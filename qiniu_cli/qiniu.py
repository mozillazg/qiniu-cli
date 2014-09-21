#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function, unicode_literals

import base64
import hashlib
import hmac
import logging
import json
import os
import time
import urllib
import urlparse

import requests

current_dir = os.path.dirname(os.path.realpath(__file__))
logger = logging.getLogger(__name__)


class QiNiu(object):
    """七牛"""
    headers = {
        'Accept': ('text/html,application/xhtml+xml,'
                   'application/xml;q=0.9,*/*;q=0.8'),
        'Accept-Encoding': 'gzip,deflate,sdch',
        'Accept-Language': 'en-US,en;q=0.5',
        'Connection': 'keep-alive',
        'DNT': 1,
        'Host': 'portal.qiniu.com',
        'Origin': 'https://portal.qiniu.com',
        'Referer': 'https://portal.qiniu.com/',
        'User-Agent': ('Mozilla/5.0 (Windows NT 6.2; rv:29.0) '
                       'Gecko/20100101 Firefox/29.0'),
    }
    cookies_json_file = os.path.join(current_dir, '.cookies.json')

    def __init__(self, username, password, accesskey=None, secretkey=None):
        self.username = username
        self.password = password
        self.request = requests.Session()
        if not os.path.exists(self.cookies_json_file):
            open(self.cookies_json_file, 'w').close()

        assert self.login(), 'Login Failed!'

        if not all([accesskey, secretkey]):
            self.get_tokens()
            self.secretkey = self.tokens['secret']
            self.accesskey = self.tokens['key']
        else:
            self.secretkey = secretkey
            self.accesskey = accesskey

    def __login(self):
        url = 'https://portal.qiniu.com/signin'
        # 先访问一次获取 cookies
        self.request.get(url=url, headers=self.headers)
        data = {
            'goto': '',
            'username': self.username,
            'password': self.password,
            'remember': 'true',
        }
        headers = self.headers.copy()
        headers.update({
            'Referer': 'https://portal.qiniu.com/signin',
        })
        response = self.request.post(url=url, data=data, headers=headers)
        # 保存 cookies
        with open(self.cookies_json_file, 'w') as f:
            f.write(json.dumps(response.cookies.get_dict(), indent=2))

        return response.ok and response.url == 'https://portal.qiniu.com/'

    def login(self):
        with open(self.cookies_json_file) as f:
            try:
                self.request.cookies.update(json.loads(f.read()))
            except ValueError as e:
                logger.exception(e)
                return self.__login()
            headers = self.headers.copy()
            headers.update({
                'Referer': 'https://portal.qiniu.com/',
                'X-Requested-With': 'XMLHttpRequest',
            })
            url = 'https://portal.qiniu.com/api/wallet/info'
            if self.request.post(url, headers=headers).status_code == 200:
                return True
            else:
                logger.debug('Relogin')
                return self.__login()

    def get_tokens(self):
        headers = self.headers.copy()
        headers.update({
            'Referer': 'https://portal.qiniu.com/setting/key',
        })
        url = 'https://portal.qiniu.com/setting/access'
        response = self.request.get(url, headers=headers)
        self.tokens = response.json()['keys'][0]
        return self.tokens


class Bucket(object):
    def __init__(self, qiniu, name, is_open=True, domain=None):
        self.qiniu = qiniu
        self.request = qiniu.request
        self.headers = qiniu.headers
        self.bucket_name = name
        if not domain:
            self.base_url = 'http://%s.qiniudn.com' % name
        else:
            self.base_url = 'http://%s' % domain
        self.is_open = is_open
        self.referer_url = ('https://portal.qiniu.com/bucket/%s/resource' % name)

    def exists(self, key):
        url = 'https://portal.qiniu.com/bucket/%s/verify' % self.bucket_name
        headers = self.headers.copy()
        headers.update({
            'X-Requested-With': 'XMLHttpRequest',
            'Referer': self.referer_url,
        })
        data = {
            'type': 'filename',
            'bucket': self.bucket_name,
            'key': key,
        }
        response = self.request.post(url, data=data, headers=headers)
        return response.json()['limit'] == 'true'

    def upload_token(self, key):
        """上传凭证"""
        encoded_put_policy = policy(self.bucket_name, key)
        # 使用 str(key) 修复如下错误:
        # TypeError: character mapping must return integer, None or unicode
        # http://stackoverflow.com/a/20862445
        sign = hmac_sha1(str(self.qiniu.secretkey), encoded_put_policy)
        encoded_sign = base64.urlsafe_b64encode(sign)
        return '%s:%s:%s' % (self.qiniu.accesskey, encoded_sign,
                             encoded_put_policy)

    def upload(self, f, key):
        """key: 文件保存位置: ab/a.txt"""
        headers = self.headers.copy()
        headers.update({
            'Access-Control-Request-Headers': 'content-type',
            'Access-Control-Request-Method': 'POST',
            'Host': 'up.qbox.me',
            'Origin': 'https://portal.qiniu.com',
            'Referer': self.referer_url,
        })
        url = 'https://up.qbox.me/'
        self.request.options(url)
        headers.pop('Access-Control-Request-Headers')
        headers.pop('Access-Control-Request-Method')
        data = {
            'token': self.upload_token(key),
            'key': key,
        }
        files = {
            'file': f,
        }
        result = self.request.post(url, data=data, files=files,
                                   headers=headers).json()
        result['url'] = self.file_url(result['key'])
        return result

    def file_url(self, key):
        url = urlparse.urljoin(self.base_url, urllib.quote(key))
        if not self.is_open:
            url, token = self.download_token(url)
            return '%s&token=%s' % (url, token)
        else:
            return url

    def download_token(self, url):
        """下载凭证"""
        deadline = int(time.time()) + 3600
        down_url = '%s?e=%s' % (url, deadline)
        sign = hmac_sha1(str(self.qiniu.secretkey), down_url)
        encoded_sign = base64.urlsafe_b64encode(sign)
        return down_url, '%s:%s' % (self.qiniu.accesskey, encoded_sign)


def hmac_sha1(key, message):
    """
    >>> from codecs import encode
    >>> encode(hmac_sha1('\x0b' * 20, 'Hi There'), 'hex')
    'b617318655057264e28bc0b6fb378c8ef146be00'
    """
    massage = hmac.new(key, message, hashlib.sha1)
    return massage.digest()


def policy(bucket_name, key):
    """上传策略"""
    if not key:
        scope = '%s' % bucket_name
    else:
        scope = '%s:%s' % (bucket_name, key)
    deadline = int(time.time()) + 3600
    return_body = """{
      "bucket": $(bucket),
      "key": $(key),
      "size": $(fsize),
      "hash": $(etag)
    }"""
    put_policy = json.dumps({
        'scope': scope,
        'deadline': deadline,
        'returnBody': return_body,
        # 'saveKey': '$(etag)',
    })
    encoded_put_policy = base64.urlsafe_b64encode(put_policy)
    return encoded_put_policy

#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function, unicode_literals
import logging
import os

import requests

from qiniu import QiNiu, Bucket

logging.basicConfig(level=logging.DEBUG)
username = ''
password = ''
bucket_name = ''
qi = QiNiu(username, password)
bucket = Bucket(qi, bucket_name)


def test_login():
    assert qi.login()


def test_bucket_exists():
    assert bucket.exists('test/a.txt')


def test_upload_token():
    token = bucket.upload_token('test/a.jpg')
    logging.debug(token)
    assert token


def test_upload():
    with open('test.txt', 'wb+') as f:
        msg = 'abcdeddfff'
        f.write(msg)
        f.seek(0)
        d = bucket.upload('abc.txt', f)
        logging.debug(d)
        assert d
        url = d['url']
        assert requests.get(url).text == msg

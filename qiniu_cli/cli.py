#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function, unicode_literals

import json
import logging
import os
from hashlib import sha1
import time

import click

from .qiniu import Bucket, QiNiu
from . import __version__


class QN(object):
    def __init__(self, f, bucket_name='default'):
        self.config = self.parse_config(f)
        self.qiniu = QiNiu(**self.config['user'])
        self.bucket_conf = self.config['bucket'][bucket_name]
        self.bucket = Bucket(self.qiniu, name=self.bucket_conf['name'],
                             is_open=self.bucket_conf['is_open'],
                             domain=self.bucket_conf['domain'])

    def parse_config(self, f):
        return json.loads(f.read())
pass_qiniu = click.make_pass_decorator(QN)


@click.group()
@click.option('-c', '--config', required=False, default='config.json',
              type=click.File('rb'), help='Config file(default: config.json).')
@click.option('--bucket', help='Bucket name.', required=False, default='default')
@click.option('-v', '--verbose', is_flag=True,
              help='Enables verbose mode.')
@click.version_option(__version__)
@click.pass_context
def main(ctx, config=None, bucket=None, verbose=False):
    if verbose:
        logging.basicConfig(level=logging.DEBUG)
    ctx.obj = QN(config, bucket)


@main.command(short_help='Upload file.')
@click.option('--save-name', required=False, help='File save name.')
@click.option('--save-dir', default='', required=False,
              help='Upload to directory.')
@click.option('--auto-name', is_flag=True,
              help='Auto name file by sh1 hex digest with timestamp.')
@click.argument('f', type=click.File('rb'))
@pass_qiniu
def upload(qn, f, save_dir, save_name, auto_name):
    if not save_name and (auto_name or qn.bucket_conf['auto_name']):
        save_name = '%s%s' % (sha1(str(time.time())).hexdigest(),
                              os.path.splitext(f.name)[-1])
    else:
        raise click.UsageError('Please set filename with --save-name, '
                               'or use --auto-name auto name file')

    to = os.path.join(save_dir, save_name)
    if not qn.config['upload']['overwrite'] and qn.bucket.exists(to):
        print(qn.bucket.file_url(to))
    else:
        print(qn.bucket.upload(f, to)['url'])


@main.command(short_help='Search file.')
@pass_qiniu
def search(qn):
    pass


if __name__ == '__main__':
    main()

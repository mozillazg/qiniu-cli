qiniu-cli
=========

Qiniu CLI tool.


Install
-----------

::

    pip install qiniu-cli


Usage
--------

::

    $ qiniu_cli upload requirements.txt
    http://tmp-images.qiniudn.com/requirements.txt

    $ qiniu_cli upload --save-dir "comics/2014/" *.png *.txt
    http://tmp-images.qiniudn.com/comics/2014/2014-09-25-EveryFall.zh-cn.png
    http://tmp-images.qiniudn.com/comics/2014/3014.painting.png
    http://tmp-images.qiniudn.com/comics/2014/requirements.txt


    $ qiniu_cli --help
    Usage: qiniu_cli [OPTIONS] COMMAND [ARGS]...

    Options:
      -c, --config FILENAME  Config file(default: config.json).
      --bucket TEXT          Bucket name.
      -v, --verbose          Enables verbose mode.
      --version              Show the version and exit.
      --help                 Show this message and exit.

    Commands:
      search  Search file.
      upload  Upload file.

    $ qiniu_cli upload --help
    Usage: qiniu_cli upload [OPTIONS] FILES...

    Options:
      --save-name TEXT  File save name.
      --save-dir TEXT   Upload to directory.
      --auto-name       Auto name file by sh1 hex digest with timestamp.
      --help            Show this message and exit.

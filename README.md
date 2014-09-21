qiniu-cli
=========

Qiniu CLI tool

```
$ python -m qiniu_cli.cli upload requirements.txt
http://tmp-images.qiniudn.com/requirements.txt


$ python -m qiniu_cli.cli --help
Usage: cli.py [OPTIONS] COMMAND [ARGS]...

Options:
  -c, --config FILENAME  Config file(default: config.json).
  --bucket TEXT          Bucket name.
  -v, --verbose          Enables verbose mode.
  --version              Show the version and exit.
  --help                 Show this message and exit.

Commands:
  search  Search file.
  upload  Upload file.

$ python -m qiniu_cli.cli upload --help
Usage: cli.py upload [OPTIONS] F

Options:
  --save-name TEXT  File save name.
  --save-dir TEXT   Upload to directory.
  --auto-name       Auto name file by sh1 hex digest with timestamp.
  --help            Show this message and exit.

```

Sync to Dropbox of local directory
Uses Dropbox API V2 and python3

Original script taken from:
https://github.com/dropbox/dropbox-sdk-python/blob/master/example/updown.py


To start working:
1. install python. E.g. using Chocolatey `choco install -y python`
1. install python dropbox dependency module `pip3 install dropbox`
1. Create your app in dropbox. Read more https://docs.gravityforms.com/creating-a-custom-dropbox-app/
1. Open created app https://www.dropbox.com/developers/apps
1. Scroll down to ‘OAuth 2’ block and hit `Generate` button near ‘Generated access token’ text
1. After the token is generated you’ll see a string of letters and numbers
1. Copy `dbox_sync.py` to your local disk
1. create `config.ini` file. Example config.ini:
```
[DBOX_SYNC]
DROPBOX_TOKEN = token_recieved_on_dropbox_com
LOCAL_DIR = ./db/scans
DBOX_DIR = /remote/path/scans
CLEAN_OLD = False
DRY_RUN = False
ACTION = sync [available actions: download|upload|sync]
```
1. run `python d:\path\dbox_sync.py -c d:\path\config.ini`

As a known issue client does not work properly with file modified dates so for now file differences in date/time are ignored during file comparison.
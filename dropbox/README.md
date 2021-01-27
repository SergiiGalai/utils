Sync local directory to Dropbox

Based on Python3 and Dropbox API V2

Original free Dropbox client is limited to run on 3 environments max. I have a phone, old linux PC, old laptop and another laptop. I don't need to keep synced all dropbox files everywhere. Usually I need keep synced several documents which are located in one folder.
Unfortunately Dropbox client does not allow this case. This is why the idea to write a script to compare and sync folder was born.

The base script was taken from the Dropdox SDK sample:
https://github.com/dropbox/dropbox-sdk-python/blob/master/example/updown.py

What it can:
- synchronize files in your local folder and folder on dropbox account per script run
- track files inside the directory
- track subfolders and their content inside the directory
- compare files base on metadata or on file content
- ask you which new or modified files to upload and which to download
- open source command line tool so your files belong to you (and Dropbox :) )
- no need to install (except python runtime and dependency module)

What it cannot:
- cannot live in memory (not a realtime client)
- cannot track your file changes in realtime
- cannot track your dropbox changes in realtime
- cannot handle file *removals*. You need to check that manually. So if you have removed file on dropbox but preserved in local folder this tool will propose to upload file again (and vise versa).

To start working:
1. You have to have a Dropbox account
1. Copy `dropbox_client.py` to your local disk
1. Create `config.ini` or other file. Check its content below.
1. Install python3. 
1.1. For windows E.g. using Chocolatey `choco install -y python`
1.1. For Ubunut `sudo apt install python-is-python3 python3-pip`   
1. Install python dropbox dependency module `pip3 install dropbox`
1. Create app on dropbox website. Read more https://docs.gravityforms.com/creating-a-custom-dropbox-app/
1. Open created app https://www.dropbox.com/developers/apps
1. Scroll down to ‘OAuth 2’ block and hit `Generate` button near `Generated access token` text
1. After the token is generated copy it to `DROPBOX_TOKEN` field in `config.ini`
1. run `python d:\path\dropbox_client.py`. If your config has other name then `python d:\path\dropbox_client.py -c d:\path\to\config\other_name.ini`

`config.ini` content:
```
[DBOX_SYNC]
DROPBOX_TOKEN = [token_recieved_on_dropbox_com]
LOCAL_DIR = [path to database root folder (absolute or relative)]
DBOX_DIR = [path to folder on dropbox]
DRY_RUN = [False|True]
SUBFOLDERS = [if true process also subfolders. Allowed values: False|True]
ACTION = [sync|download|upload]
```

Config file Example:
```
[DBOX_SYNC]
DROPBOX_TOKEN = 1234567890
LOCAL_DIR = ./db
DBOX_DIR = /documents
DRY_RUN = False
SUBFOLDERS = True
ACTION = sync
```

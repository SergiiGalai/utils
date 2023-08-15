Sync local directory to Google Drive

Problem
Normally we install the Google Drive client on our system which takes care of all the syncing. So you can keep editing your files locally inside the Google Drive Folder without worrying about them getting synced with your google account because the client will take care of it. However, due to certain restrictions on my system the Google Drive client cannot be installed. 

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
1. Copy `cloud_sync_client.py` to your local disk
1. Create `config.ini` or other file. Check its content below.
1. Install python3. E.g. using Chocolatey `choco install -y python`
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

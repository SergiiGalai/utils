Sync local directory to Google Drive or Dropbox

## Problem
Normally we install the Google Drive client on our system which takes care of all the syncing. So you can keep editing your files locally inside the Google Drive Folder without worrying about them getting synced with your google account because the client will take care of it. However, due to certain restrictions on my system the Google Drive client cannot be installed. 

### What it can do:
- synchronize files in your local folder and folder on dropbox account per script run
- track files inside the directory
- track subfolders and their content inside the directory
- compare files base on metadata or on file content
- ask you which new or modified files to upload and which to download
- open source command line tool so your files belong to you
- no need to install (except python runtime and dependency module)

### What it cannot do:
- cannot live in memory (not a realtime client)
- cannot track your file changes in realtime
- cannot track your dropbox changes in realtime
- cannot handle file *removals*. You need to check that manually. So if you have removed file on dropbox but preserved in local folder this tool will propose to upload file again (and vise versa).

## Start working
1. Copy the content of this folder to your local disk
1. Create `config.ini` or other file. Check its content below.
1. Install python3. E.g. using Chocolatey `choco install -y python`
1. Run unit tests `python -m unittest`

### Google Drive
1. You have to have a Dropbox account
1. Install python dropbox dependency module `pip install pydrive`
1. Perform [Authentication steps](https://pythonhosted.org/PyDrive/quickstart.html#authentication)	allowing to access google drive in the scopes
1. run `python d:\path\cloud_sync\main.py`

### Dropbox
1. You have to have a Dropbox account
1. Install python dropbox dependency module `pip3 install dropbox`
1. Create the app on the [Dropbox website](https://docs.gravityforms.com/creating-a-custom-dropbox-app/).
1. Open [created Dropbox app](https://www.dropbox.com/developers/apps)
1. Scroll down to ‘OAuth 2’ block and hit `Generate` button near `Generated access token` text
1. After the token is generated copy it to `TOKEN` field in `config.ini`
1. run `python d:\path\cloud_sync\main.py`

### Examples
`python d:\path\cloud_sync\main.py -h` - get help
`python d:\path\cloud_sync\main.py`
`python d:\path\cloud_sync\main.py -c d:\path\to\config\other_name.ini`

### Config file

`config.ini` content:
```
STORAGE = [DROPBOX|GDRIVE]

[GDRIVE]
ACTION = [sync|download|upload]
LOCAL_DIR = [path to database root folder (absolute or relative)]
CLOUD_DIR = [path to folder on Goodle Drive]
RECURSIVE = [False|True - process subfolders if true]
DRY_RUN = [False|True]

[DROPBOX]
ACTION = [sync|download|upload]
TOKEN = [token_recieved_on_dropbox_com. see https://www.dropbox.com/developers/apps]
LOCAL_DIR = [path to database root folder (absolute or relative)]
CLOUD_DIR = [path to folder on Dropbox]
RECURSIVE = [False|True - process subfolders if true]
DRY_RUN = [False|True]
```

## Development
[Code Style Guide](https://peps.python.org/pep-0008/)
install VS Code extension for code formatting `autopep8`` 

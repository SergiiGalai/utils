dropbox_api.ps1 contains list of functions to work with your dropbox account.
To start working:
1. Create your app in dropbox. Read more https://docs.gravityforms.com/creating-a-custom-dropbox-app/
2. Open created app https://www.dropbox.com/developers/apps
3. Scroll down to ‘OAuth 2’ block and hit ‘Generate’ button near ‘Generated access token’ text
4. After the token is generated you’ll see a string of letters and numbers
5. Copy 'dropbox_api.ps1' to your local disk
6. create token.txt file near 'dropbox_api.ps1' and fill it the access token generated on step 4
7. create folder 'Files' in current directory which will be used as base directory to download/upload files
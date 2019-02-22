story_tagger

A script to tag stories in Pivotal Tracker with sequential user-friendly short IDs (like in Jira).

Run similar to 
`.\story_tagger.ps1 -projectId 123 -apiToken "123" -storyPrefix "PRG-" -action add`
* `-projectId` - Pivotal Tracker project id you can find by loggin in browser and opening project. Find it in the url
* `-apiToken` - Pivotal Tracker token. You can find or generate it in your Pivotal Tracker profile
* `-storyPrefix` - prefix to be added to story name in square brackets. 
* `-action` - action to do with stories

E.g. in the current example for name 'story description' result will be '[PRG-1] story description'

Possible `-action` parameter values:
* `get` - show the list of user stories
* `add` - add prefix id to applicable user stories
* `delete` - delete prefix id from applicable user stories

    

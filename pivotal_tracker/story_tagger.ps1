[CmdLetBinding()]
param(
	[Parameter(Mandatory=$true)]
	[string] $projectId,
	[Parameter(Mandatory=$true)]
	[string] $apiToken,
	[Parameter(Mandatory=$true)]
	[string] $storyPrefix,
	[Parameter(Mandatory=$true)]
	[string] $action
)
$projectUrl = "https://www.pivotaltracker.com/services/v5/projects/$projectId"
$storyPrefixPattern = "\[$storyPrefix(\d+)\]"

function getStories {
	[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12
	return Invoke-RestMethod -Uri $projectUrl/stories -Headers $headers | Sort-Object -Property id, created_at
}

function setStoryName([string] $id, [string] $name){
	$data = @{ name = $name }
	$body = $data | ConvertTo-Json;

	write-host "setStoryName $name $id"
	[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12
	$updateResponse = Invoke-RestMethod -Uri $projectUrl/stories/$id -Body $body -Method PUT -Headers $headers -ContentType "application/json"
}

function setStoryNames([UpdateStoryName[]] $updateStoryNames){
	write-host "setStoryNames"
	foreach ($updateStory in $updateStoryNames) {
		setStoryName $updateStory.PivotalId $updateStory.Name
	}
}

function getMaxFoundStoryId($stories){
	$maxFoundStoryId = 0

	write-host "getMaxFoundStoryId"

	foreach ($story in $stories) {
		$match = [regex]::Match($story.name, $storyPrefixPattern)
		if ( $match.Success ){
			$foundId = [int]$match.Groups[1].Value
			$maxFoundStoryId = [math]::max($maxFoundStoryId, $foundId)
		}
	}

	return $maxFoundStoryId
}

class UpdateStoryName {
	[int]$Id;
	[string]$Name;
	[string]$PivotalId;
}

function getStoriesToAddPrefixes($stories, $nextId){
	write-host "Looking for stories to ADD prefixes ( nextId=$nextId )"

	$result = @()
	foreach ($story in $stories) {
		$match = [regex]::Match($story.name, "$storyPrefixPattern (.*)" )

		if ( -Not $match.Success ){
			$nextId += 1

			$item = [UpdateStoryName]::new()
			$item.PivotalId = $story.id
			$item.Id = $nextId
			$item.Name = "[$storyPrefix$nextId] $($story.name)"
			$result += $item
		}
	}

	return $result
}

function getStoriesToRemovePrefixes($stories){
	write-host "Looking for stories to REMOVE prefixes"

	$result = @()
	foreach ($story in $stories) {
		$match = [regex]::Match($story.name, "$storyPrefixPattern (.*)" )

		if ( $match.Success ){
			$item = [UpdateStoryName]::new()
			$item.PivotalId = $story.id
			$item.Id = [int]$match.Groups[1].Value
			$item.Name = $match.Groups[2].Value
			$result += $item
		}
	}

	return $result
}

function showItems($items){
	write-host "Found $($items.length) applicable stories:"
	$items | Format-Table | Out-String
}

function Confirm {
	$confirmation = Read-Host "Are you Sure You Want To Proceed [y/n] ?"
	if ($confirmation -eq 'y') {
		return $TRUE
	}
	return $FALSE
}

function processFilteredStories([UpdateStoryName[]]$updateStories){
	showItems $updateStories
	if (Confirm $updateStories){
		setStoryNames $updateStories
	}
}

$headers = New-Object "System.Collections.Generic.Dictionary[[String],[String]]"
$headers.Add("X-TrackerToken", $apiToken)

$stories = getStories

if ($action -eq "delete"){
	$updateStories = getStoriesToRemovePrefixes $stories
	processFilteredStories $updateStories
}elseif ($action -eq "add"){
	$maxFoundId = getMaxFoundStoryId $stories
	$updateStories = getStoriesToAddPrefixes $stories $maxFoundId
	processFilteredStories $updateStories
}else{
	showItems $stories
}
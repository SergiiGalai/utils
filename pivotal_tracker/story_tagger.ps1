[CmdLetBinding()]
param(
    [Parameter(Mandatory=$true)]
    [string] $projectId,
    [Parameter(Mandatory=$true)]
    [string] $apiToken,
	[Parameter(Mandatory=$true)]
	[string] $storyPrefix,
	[Parameter(Mandatory=$false)]
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

	[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12
	$updateResponse = Invoke-RestMethod -Uri $projectUrl/stories/$id -Body $body -Method PUT -Headers $headers -ContentType "application/json"
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

class UpdateStoryResult {
	[bool]$Match;
	[int]$Id;
	[string]$Name;
	[string]$PivotalId;
}

function setStoryPrefixes($stories, $maxSeenStoryId){
	$newlyTaggedStoryCount = 0	

	write-host "setStoryPrefixes maxSeenStoryId $maxSeenStoryId"

	foreach ($story in $stories) {
		$item = [UpdateStoryResult]::new()
		$item.PivotalId = $story.id

		$match = [regex]::Match($story.name, "$storyPrefixPattern (.*)" )		
		$item.Match = $match.Success

		if ($match.Success ){
			$item.Id = [int]$match.Groups[1].Value			
			$item.Name = $story.name
		}else{
			$newlyTaggedStoryCount += 1
			$maxSeenStoryId += 1

			$item.Id = $maxSeenStoryId
			$item.Name = "[$storyPrefix$maxSeenStoryId] $($story.name)"
			setStoryName $item.PivotalId $item.Name
		}
		$item
	}

	write-host "Tagged $newlyTaggedStoryCount new stories out of $($stories.Length) total"
}

function removeStoryPrefixes($stories){
	write-host "removeStoryPrefixes"

	foreach ($story in $stories) {
		$item = [UpdateStoryResult]::new()
		$item.PivotalId = $story.id

		$match = [regex]::Match($story.name, "$storyPrefixPattern (.*)" )
		$item.Match = $match.Success

		if ( $match.Success ){
			$item.Id = [int]$match.Groups[1].Value
			$item.Name = $match.Groups[2].Value

			setStoryName $item.PivotalId $item.Name
		}else{
			$item.Id = -1
			$item.Name = $story.name
		}
		$item
	}
}

$headers = New-Object "System.Collections.Generic.Dictionary[[String],[String]]"
$headers.Add("X-TrackerToken", $apiToken)

$stories = getStories

if ($action -eq "delete"){
	removeStoryPrefixes $stories
}elseif ($action -eq "update"){
	$maxFoundId = getMaxFoundStoryId $stories
	setStoryPrefixes $stories $maxFoundId
}else{
	$stories
}
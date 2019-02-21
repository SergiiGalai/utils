[CmdLetBinding()]
param(
    [Parameter(Mandatory=$true)]
    [string] $projectId,
    [Parameter(Mandatory=$true)]
    [string] $apiToken,
	[Parameter(Mandatory=$true)]
	[string] $storyPrefix
)

$projectUrl = "https://www.pivotaltracker.com/services/v5/projects/$projectId"

function getStories {
	[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12
	return Invoke-RestMethod -Uri $projectUrl/stories -Headers $headers | Sort-Object -Property id, created_at
}

function setStoryName([string] $id, [string] $name){
	$data = @{ name = $name }
	$body = $data | ConvertTo-Json;

	write-host "setStoryName $id $name"
	
	[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12
	$updateResponse = Invoke-RestMethod -Uri $projectUrl/stories/$id -Body $body -Method PUT -Headers $headers -ContentType "application/json"
}

class UpdateStoryResult {
	[bool]$Match;
	[string]$Name;
	[string]$Id;
	[string]$PivotalId;
}

function setStoryPrefixes($stories){
	$newlyTaggedStoryCount = 0
	$maxSeenStoryId = 0

	write-host "setStoryPrefixes"
	
	foreach ($story in $stories) {
		$item = [UpdateStoryResult]::new()
		$item.PivotalId = $story.id

		$match = [regex]::Match($story.name, "\[$storyPrefix(\d+)\]" )
		$item.Match = $match.Success

		if ( $match.Success ){
			$item.Id = $match.Groups[1].Value
			$item.Name = $story.name
			
			$maxSeenStoryId = if ($maxSeenStoryId -lt $item.Id) {$item.Id} else {$maxSeenStoryId}			
		}else{
			$newlyTaggedStoryCount += 1
			$maxSeenStoryId += 1

			$item.Id = $maxSeenStoryId
			$item.Name = "[$storyPrefix$maxSeenStoryId] - $($story.name)"

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

		$match = [regex]::Match($story.name, "\[$storyPrefix(\d+)\] - (.*)" )
		$item.Match = $match.Success

		if ( $match.Success ){
			$item.Id = $match.Groups[1].Value
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
removeStoryPrefixes $stories
#setStoryPrefixes $stories
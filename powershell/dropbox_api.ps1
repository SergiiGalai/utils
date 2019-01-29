Param(	
	[string]$list,
	[string]$upload,
	[string]$download,
	[string]$to,
	[switch]$debug
)

$localPathBase = "d:\Dropbox"

function show_exception
{
	Param ($exception)
	
	$exception.Response
	$exception.InnerException
	
	$streamReader = [System.IO.StreamReader]::new($exception.Response.GetResponseStream())
	$errResp = $streamReader.ReadToEnd()
	write-host "error: $errResp"
	$streamReader.Close()
}

function list_folder
{
	Param ($path)
	write-host "== list_folder $path"
	
	$url = "https://api.dropboxapi.com/2/files/list_folder"	
	$body = "{`"path`":`"$path`"}"
	$headers = @{
		"Authorization"="Bearer $token";
		"Content-Type"="text/plain; charset=dropbox-cors-hack"
	}
	
	try{
		$response = Invoke-RestMethod -Uri $url -Method Post -Headers $headers -Body $body
		$response.entries | Select path_display, size, client_modified | Format-Table
		
	} catch {
		show_exception $_.Exception	
	}
}    

function download_file
{
	Param ($httpPath, $savePath)
	write-host "== download_file $httpPath => $savePath"
	
	$url = "https://content.dropboxapi.com/2/files/download"
	$headers = @{
		"Authorization"="Bearer $token";
		"Content-Type"="application/octet-stream";
		"Dropbox-API-Arg"="{`"path`":`"$httpPath`"}"		
	}	
		
	try{ 
		Invoke-RestMethod -Uri $url -Method Post -Headers $headers -OutFile $savePath
		return $True
	} catch {
		show_exception $_.Exception
		return $False
	}
}

function upload_file
{
	Param ($sourceFilePath, $httpPath)
	write-host "== upload_file $sourceFilePath => $httpPath"

	$url = "https://content.dropboxapi.com/2/files/upload"
	$headers = @{
		"Authorization"="Bearer $token";		
		"Content-Type"="application/octet-stream";
		"Dropbox-API-Arg"="{`"path`":`"$httpPath`",`"mode`":{`".tag`":`"overwrite`"}}"
	}
		
	try{ 
		Invoke-RestMethod -Uri $url -Method Post -Headers $headers -InFile $sourceFilePath
		return $True
	} catch {
		show_exception $_.Exception
		return $False
	}
}

function test_path
{
	Param ($path)
	
	if(-Not ($path | Test-Path) ){
		throw "File or folder does not exist"
	}
}
function test_file_path
{
	Param ($path)
	
	if(-Not ($path | Test-Path -PathType Leaf) ){
		throw "The Path argument must be a file. Folder paths are not allowed."
	}	
}
function read_token
{
	write-host "== read_token .\token.txt"
	return Get-Content -Path .\token.txt
}

$token=read_token
if($debug)
{
	write-host "Passed params:"
	write-host "list = $list"
	write-host "download = $download"
	write-host "upload = $upload"
	write-host "to = $to"
}
elseif ($list)
{
	if ($list -eq "/") {$list = ""}
	list_folder $list
}
elseif ($download -and $to)
{
	$fileName = Split-Path $download -leaf	
	$localPathToDownload = "$localPathBase$to"
	test_path $localPathToDownload
	
	$downloadResult = download_file $download "$localPathToDownload\$fileName"
	if ($downloadResult -eq $True)
	{
		ii $localPathToDownload
	}	
}
elseif ($upload -and $to)
{
	$localPathToUpload = "$localPathBase$upload"
	test_file_path $localPathToUpload
	$fileName = Split-Path $localPathToUpload -leaf	
	
	$uploadResult = upload_file $localPathToUpload "$to/$fileName"
	if ($uploadResult -eq $True)
	{
		list_folder $to
	}
}
else
{
	write-host "Dropbox folder is $localPathBase"
	write-host "allowed commands:"
	write-host ""
	write-host "-list /remote/folder"
	write-host "-download /remote/file/path/with_file.name \local\relative\folder"
	write-host "-upload \local\relative\path\with_file.name /remote/folder"	
}
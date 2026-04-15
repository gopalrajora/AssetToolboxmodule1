if (!([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)) {
    Start-Process PowerShell -Verb RunAs "-NoProfile -ExecutionPolicy Bypass -Command `"cd '$pwd'; & '$PSCommandPath';`"";
    exit;
}



$ProgressPreference = 'SilentlyContinue'
$main_page = "https://upcomillas-my.sharepoint.com/:u:/g/personal/pcalvo_comillas_edu/EbwQGVnUkOZHjFAFgqWVxzABr9-qPAuxmulpWMZmXwDwjQ?e=5jcEed"
$file_page = "https://upcomillas-my.sharepoint.com/personal/pcalvo_comillas_edu/_layouts/15/download.aspx?SourceUrl=%2Fpersonal%2Fpcalvo%5Fcomillas%5Fedu%2FDocuments%2FATTEST%2FATTEST%5Fenv%2E7z"
$sourcefile = "ATTEST_env.7z"
Write-Output "Connecting..."
$a = Invoke-WebRequest $main_page -SessionVariable MyWebSession
Write-Output "DOWNLOADING. PLEASE WAIT..."
Invoke-WebRequest $file_page -OutFile $sourcefile -WebSession $MyWebSession
Write-Output "Download finished"
if (Test-Path -Path Software\ATTEST_env){
	Write-Output "Removing old files"
	Remove-Item -Path Software\ATTEST_env -Force -Recurse -ErrorAction SilentlyContinue -Confirm:$false
}
Write-Output "Decompressing files"

if (Get-Module -ListAvailable -Name 7Zip4PowerShell) {
	Expand-7Zip -ArchiveFileName $sourcefile -TargetPath "Software\"
} else {
	Write-Output "Installing 7zip Module"
	[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12
	Install-PackageProvider -Name NuGet -MinimumVersion 2.8.5.201 -Force
	Set-PSRepository -Name 'PSGallery' -SourceLocation "https://www.powershellgallery.com/api/v2" -InstallationPolicy Trusted
	Install-Module -Name 7Zip4PowerShell
	Expand-7Zip -ArchiveFileName $sourcefile -TargetPath "Software\"
}

Write-Output "Removing old files"
Remove-Item -Path $sourcefile -Force -ErrorAction SilentlyContinue -Confirm:$false
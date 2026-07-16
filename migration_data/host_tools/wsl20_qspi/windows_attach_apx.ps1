param(
    [string]$BusId,
    [switch]$AutoAttach
)

$ErrorActionPreference = 'Stop'
$Distro = 'Ubuntu-20.04-Jetson'

if (-not $BusId) {
    $matches = @(usbipd list | Select-String -Pattern '^\s*([0-9]+-[0-9]+)\s+0955:7e19\s+')
    if ($matches.Count -eq 0) {
        throw 'No connected Xavier NX APX device (0955:7e19). Enter Force Recovery and retry.'
    }
    if ($matches.Count -gt 1) {
        usbipd list
        throw 'Multiple APX devices found. Run again with -BusId <BUSID>.'
    }
    $BusId = $matches[0].Matches[0].Groups[1].Value
}

Write-Host "Binding APX BUSID $BusId"
usbipd bind --busid $BusId

$arguments = @('attach', '--wsl', $Distro, '--busid', $BusId)
if ($AutoAttach) {
    $arguments += '--auto-attach'
}
Write-Host "Attaching BUSID $BusId to $Distro"
& usbipd @arguments

wsl.exe -d $Distro -- lsusb -d 0955:7e19
if ($LASTEXITCODE -ne 0) {
    throw 'APX was not visible inside Ubuntu-20.04-Jetson.'
}
Write-Host 'WSL_APX_ATTACH=PASS'

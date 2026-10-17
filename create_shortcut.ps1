# Создаёт ярлык «Keeeensy Launcher» с иконкой лаунчера.
# По умолчанию на рабочем столе; другое место: .\create_shortcut.ps1 -Destination <папка>
param(
    [string]$Destination = [Environment]::GetFolderPath("Desktop")
)

$root = $PSScriptRoot
$link = Join-Path $Destination "Keeeensy Launcher.lnk"

$shell = New-Object -ComObject WScript.Shell
$shortcut = $shell.CreateShortcut($link)
$shortcut.TargetPath = Join-Path $root "launcher.bat"
$shortcut.WorkingDirectory = $root
$shortcut.IconLocation = (Join-Path $root "assets\launcher\icon.ico") + ",0"
$shortcut.Description = "Keeeensy Launcher — игры и профили Minecraft"
$shortcut.WindowStyle = 7   # консоль launcher.bat сразу свёрнута и не мелькает
$shortcut.Save()

Write-Host "Ярлык создан: $link"

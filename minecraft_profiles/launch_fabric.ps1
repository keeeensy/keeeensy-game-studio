param(
    [ValidateSet("vanilla", "rpg_levels", "death_marker", "all_mods")]
    [string]$Profile = "all_mods"
)

$ErrorActionPreference = "Stop"

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$workDir = Split-Path -Parent $scriptDir
$mcDir = "$env:APPDATA\.minecraft"
$javaHome = "C:\Users\keeeensy\AppData\Local\Programs\Microsoft\jdk-25.0.3.9-hotspot"
$javaExe = "$javaHome\bin\javaw.exe"
$libDir = "$mcDir\libraries"
$versionsDir = "$mcDir\versions"
$modsDir = "$mcDir\mods"
$assetsDir = "$mcDir\assets"
$nativesDir = "$mcDir\natives_tmp"
$objectsDir = "$libDir\v1\objects"
$sharedDir = Join-Path $scriptDir "shared"
$profileModsDir = Join-Path $scriptDir "profiles\$Profile\mods"
$backupDir = "$mcDir\mods_backup_launcher"

function Resolve-LibPath($name) {
    $parts = $name.Split(':')
    $group = $parts[0]; $artifact = $parts[1]; $version = $parts[2]
    $classifier = if ($parts.Length -gt 3) { "-$($parts[3])" } else { "" }
    $jarName = "$artifact-$version$classifier.jar"
    $path = $group.Replace('.', [IO.Path]::DirectorySeparatorChar)
    return "$libDir\$path\$artifact\$version\$jarName"
}

function Get-ClientJar {
    $vanillaJson = Get-Content "$versionsDir\26.1.2\26.1.2.json" -Raw | ConvertFrom-Json
    $sha1 = $vanillaJson.downloads.client.sha1
    $jar = "$objectsDir\$sha1\client.jar"
    if (!(Test-Path $jar)) { throw "Client jar not found: $jar" }
    return $jar
}

function Get-Libraries($jsonPath) {
    $json = Get-Content $jsonPath -Raw | ConvertFrom-Json
    $libs = @()
    foreach ($lib in $json.libraries) {
        $name = $lib.name
        if ($name -match "natives-") { continue }

        $allow = $false
        if ($lib.rules) {
            foreach ($rule in $lib.rules) {
                $osName = $null
                if ($rule.os -and $rule.os.name) { $osName = $rule.os.name }
                if ($null -eq $osName) {
                    $allow = ($rule.action -eq "allow")
                } elseif ($osName -eq "windows") {
                    $allow = ($rule.action -eq "allow")
                }
            }
        } else {
            $allow = $true
        }
        if (!$allow) { continue }

        if ($lib.artifact -and $lib.artifact.path) {
            $path = "$libDir\$($lib.artifact.path)"
        } else {
            $path = Resolve-LibPath $name
        }
        if (Test-Path $path) { $libs += $path }
    }
    return $libs
}

function Ensure-FabricApi {
    New-Item $sharedDir -ItemType Directory -Force | Out-Null
    $apiJar = Join-Path $sharedDir "fabric-api-0.149.1+26.1.2.jar"
    if (Test-Path $apiJar) { return $apiJar }

    $installed = Join-Path $modsDir "fabric-api-0.149.1+26.1.2.jar"
    if (Test-Path $installed) {
        Copy-Item $installed $apiJar -Force
        return $apiJar
    }

    Write-Host "Downloading Fabric API..." -ForegroundColor Yellow
    $url = "https://maven.fabricmc.net/net/fabricmc/fabric-api/fabric-api/0.149.1+26.1.2/fabric-api-0.149.1+26.1.2.jar"
    Invoke-WebRequest -Uri $url -OutFile $apiJar -UseBasicParsing
    return $apiJar
}

function Sync-ProfileMods {
    if ($Profile -eq "vanilla") {
        New-Item (Join-Path $scriptDir "profiles\vanilla\mods") -ItemType Directory -Force | Out-Null
        return
    }

    $rpgJar = Join-Path $workDir "rpg_levels_mod\build\libs\rpg-levels-1.0.0.jar"
    $deathJar = Join-Path $workDir "death_marker_mod\build\libs\death-marker-1.0.0.jar"
    $fabricApi = Ensure-FabricApi

    foreach ($dir in @("rpg_levels", "death_marker", "all_mods")) {
        $target = Join-Path $scriptDir "profiles\$dir\mods"
        New-Item $target -ItemType Directory -Force | Out-Null
        Get-ChildItem $target -Filter "*.jar" -ErrorAction SilentlyContinue | Remove-Item -Force
    }

    if (Test-Path $fabricApi) {
        Copy-Item $fabricApi (Join-Path $scriptDir "profiles\rpg_levels\mods\fabric-api-0.149.1+26.1.2.jar") -Force
        Copy-Item $fabricApi (Join-Path $scriptDir "profiles\death_marker\mods\fabric-api-0.149.1+26.1.2.jar") -Force
        Copy-Item $fabricApi (Join-Path $scriptDir "profiles\all_mods\mods\fabric-api-0.149.1+26.1.2.jar") -Force
    }

    if (Test-Path $rpgJar) {
        Copy-Item $rpgJar (Join-Path $scriptDir "profiles\rpg_levels\mods\rpg-levels-1.0.0.jar") -Force
        Copy-Item $rpgJar (Join-Path $scriptDir "profiles\all_mods\mods\rpg-levels-1.0.0.jar") -Force
    } else {
        Write-Host "WARNING: missing $rpgJar - run gradlew build in rpg_levels_mod" -ForegroundColor Yellow
    }

    if (Test-Path $deathJar) {
        Copy-Item $deathJar (Join-Path $scriptDir "profiles\death_marker\mods\death-marker-1.0.0.jar") -Force
        Copy-Item $deathJar (Join-Path $scriptDir "profiles\all_mods\mods\death-marker-1.0.0.jar") -Force
    } else {
        Write-Host "WARNING: missing $deathJar - run gradlew build in death_marker_mod" -ForegroundColor Yellow
    }
}

function Deploy-Mods {
    if (Test-Path $backupDir) { Remove-Item $backupDir -Recurse -Force }
    if (Test-Path $modsDir) {
        Move-Item $modsDir $backupDir
    }
    New-Item $modsDir -ItemType Directory -Force | Out-Null

    if ($Profile -eq "vanilla") { return }

    if (!(Test-Path $profileModsDir)) {
        throw "Profile folder not found: $profileModsDir"
    }

    $jars = @(Get-ChildItem "$profileModsDir\*.jar" -ErrorAction SilentlyContinue)
    if ($jars.Count -eq 0) {
        throw "No jar files in profile [$Profile]. Build mods first: gradlew build"
    }

    foreach ($jar in $jars) {
        Copy-Item $jar.FullName (Join-Path $modsDir $jar.Name) -Force
    }
}

function Restore-Mods {
    if (Test-Path $modsDir) { Remove-Item $modsDir -Recurse -Force }
    if (Test-Path $backupDir) {
        Move-Item $backupDir $modsDir
    }
}

function Get-ModJars {
    if (!(Test-Path $modsDir)) { return @() }
    return @(Get-ChildItem "$modsDir\*.jar" | Select-Object -ExpandProperty FullName)
}

function Extract-Natives {
    if (Test-Path $nativesDir) { Remove-Item $nativesDir -Recurse -Force }
    New-Item $nativesDir -ItemType Directory -Force | Out-Null

    Add-Type -AssemblyName System.IO.Compression.FileSystem
    $vanillaJson = Get-Content "$versionsDir\26.1.2\26.1.2.json" -Raw | ConvertFrom-Json

    foreach ($lib in $vanillaJson.libraries) {
        $name = $lib.name
        if ($name -notmatch ':natives-windows$') { continue }
        $jarPath = Resolve-LibPath $name
        if (!(Test-Path $jarPath)) { continue }
        try {
            $archive = [System.IO.Compression.ZipFile]::OpenRead($jarPath)
            foreach ($entry in $archive.Entries) {
                if ($entry.Name -match "\.(dll|so|dylib)$") {
                    $target = "$nativesDir\$($entry.Name)"
                    try { [System.IO.Compression.ZipFileExtensions]::ExtractToFile($entry, $target, $true) } catch {}
                }
            }
            $archive.Dispose()
        } catch {}
    }
}

function Escape-Resp($s) {
    if ($s -match '[\s"]') { return '"' + $s.Replace('"', '""') + '"' }
    return $s
}

$profileNames = @{
    vanilla       = "Vanilla (Fabric, no mods)"
    rpg_levels    = "RPG Levels Mod"
    death_marker  = "Death Marker Mod"
    all_mods      = "RPG Levels + Death Marker"
}

Write-Host "=== Minecraft Fabric Launcher ===" -ForegroundColor Cyan
Write-Host "Profile: $($profileNames[$Profile])" -ForegroundColor White
Write-Host ""

if (!(Test-Path $javaExe)) {
    throw "JDK not found: $javaExe"
}

Sync-ProfileMods
Deploy-Mods

try {
    Write-Host "[1/4] Client jar..." -NoNewline
    $clientJar = Get-ClientJar
    Write-Host " OK" -ForegroundColor Green

    Write-Host "[2/4] Classpath..." -NoNewline
    $cp = @()
    $cp += $clientJar
    $cp += Get-Libraries "$versionsDir\26.1.2\26.1.2.json"
    $cp += Get-Libraries "$versionsDir\fabric-loader-0.19.2-26.1.2\fabric-loader-0.19.2-26.1.2.json"
    $cp += Get-ModJars
    $modCount = (Get-ModJars).Count
    Write-Host " OK ($($cp.Count) jars, mods: $modCount)" -ForegroundColor Green

    Write-Host "[3/4] Natives..." -NoNewline
    Extract-Natives
    Write-Host " OK" -ForegroundColor Green

    Write-Host "[4/4] Launching Minecraft..." -ForegroundColor Green
    Write-Host ""

    $classpath = $cp -join ";"
    $respLines = @(
        "-Djava.library.path=$nativesDir"
        "-Djna.tmpdir=$nativesDir"
        "-Dorg.lwjgl.librarypath=$nativesDir"
        "-Dorg.lwjgl.system.SharedLibraryExtractPath=$nativesDir"
        "-Dio.netty.native.workdir=$nativesDir"
        "-Dminecraft.launcher.brand=keeeensy"
        "-Dminecraft.launcher.version=1.0"
        (Escape-Resp "-DFabricMcEmu= net.minecraft.client.main.Main ")
        "-Xss1M"
        "--sun-misc-unsafe-memory-access=allow"
        "--enable-native-access=ALL-UNNAMED"
        "-Xms2G"
        "-Xmx4G"
        "-XX:+UseCompactObjectHeaders"
        "-XX:+AlwaysPreTouch"
        "-XX:+UseStringDeduplication"
        "-XX:+UseZGC"
        "-cp"
        $classpath
        "net.fabricmc.loader.impl.launch.knot.KnotClient"
        "--username"
        "Keeeensyy"
        "--version"
        "fabric-loader-0.19.2-26.1.2"
        "--gameDir"
        $mcDir
        "--assetsDir"
        $assetsDir
        "--assetIndex"
        "30"
        "--uuid"
        "00000000-0000-0000-0000-000000000000"
        "--accessToken"
        "0"
        "--clientId"
        "keeeensy"
        "--xuid"
        ""
        "--versionType"
        "release"
    )

    $respFile = "$env:TEMP\mc_args_$Profile.txt"
    $respLines | Set-Content -Path $respFile -Encoding ASCII

    $p = Start-Process -FilePath $javaExe -ArgumentList "@`"$respFile`"" -WorkingDirectory $mcDir -PassThru
    Write-Host "PID: $($p.Id)" -ForegroundColor Yellow
    $p.WaitForExit()
}
finally {
    if (Test-Path $nativesDir) { Remove-Item $nativesDir -Recurse -Force }
    Restore-Mods
    Write-Host "Done." -ForegroundColor Cyan
}

param(
    [string]$PackageUrl = "https://github.com/xiangzuoxiangyoukan7/context-atlas/releases/download/v0.11.0/context-atlas-trae-0.11.0.zip",
    [string]$ProjectRoot = (Get-Location).Path
)

$ErrorActionPreference = "Stop"
$project = (Resolve-Path -LiteralPath $ProjectRoot).Path
$temp = Join-Path ([System.IO.Path]::GetTempPath()) ("context-atlas-trae-" + [guid]::NewGuid().ToString("N"))
$zip = Join-Path $temp "context-atlas-trae.zip"
$expanded = Join-Path $temp "expanded"
$backup = $null
$moved = @()

try {
    New-Item -ItemType Directory -Force $temp | Out-Null
    Invoke-WebRequest -Uri $PackageUrl -OutFile $zip
    Expand-Archive -LiteralPath $zip -DestinationPath $expanded -Force
    $agents = Get-ChildItem -LiteralPath $expanded -Directory -Recurse |
        Where-Object { $_.Name -eq ".agents" } | Select-Object -First 1
    if ($null -eq $agents) {
        throw "Trae 发布包缺少 .agents 运行目录"
    }

    $target = Join-Path $project ".agents"
    New-Item -ItemType Directory -Force $target | Out-Null
    $backup = Join-Path $target (".context-atlas-backup-" + (Get-Date -Format "yyyyMMddHHmmss"))
    New-Item -ItemType Directory -Force $backup | Out-Null
    foreach ($name in @("skills", "assets", "references")) {
        $source = Join-Path $agents.FullName $name
        $destination = Join-Path $target $name
        if (Test-Path -LiteralPath $destination) {
            Move-Item -LiteralPath $destination -Destination (Join-Path $backup $name)
            $moved += $name
        }
        Copy-Item -LiteralPath $source -Destination $destination -Recurse -Force
    }
    Write-Output "Context Atlas Trae 0.11.0 已安装到项目：$project"
    Write-Output "如需回滚，可将 $backup 下的目录移回 .agents。"
}
catch {
    if ($null -ne $backup) {
        foreach ($name in $moved) {
            $destination = Join-Path $project ".agents\$name"
            if (Test-Path -LiteralPath $destination) {
                Remove-Item -LiteralPath $destination -Recurse -Force
            }
            $old = Join-Path $backup $name
            if (Test-Path -LiteralPath $old) {
                Move-Item -LiteralPath $old -Destination $destination
            }
        }
    }
    throw
}
finally {
    if (Test-Path -LiteralPath $temp) {
        Remove-Item -LiteralPath $temp -Recurse -Force
    }
}

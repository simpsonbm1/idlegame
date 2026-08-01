<#
.SYNOPSIS
    Set up the Blender MCP connection on a fresh machine.

.DESCRIPTION
    The art pipeline runs headless and needs none of this -- `render_all.py` and
    `render_attacks.py` only need Blender on disk. The MCP connection is for
    driving Blender INTERACTIVELY, with the viewport in front of you, which is
    how new models get built.

    Three pieces have to line up:

      Claude  <-- MCP/stdio -->  blender-mcp  <-- TCP -->  Blender add-on

    This installs all three: `uv` to run the server, a clone of the upstream
    repository, the add-on copied into Blender's extensions folder, and the MCP
    server registered with Claude Code.

    Mirrors what is installed on BENSDESKTOP as of 2026-07-31, where the
    checkout sits at C:\blender_mcp at upstream commit 98b0e49.

.PARAMETER BlenderVersion
    Which Blender's extensions folder to install the add-on into. Defaults to
    5.2, which is what the pipeline is built and verified against.

.PARAMETER CheckoutPath
    Where to clone the upstream repository. Defaults to C:\blender_mcp.

.EXAMPLE
    pwsh -File tools/blender/setup-blender-mcp.ps1
    pwsh -File tools/blender/setup-blender-mcp.ps1 -WhatIfOnly
#>
[CmdletBinding()]
param(
    [string]$BlenderVersion = "5.2",
    [string]$CheckoutPath = "C:\blender_mcp",
    [switch]$WhatIfOnly
)

$ErrorActionPreference = "Stop"
$repoUrl = "https://projects.blender.org/lab/blender_mcp.git"
$extRoot = Join-Path $env:APPDATA "Blender Foundation\Blender\$BlenderVersion\extensions\user_default"
$addonDest = Join-Path $extRoot "mcp"

function Step($msg) { Write-Host "==> $msg" -ForegroundColor Cyan }
function Note($msg) { Write-Host "    $msg" -ForegroundColor DarkGray }

if ($WhatIfOnly) {
    Write-Host "DRY RUN - nothing will be changed" -ForegroundColor Yellow
}

# ---- 1. uv, which runs the MCP server ------------------------------------
Step "Checking for uv"
$uv = (Get-Command uv -ErrorAction SilentlyContinue).Source
if (-not $uv) {
    $winget = Join-Path $env:LOCALAPPDATA "Microsoft\WinGet\Packages\astral-sh.uv_Microsoft.Winget.Source_8wekyb3d8bbwe\uv.exe"
    if (Test-Path $winget) { $uv = $winget }
}
if (-not $uv) {
    Note "not found; installing with winget"
    if (-not $WhatIfOnly) { winget install --id astral-sh.uv --source winget --accept-package-agreements --accept-source-agreements }
    $uv = Join-Path $env:LOCALAPPDATA "Microsoft\WinGet\Packages\astral-sh.uv_Microsoft.Winget.Source_8wekyb3d8bbwe\uv.exe"
} else {
    Note "found at $uv"
}

# ---- 2. the upstream checkout --------------------------------------------
Step "Cloning $repoUrl to $CheckoutPath"
if (Test-Path $CheckoutPath) {
    Note "already present; leaving it alone"
} elseif (-not $WhatIfOnly) {
    git clone $repoUrl $CheckoutPath
}

# ---- 3. the Blender add-on ------------------------------------------------
# Blender loads extensions from a folder named after the manifest id, which is
# "mcp" -- NOT after the source folder, which is "blender_mcp_addon". Copying it
# under its source name leaves Blender unable to find it.
Step "Installing the add-on into Blender $BlenderVersion"
$addonSrc = Join-Path $CheckoutPath "addon\blender_mcp_addon"
if (-not (Test-Path $extRoot)) {
    Note "creating $extRoot"
    if (-not $WhatIfOnly) { New-Item -ItemType Directory -Force -Path $extRoot | Out-Null }
}
Note "$addonSrc  ->  $addonDest"
if (-not $WhatIfOnly) {
    if (Test-Path $addonDest) { Remove-Item -Recurse -Force $addonDest }
    Copy-Item -Recurse -Force $addonSrc $addonDest
}

# ---- 4. register the server with Claude Code ------------------------------
Step "Registering the 'blender' MCP server"
$mcpDir = Join-Path $CheckoutPath "mcp"
Note "claude mcp add blender --scope user -- `"$uv`" --directory `"$mcpDir`" run blender-mcp"
if (-not $WhatIfOnly) {
    $existing = & claude mcp list 2>$null
    if ($existing -match "^blender") {
        Note "already registered; skipping"
    } else {
        & claude mcp add blender --scope user -- "$uv" --directory "$mcpDir" run blender-mcp
    }
}

Write-Host ""
Write-Host "Done. Two things are still manual:" -ForegroundColor Green
Write-Host "  1. Open Blender, then Edit > Preferences > Add-ons, and ENABLE 'MCP'." -ForegroundColor Green
Write-Host "     The add-on is the TCP end of the link and does nothing until enabled." -ForegroundColor Green
Write-Host "  2. Restart Claude Code so it picks up the new MCP server." -ForegroundColor Green
Write-Host ""
Write-Host "Verify: ask Claude to run get_objects_summary with Blender open." -ForegroundColor Green

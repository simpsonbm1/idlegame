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
# -BlenderVersion picks the extensions folder by name. Get it wrong and the copy
# still "succeeds", into a folder no Blender will ever read. If the machine has
# config for OTHER versions but not this one, that is the misconfiguration, so
# say so. A machine whose Blender has never been launched has no config folder at
# all, which is normal and not worth a warning.
$verRoot = Join-Path $env:APPDATA "Blender Foundation\Blender"
if ((Test-Path $verRoot) -and -not (Test-Path (Join-Path $verRoot $BlenderVersion))) {
    $present = (Get-ChildItem $verRoot -Directory | Select-Object -ExpandProperty Name) -join ", "
    if ($present) {
        Write-Host "    WARNING: no config for Blender $BlenderVersion; this machine has $present" -ForegroundColor Yellow
        Write-Host "             Re-run with -BlenderVersion <one of those> or the add-on lands where nothing reads it." -ForegroundColor Yellow
    }
}
if (-not (Test-Path $extRoot)) {
    Note "creating $extRoot"
    if (-not $WhatIfOnly) { New-Item -ItemType Directory -Force -Path $extRoot | Out-Null }
}
Note "$addonSrc  ->  $addonDest"
if (-not $WhatIfOnly) {
    if (Test-Path $addonDest) { Remove-Item -Recurse -Force $addonDest }
    Copy-Item -Recurse -Force $addonSrc $addonDest
}

$mcpDir = Join-Path $CheckoutPath "mcp"

# ---- 4. pin the MCP SDK below 2.0 -----------------------------------------
# Upstream asks for `mcp[cli]>=1.2.0` with no upper bound, but its code imports
# `mcp.server.fastmcp`, which mcp 2.0.0 removed. A fresh clone resolves to 2.x
# and the server dies on import with ModuleNotFoundError. Verified on
# LAPTOP-7EN0K6TP 2026-08-01: 1.29.0 works, 2.0.0 does not. Delete this step
# when upstream supports the 2.x API.
Step "Pinning mcp below 2.0 in the checkout's pyproject.toml"
$pyproject = Join-Path $mcpDir "pyproject.toml"
if (Test-Path $pyproject) {
    $text = Get-Content $pyproject -Raw
    if ($text -match [regex]::Escape('"mcp[cli]>=1.2.0",')) {
        Note 'mcp[cli]>=1.2.0  ->  mcp[cli]>=1.2.0,<2'
        if (-not $WhatIfOnly) {
            $text = $text.Replace('"mcp[cli]>=1.2.0",', '"mcp[cli]>=1.2.0,<2",')
            [System.IO.File]::WriteAllText($pyproject, $text)
        }
    } else {
        Note "no unpinned mcp[cli] dependency found; leaving pyproject.toml alone"
    }
}

# ---- 5. build the server's virtualenv -------------------------------------
# Done here rather than lazily on first use, so a broken resolve shows up now
# instead of as a silently dead MCP server later.
Step "Building the server virtualenv"
if (-not $WhatIfOnly) { & $uv --directory $mcpDir sync }

# ---- 6. register the server with Claude Code ------------------------------
# The `claude` CLI is not on PATH under the desktop app, so fall back to writing
# the user-scope config directly. Both routes land in the same place: the
# top-level "mcpServers" object of ~/.claude.json.
Step "Registering the 'blender' MCP server"
Note "command: `"$uv`" --directory `"$mcpDir`" run blender-mcp"
$claude = (Get-Command claude -ErrorAction SilentlyContinue).Source
if ($WhatIfOnly) {
    Note $(if ($claude) { "would use the claude CLI" } else { "no claude CLI; would edit ~/.claude.json directly" })
} elseif ($claude) {
    $existing = & claude mcp list 2>$null
    if ($existing -match "^blender") {
        Note "already registered; skipping"
    } else {
        & claude mcp add blender --scope user -- "$uv" --directory "$mcpDir" run blender-mcp
    }
} else {
    Note "no claude CLI on PATH; editing ~/.claude.json directly"
    $cfg = Join-Path $env:USERPROFILE ".claude.json"
    if (-not (Test-Path $cfg)) { throw "no $cfg to register into" }
    # -AsHashtable because the file contains project keys differing only in case,
    # which ConvertFrom-Json rejects by default.
    $parsed = Get-Content $cfg -Raw | ConvertFrom-Json -AsHashtable
    if ($parsed.ContainsKey("mcpServers") -and $parsed["mcpServers"].ContainsKey("blender")) {
        Note "already registered; skipping"
    } else {
        Copy-Item $cfg "$cfg.bak-preblender" -Force
        $raw = Get-Content $cfg -Raw
        $entry = [ordered]@{
            blender = [ordered]@{
                type    = "stdio"
                command = $uv
                args    = @("--directory", $mcpDir, "run", "blender-mcp")
                env     = @{}
            }
        }
        # Splice the key in as text rather than re-serialising the whole file,
        # which would drop those same case-colliding project keys.
        $json = ($entry | ConvertTo-Json -Depth 6).Trim()
        $inner = $json.Substring(1, $json.Length - 2).TrimEnd()
        $open = $raw.IndexOf("{")
        [System.IO.File]::WriteAllText($cfg, "{`n  `"mcpServers`": {$inner`n  }," + $raw.Substring($open + 1))
        try { $null = Get-Content $cfg -Raw | ConvertFrom-Json -AsHashtable }
        catch { Copy-Item "$cfg.bak-preblender" $cfg -Force; throw "config edit produced invalid JSON; restored backup" }
        Note "registered; backup at $cfg.bak-preblender"
    }
}

Write-Host ""
Write-Host "Done. Two things are still manual:" -ForegroundColor Green
Write-Host "  1. Open Blender, then Edit > Preferences > Add-ons, and ENABLE 'MCP'." -ForegroundColor Green
Write-Host "     The add-on is the TCP end of the link and does nothing until enabled." -ForegroundColor Green
Write-Host "  2. Restart Claude Code so it picks up the new MCP server." -ForegroundColor Green
Write-Host ""
Write-Host "Verify: ask Claude to run get_objects_summary with Blender open." -ForegroundColor Green

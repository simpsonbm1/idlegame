<#
.SYNOPSIS
  Design-read gate (idlegame). Refuses the MAIN session's first game.js edit of a session,
  pointing at DESIGN.md, then lets the retry through. Subagent edits pass silently.

.DESCRIPTION
  Exists for the opus-and-under authoring rule (user ruling 2026-07-27, recorded in
  ~/.claude/harness/context-audit-2026-07-27.md): a pointer read at session start is not
  followed at edit time, so when the design spec moved out of the auto-loaded CLAUDE.md
  the pointer to it had to fire at the moment of need. This gate is that delivery.

  Mechanism patterns are copied from the proven fleet:
  - Subagent detection mirrors askamods delegation-gate: a PreToolUse payload carries
    agent_id ONLY inside a subagent (fire-verified 2026-07-21).
  - Once-per-session mirrors state-check-gate: a stamp keyed by sanitized session_id
    under %LOCALAPPDATA%\claude-hooks.
  - The transcript check mirrors handoff-read-nag/skill-gate: a Read tool_use naming
    DESIGN.md on one JSONL line satisfies the gate before it ever fires; a prose mention
    does not.

  Fails open on any internal error (exit 0): a QoL gate must never wedge a session. A dead
  gate is the liveness sweep's job to report, which is why -SelfTest exists.
#>
param([switch]$SelfTest)
. "$env:USERPROFILE/.claude/hooks/_encoding.ps1"

$script:RefusalText = @'
[design-read-gate] First game.js edit this session. game.js is a prototype being redesigned
around the spec: DESIGN.md is the source of truth, not the code's current behavior. Before
editing, Read the DESIGN.md sections relevant to this change - mechanics, formulas, and
balance values must match it, and any balance change also reruns node tools/balance-sim.js
and updates the sim's mirrored constants. Repeat the call and it goes through.
'@

function Get-GateDecision {
    # Returns 'block' or 'pass'. Pure decision logic so the self-test can drive it in-process.
    param([string]$EventJson)
    if (-not $EventJson) { return 'pass' }
    try { $ev = $EventJson | ConvertFrom-Json } catch { return 'pass' }
    if (-not $ev) { return 'pass' }

    # Subagents pass: they receive the design context in their delegation prompt.
    if ($ev.PSObject.Properties.Name -contains 'agent_id' -and $ev.agent_id) { return 'pass' }

    $fp = ''
    if ($ev.PSObject.Properties.Name -contains 'tool_input' -and $ev.tool_input -and
        $ev.tool_input.PSObject.Properties.Name -contains 'file_path' -and $ev.tool_input.file_path) {
        $fp = [string]$ev.tool_input.file_path
    }
    if ($fp -notmatch '(?i)(^|[\\/])game\.js$') { return 'pass' }

    # A DESIGN.md Read already in the transcript satisfies the gate without friction.
    $tx = ''
    if ($ev.PSObject.Properties.Name -contains 'transcript_path' -and $ev.transcript_path) {
        $tx = [string]$ev.transcript_path
    }
    if ($tx -and (Test-Path -LiteralPath $tx)) {
        $hit = Select-String -LiteralPath $tx -Pattern '"name"\s*:\s*"Read"' |
               Where-Object { $_.Line -match 'DESIGN\.md' } | Select-Object -First 1
        if ($hit) { return 'pass' }
    }

    $sessionId = 'nosession'
    if ($ev.PSObject.Properties.Name -contains 'session_id' -and $ev.session_id) {
        $sessionId = [string]$ev.session_id
    }
    $safeId = ($sessionId -replace '[^A-Za-z0-9_.-]', '_')
    $stampDir = Join-Path $env:LOCALAPPDATA 'claude-hooks'
    if (-not (Test-Path -LiteralPath $stampDir)) {
        New-Item -ItemType Directory -Path $stampDir -Force | Out-Null
    }
    $stamp = Join-Path $stampDir "design-read-gate-$safeId.stamp"
    if (Test-Path -LiteralPath $stamp) { return 'pass' }
    Write-Utf8File -Path $stamp -Content (Get-Date -Format o)
    return 'block'
}

if ($SelfTest) {
    $script:tfails = 0
    function Check { param([string]$Name, [bool]$Ok)
        if ($Ok) { Write-Host "  ok   $Name" } else { Write-Host "  FAIL $Name"; $script:tfails++ } }

    $mkSid = { 'st-' + [guid]::NewGuid().ToString('N') }
    $mkEv = { param($sid, $extra, $fp)
        $h = @{ session_id = $sid; tool_name = 'Edit'; tool_input = @{ file_path = $fp } }
        foreach ($k in $extra.Keys) { $h[$k] = $extra[$k] }
        ($h | ConvertTo-Json -Compress) }

    $tmp = Join-Path ([System.IO.Path]::GetTempPath()) ('drg-selftest-' + [guid]::NewGuid().ToString('N'))
    New-Item -ItemType Directory -Path $tmp | Out-Null
    $txRead = Join-Path $tmp 'tx-read.jsonl'
    Write-Utf8File -Path $txRead -Content '{"type":"assistant","message":{"content":[{"type":"tool_use","name":"Read","input":{"file_path":"D:\\x\\DESIGN.md"}}]}}'
    $txMention = Join-Path $tmp 'tx-mention.jsonl'
    Write-Utf8File -Path $txMention -Content '{"type":"assistant","text":"I will read DESIGN.md at some point"}'

    # 1. Main-session first game.js edit blocks; the SAME session's retry passes (stamp).
    $sid = & $mkSid
    Check 'first game.js edit blocks'   ((Get-GateDecision (& $mkEv $sid @{} 'D:\x\game.js')) -eq 'block')
    Check 'same-session retry passes'   ((Get-GateDecision (& $mkEv $sid @{} 'D:\x\game.js')) -eq 'pass')

    # 2. Subagent game.js edit passes untouched (fresh session).
    Check 'subagent edit passes'        ((Get-GateDecision (& $mkEv (& $mkSid) @{ agent_id = 'abc'; agent_type = 'general-purpose' } 'D:\x\game.js')) -eq 'pass')

    # 3. Non-game.js edits pass; a file merely containing the name does not match.
    Check 'style.css passes'            ((Get-GateDecision (& $mkEv (& $mkSid) @{} 'D:\x\style.css')) -eq 'pass')
    Check 'my-game.js.md passes'        ((Get-GateDecision (& $mkEv (& $mkSid) @{} 'D:\x\game.js.md')) -eq 'pass')

    # 4. A real DESIGN.md Read in the transcript satisfies the gate; a prose mention does not.
    Check 'transcript Read satisfies'   ((Get-GateDecision (& $mkEv (& $mkSid) @{ transcript_path = $txRead } 'D:\x\game.js')) -eq 'pass')
    Check 'prose mention still blocks'  ((Get-GateDecision (& $mkEv (& $mkSid) @{ transcript_path = $txMention } 'D:\x\game.js')) -eq 'block')

    # 5. Degenerate inputs pass (fail-open contract).
    Check 'empty stdin passes'          ((Get-GateDecision '') -eq 'pass')
    Check 'malformed JSON passes'       ((Get-GateDecision '{not json') -eq 'pass')

    # 6. Child-process pipe test: real stdin, real exit codes, refusal on stderr.
    $self = $MyInvocation.MyCommand.Path
    function Invoke-Child { param([string]$Json)
        $inFile = Join-Path $tmp ('in-' + [guid]::NewGuid().ToString('N'))
        $errFile = Join-Path $tmp ('err-' + [guid]::NewGuid().ToString('N'))
        Write-Utf8File -Path $inFile -Content $Json
        $p = Start-Process -FilePath 'pwsh' -ArgumentList @('-NoProfile','-ExecutionPolicy','Bypass','-File',('"' + $self + '"')) `
             -RedirectStandardInput $inFile -RedirectStandardError $errFile -PassThru -Wait -WindowStyle Hidden
        $err = ''
        if (Test-Path $errFile) { $err = [System.IO.File]::ReadAllText($errFile, [System.Text.Encoding]::UTF8) }
        return @{ Code = $p.ExitCode; Err = $err }
    }
    $r = Invoke-Child -Json (& $mkEv (& $mkSid) @{} 'D:\x\game.js')
    Check 'child: first edit exit 2 + pointer' ($r.Code -eq 2 -and $r.Err -match 'DESIGN\.md is the source of truth')
    $r = Invoke-Child -Json (& $mkEv (& $mkSid) @{ agent_id = 'abc' } 'D:\x\game.js')
    Check 'child: subagent exit 0'      ($r.Code -eq 0)
    $r = Invoke-Child -Json ''
    Check 'child: empty stdin exit 0'   ($r.Code -eq 0)

    Remove-Item -Recurse -Force $tmp -ErrorAction SilentlyContinue
    Get-ChildItem (Join-Path $env:LOCALAPPDATA 'claude-hooks') -Filter 'design-read-gate-st-*.stamp' -ErrorAction SilentlyContinue |
        Remove-Item -Force -ErrorAction SilentlyContinue
    if ($script:tfails -gt 0) { Write-Host "SELF-TEST: $script:tfails FAILURE(S)"; exit 1 }
    Write-Host 'SELF-TEST: all passed'; exit 0
}

try {
    $raw = Read-HookStdin
    if ((Get-GateDecision $raw) -eq 'block') {
        [Console]::Error.WriteLine($script:RefusalText)
        exit 2
    }
    exit 0
} catch {
    exit 0
}

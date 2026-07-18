# Renders the two annotated layout mockups for the Antigravity scene-pair
# generation (M15_ASSET_SPECS.md entry 85) into assets/reference/.
# These accompany the prompts as geometric ground truth — the generator
# respects reference images far more than prose. Rough on purpose: colored
# regions + text labels, not art. Rerun after editing to regenerate.
#   powershell -File tools\make-scene-mockups.ps1

Add-Type -AssemblyName System.Drawing

$repo = Split-Path $PSScriptRoot -Parent
$outDir = Join-Path $repo 'assets\reference'

function New-Ctx {
    $bmp = New-Object System.Drawing.Bitmap 1024, 1024
    $g = [System.Drawing.Graphics]::FromImage($bmp)
    $g.SmoothingMode = 'AntiAlias'
    $g.TextRenderingHint = 'AntiAliasGridFit'
    @{ bmp = $bmp; g = $g }
}

$col = @{
    sky = '#b8d4e8'; mountain = '#8a9aac'; grass = '#9db86a'; grassOut = '#a3b878'
    dirt = '#c2a878'; wall = '#9a9a92'; wallDark = '#7a7a72'; door = '#8a5a30'
    plaza = '#b0aa96'; tree = '#4a7a3a'; ink = '#222222'; halo = '#ffffff'
}
function B([string]$hex) { New-Object System.Drawing.SolidBrush ([System.Drawing.ColorTranslator]::FromHtml($hex)) }

function Label($g, [int]$tx, [int]$ty, [string[]]$lines, [int]$size = 26) {
    $font = New-Object System.Drawing.Font('Arial', $size, [System.Drawing.FontStyle]::Bold, [System.Drawing.GraphicsUnit]::Pixel)
    $y = $ty
    foreach ($ln in $lines) {
        foreach ($o in @(@(-2,0),@(2,0),@(0,-2),@(0,2),@(-2,-2),@(2,-2),@(-2,2),@(2,2))) {
            $g.DrawString($ln, $font, (B $col.halo), [single]($tx + $o[0]), [single]($y + $o[1]))
        }
        $g.DrawString($ln, $font, (B $col.ink), [single]$tx, [single]$y)
        $y += [int]($size * 1.2)
    }
}
function Arrow($g, [int]$x1, [int]$y1, [int]$x2, [int]$y2) {
    $pen = New-Object System.Drawing.Pen ([System.Drawing.ColorTranslator]::FromHtml($col.ink)), 4
    $g.DrawLine($pen, $x1, $y1, $x2, $y2)
    $a = [Math]::Atan2($y2 - $y1, $x2 - $x1)
    foreach ($da in @(-0.4, 0.4)) {
        $g.DrawLine($pen, $x2, $y2,
            [int]($x2 - 16 * [Math]::Cos($a + $da)), [int]($y2 - 16 * [Math]::Sin($a + $da)))
    }
}
function Tree($g, [int]$cx, [int]$cy, [int]$r = 24) {
    $g.FillEllipse((B $col.tree), $cx - $r, $cy - $r, 2 * $r, 2 * $r)
}
function Road($g, [int[]]$p0, [int[]]$c, [int[]]$p1, [int]$w) {
    # quadratic (p0, c, p1) as cubic bezier with a round-cap thick pen
    $pen = New-Object System.Drawing.Pen ([System.Drawing.ColorTranslator]::FromHtml($col.dirt)), $w
    $pen.StartCap = 'Round'; $pen.EndCap = 'Round'
    $c1x = $p0[0] + 2.0 * ($c[0] - $p0[0]) / 3.0; $c1y = $p0[1] + 2.0 * ($c[1] - $p0[1]) / 3.0
    $c2x = $p1[0] + 2.0 * ($c[0] - $p1[0]) / 3.0; $c2y = $p1[1] + 2.0 * ($c[1] - $p1[1]) / 3.0
    $g.DrawBezier($pen, [single]$p0[0], [single]$p0[1], [single]$c1x, [single]$c1y, [single]$c2x, [single]$c2y, [single]$p1[0], [single]$p1[1])
}
function Mountains($g, [int]$seed) {
    $g.FillRectangle((B $col.sky), 0, 0, 1024, 120)
    $pts = New-Object System.Collections.Generic.List[System.Drawing.Point]
    $pts.Add([System.Drawing.Point]::new(0, 120))
    for ($i = 0; $i -le 8; $i++) {
        $pts.Add([System.Drawing.Point]::new($i * 128 + 64, 45 + (($i + $seed) % 3) * 22))
        $pts.Add([System.Drawing.Point]::new(($i + 1) * 128, 120))
    }
    $g.FillPolygon((B $col.mountain), $pts.ToArray())
}
function Crenel($g, [int]$xa, [int]$ya, [int]$xb, [int]$yb, [int]$step) {
    $br = B $col.wallDark
    if ($ya -eq $yb) { for ($px = $xa; $px -lt $xb; $px += $step * 2) { $g.FillRectangle($br, $px, $ya - 10, $step, 10) } }
    else { for ($py = $ya; $py -lt $yb; $py += $step * 2) { $g.FillRectangle($br, $xa - 10, $py, 10, $step) } }
}

# ---------------- Mockup A: the town square (85a) ----------------
$a = New-Ctx; $g = $a.g
Mountains $g 0
$g.FillRectangle((B $col.grass), 0, 120, 1024, 904)
$g.FillRectangle((B $col.wall), 0, 120, 1024, 90)          # north wall
Crenel $g 0 130 1024 130 16
$g.FillRectangle((B $col.wall), 0, 120, 55, 904)           # west wall
$g.FillRectangle((B $col.wall), 940, 120, 84, 904)         # EAST wall, vertical
Crenel $g 950 220 950 1024 16
$g.FillRectangle((B $col.wallDark), 920, 105, 104, 125)    # NE corner tower
$g.FillRectangle((B $col.wallDark), 875, 400, 149, 190)    # gatehouse body
$g.FillRectangle((B $col.wall), 885, 380, 50, 40)          # gate towers
$g.FillRectangle((B $col.wall), 974, 380, 50, 40)
$g.FillRectangle((B $col.door), 880, 455, 44, 110)         # closed doors
Road $g @(30, 1010) @(480, 760) @(872, 510) 46
$g.FillEllipse((B $col.plaza), 295, 638, 270, 184)         # plaza
$g.FillRectangle((B '#555555'), 412, 706, 36, 36)          # well
Tree $g 130 290; Tree $g 210 258; Tree $g 620 265; Tree $g 140 860; Tree $g 700 930
Label $g 20 8   @('narrow band: distant mountains + sky (top 12% ONLY)') 24
Label $g 340 152 @('stone wall with battlements') 24
Label $g 70 240 @('FLAT OBLIQUE PROJECTION (16-bit RPG town map):',
                  'walls PARALLEL to image edges - no vanishing point') 24
Label $g 590 640 @('EAST WALL: PERFECTLY', 'VERTICAL, flush with', 'right edge, top to', 'bottom, NO bends') 24
Arrow $g 900 700 955 700
Arrow $g 900 900 955 900
Label $g 555 420 @('gatehouse + CLOSED', 'wooden doors, midway') 24
Arrow $g 800 445 875 470
Label $g 90 460 @('dirt road: lower-left corner to the gate') 24
Label $g 250 838 @('cobbled plaza + stone well (lower-center)') 24
Arrow $g 400 848 425 750
Label $g 300 330 @('everything else: EMPTY trampled grass',
                   'NO buildings, tents, carts, people, animals') 24
Label $g 70 960 @('a few trees near the walls') 22
$a.bmp.Save((Join-Path $outDir 'mockup_town_square.png'), [System.Drawing.Imaging.ImageFormat]::Png)
$g.Dispose(); $a.bmp.Dispose()

# ---------------- Mockup B: the battlefield square (85b) ----------------
$b = New-Ctx; $g = $b.g
Mountains $g 1
$g.FillRectangle((B $col.grassOut), 0, 120, 1024, 904)
$tr = New-Object System.Drawing.SolidBrush ([System.Drawing.Color]::FromArgb(128, 194, 168, 120))
$g.FillEllipse($tr, 210, 520, 420, 240)                    # trampled patches
$g.FillEllipse($tr, 540, 760, 320, 180)
Road $g @(0, 520) @(430, 500) @(800, 215) 52
foreach ($t in @(@(700,150),@(760,190),@(820,150),@(880,200),@(940,160),@(990,210),
                 @(860,255),@(930,265),@(990,300),@(780,250),@(1000,150),@(960,360),
                 @(1000,420),@(930,315))) { Tree $g $t[0] $t[1] 30 }
$dp = New-Object System.Drawing.Pen ([System.Drawing.ColorTranslator]::FromHtml('#6a5030')), 5
$g.DrawLine($dp, 300, 500, 340, 520)                        # debris marks
$g.DrawLine($dp, 560, 740, 590, 725)
$g.FillEllipse((B '#888888'), 236, 786, 28, 28)
Label $g 20 8   @('SAME mountain band, SAME height as the town image') 24
Label $g 28 200 @('LEFT EDGE: the town wall stands JUST',
                  'off this edge - draw NO wall, only',
                  'trampled ground at its base') 24
Arrow $g 100 300 12 300
Label $g 40 600 @('road enters left edge 50% down -', 'LEVEL WITH THE TOWN GATE') 24
Arrow $g 110 592 15 528
Label $g 330 430 @('ground: SAME GREEN GRASS as the town,', 'trampled with muddy patches - NOT desert') 24
Label $g 560 330 @('dense treeline upper right -', 'raids arrive down this road') 24
Arrow $g 680 350 780 240
Label $g 380 720 @('EMPTY trampled battlefield:',
                   'NO creatures, NO structures, NO wall,',
                   'no well or plaza from the town image') 24
Label $g 150 900 @('sparse debris only (broken arrow, a rock or two)') 22
$b.bmp.Save((Join-Path $outDir 'mockup_field_square.png'), [System.Drawing.Imaging.ImageFormat]::Png)
$g.Dispose(); $b.bmp.Dispose()

Write-Output "wrote mockup_town_square.png + mockup_field_square.png to $outDir"

# 百年散歩 バックアップ
#
#   使い方: PowerShell で次を実行するだけ
#       & "E:\AI_Projects\クロードコード部\ニコ活動\百年散歩\バックアップ.ps1"
#
#   2か所へ日付つきで保存する:
#     A) C:\backup\百年散歩\                    … このPCのSSD側(E:のHDDが壊れても残る)
#     C) \\Akira\ai_共有\バックアップ\百年散歩\ … 別のPC(このPCごと駄目になっても残る)
#
#   取ったあとに必ず読み直して、取材記録が何件入っているかを表示する。
#   「取ったつもり」で中身が壊れている、を防ぐため。
#
#   ※このファイルは UTF-8(BOM付き) で保存すること。
#     BOM無しだと Windows PowerShell 5.1 が日本語を読み違えて動かない。

$ErrorActionPreference = "Stop"

$src       = "E:\AI_Projects\クロードコード部\ニコ活動\百年散歩"
$destLocal = "C:\backup\百年散歩"
$destShare = "\\Akira\ai_共有\バックアップ\百年散歩"
$shareRoot = "\\Akira\ai_共有"
$keep      = 30

$stamp  = Get-Date -Format "yyyy-MM-dd_HHmm"
$skip   = @(".git", "__pycache__")

Write-Host ""
Write-Host "百年散歩 バックアップ  $stamp" -ForegroundColor Cyan
Write-Host ("-" * 52)

# ---- 元データの確認(取る前に、取るものが正しいか見る) ----
$srcJson = Join-Path $src "streamlit\data\shops.json"
if (-not (Test-Path $srcJson)) {
    Write-Host "★ 取材記録が見つかりません: $srcJson" -ForegroundColor Red
    exit 1
}
$srcCount = @(Get-Content $srcJson -Raw -Encoding utf8 | ConvertFrom-Json).Count
Write-Host "元データ: 取材記録 $srcCount 件"
Write-Host ""

function Backup-To($root, $label) {
    try {
        $to = Join-Path $root $stamp
        New-Item -ItemType Directory -Path $to -Force | Out-Null
        Copy-Item -Path (Join-Path $src "*") -Destination $to -Recurse -Force -Exclude $skip
        foreach ($s in $skip) {
            Get-ChildItem $to -Recurse -Force -Directory -Filter $s -ErrorAction SilentlyContinue |
                Remove-Item -Recurse -Force -ErrorAction SilentlyContinue
        }
        return $to
    } catch {
        Write-Host "  $label : 失敗 - $($_.Exception.Message)" -ForegroundColor Red
        return $null
    }
}

function Verify-Backup($to, $label) {
    if (-not $to) { Write-Host "  $label : NG 取れていません" -ForegroundColor Red; return $false }
    $f = Join-Path $to "streamlit\data\shops.json"
    if (-not (Test-Path $f)) {
        Write-Host "  $label : NG 取材記録が入っていません" -ForegroundColor Red
        return $false
    }
    try {
        $n = @(Get-Content $f -Raw -Encoding utf8 | ConvertFrom-Json).Count
    } catch {
        Write-Host "  $label : NG 読み直せません(壊れています)" -ForegroundColor Red
        return $false
    }
    if ($n -ne $srcCount) {
        Write-Host "  $label : NG 件数が合いません(元 $srcCount / 控え $n)" -ForegroundColor Red
        return $false
    }
    $files = (Get-ChildItem $to -Recurse -File).Count
    Write-Host "  $label : OK  取材記録 $n 件 / ファイル $files 個" -ForegroundColor Green
    Write-Host "      $to" -ForegroundColor DarkGray
    return $true
}

function Remove-Old($root, $label) {
    if (-not (Test-Path $root)) { return }
    $old = @(Get-ChildItem $root -Directory | Sort-Object Name -Descending | Select-Object -Skip $keep)
    foreach ($g in $old) { Remove-Item $g.FullName -Recurse -Force -ErrorAction SilentlyContinue }
    if ($old.Count -gt 0) {
        Write-Host "  $label : 古い控え $($old.Count) 世代を片づけました" -ForegroundColor DarkGray
    }
}

$toLocal = Backup-To $destLocal "A 手元(C:)"
$okLocal = Verify-Backup $toLocal "A 手元(C:)"

$okShare = $false
if (Test-Path $shareRoot) {
    $toShare = Backup-To $destShare "C 別PC(共有)"
    $okShare = Verify-Backup $toShare "C 別PC(共有)"
} else {
    Write-Host "  C 別PC(共有) : NG つながりません(相手のPCの電源が入っていない可能性)" -ForegroundColor Yellow
}

Remove-Old $destLocal "A 手元(C:)"
if ($okShare) { Remove-Old $destShare "C 別PC(共有)" }

Write-Host ""
Write-Host ("-" * 52)
if ($okLocal -and $okShare) {
    Write-Host "2か所とも取れました。安心してよい状態です。" -ForegroundColor Green
} elseif ($okLocal) {
    Write-Host "手元(C:)だけ取れました。別PCへは届いていません。" -ForegroundColor Yellow
    Write-Host "相手のPCが起動したら、もう一度実行してください。" -ForegroundColor Yellow
} else {
    Write-Host "★ バックアップできていません。上のメッセージを確認してください。" -ForegroundColor Red
}
Write-Host ""

# VespAI check launcher (Seohyun, CAP-AI-21). ASCII only on purpose.
# Uses the J1 install (Documents\capstone_vespai) made by 1_install_vespai.bat (Seungjun's j1_vespai_windows.ps1).
# No argument = webcam. A video file or a folder of pictures as argument = file mode (5 conditions, table).
$ErrorActionPreference = 'Continue'
# Where the J1 install is: next to this kit folder (..\capstone_vespai) first, then Documents\capstone_vespai
$Base = $null
foreach ($c in @((Join-Path (Split-Path $PSScriptRoot -Parent) 'capstone_vespai'), (Join-Path ([Environment]::GetFolderPath('MyDocuments')) 'capstone_vespai'))) {
    if (Test-Path (Join-Path $c 'venv\Scripts\python.exe')) { $Base = $c; break }
}
if (-not $Base) { Write-Host 'capstone_vespai folder not found (looked next to this folder and in Documents). Run 1_install_vespai.bat first.' -ForegroundColor Red; exit 1 }
Write-Host "Using $Base"
$Py   = Join-Path $Base 'venv\Scripts\python.exe'
$Yolo = Join-Path $Base 'yolov5'
$W    = Join-Path $Base 'vespai\models\yolov5-params\yolov5s-all-data.pt'
$Here = $PSScriptRoot
$Chk  = Join-Path $Here 'vespai_check.py'
$Out  = Join-Path $Here ('out_check_' + (Get-Date -Format 'yyyyMMdd_HHmm'))
$WEIGHTS_SHA = '1FFF0BDE968690917E6136077BF144DDA2E03CCCAA5AE0648CF2BF5CCE423694'
foreach ($p in @($Py, $Yolo, $W, $Chk)) {
    if (-not (Test-Path $p)) {
        Write-Host "MISSING: $p" -ForegroundColor Red
        Write-Host 'Run 1_install_vespai.bat first (5-15 min, about 300 MB).'
        exit 1
    }
}
if ((Get-FileHash $W -Algorithm SHA256).Hash -ne $WEIGHTS_SHA) { Write-Host 'Weights hash mismatch - NOT loaded.' -ForegroundColor Red; exit 1 }
$env:YOLOv5_AUTOINSTALL = 'False'
$env:TORCH_FORCE_NO_WEIGHTS_ONLY_LOAD = '1'
$env:PYTHONIOENCODING = 'utf-8'
$env:PYTHONWARNINGS = 'ignore::FutureWarning'
Write-Host 'Webcam keys (click the video window first): g grid, k chamber only, i size 640/1280, [ ] frame mm, +/- conf, s save, q quit'
& $Py $Chk --yolo $Yolo --weights $W --out $Out @args
Write-Host ''
Write-Host "Results: $Out  (check_summary.txt, check_*.csv)" -ForegroundColor Green

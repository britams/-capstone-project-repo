# VespAI live webcam (CAP-AI-SJ-09). Put this file in the J1 folder (the one with venv, yolov5, vespai)
# and start it with vespai_webcam_windows.bat (double-click). ASCII only on purpose.
$ErrorActionPreference = 'Continue'
$Base = $PSScriptRoot
$Py   = Join-Path $Base 'venv\Scripts\python.exe'
$Yolo = Join-Path $Base 'yolov5'
$W    = Join-Path $Base 'vespai\models\yolov5-params\yolov5s-all-data.pt'
$Live = Join-Path $Base 'vespai_live_webcam.py'
$Out  = Join-Path $Base 'out_live'
$WEIGHTS_SHA = '1FFF0BDE968690917E6136077BF144DDA2E03CCCAA5AE0648CF2BF5CCE423694'

foreach ($p in @($Py, $Yolo, $W, $Live)) {
    if (-not (Test-Path $p)) {
        Write-Host "MISSING: $p" -ForegroundColor Red
        Write-Host 'Run the J1 setup (j1_vespai_windows.bat) first, or put this file in the J1 folder.'
        exit 1
    }
}
if ((Get-FileHash $W -Algorithm SHA256).Hash -ne $WEIGHTS_SHA) { Write-Host 'Weights hash mismatch - NOT loaded.' -ForegroundColor Red; exit 1 }

& $Py -c "import torch, cv2" 2>$null
if ($LASTEXITCODE) {
    Write-Host 'The Python environment does not start (maybe moved or Python removed).' -ForegroundColor Red
    Write-Host 'Fix: delete the venv folder and run j1_vespai_windows.bat again.'
    exit 1
}

$env:YOLOv5_AUTOINSTALL = 'False'
$env:TORCH_FORCE_NO_WEIGHTS_ONLY_LOAD = '1'
$env:PYTHONIOENCODING = 'utf-8'
$env:PYTHONWARNINGS = 'ignore::FutureWarning'
Write-Host 'Click the video window, then: q = quit, s = save picture, + / - = confidence, c = next camera'
& $Py $Live --yolo $Yolo --weights $W --out $Out @args
Write-Host ''
Write-Host "Results: $Out  (send live_summary.txt and any snap_*.jpg to Claude)" -ForegroundColor Green

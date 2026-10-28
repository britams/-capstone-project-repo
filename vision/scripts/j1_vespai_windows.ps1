# J1 - VespAI step 1 on Windows (CAP-AI-SJ-03)
# Runs VespAI weights on the repo's example frames and compares with the original results.
# Start it with j1_vespai_windows.bat (double-click). Re-running is safe: finished steps are skipped.
# Everything goes into  Documents\capstone_vespai  . Delete that folder to undo.
# ASCII only on purpose (Windows PowerShell 5.1 misreads UTF-8 without BOM).

$ErrorActionPreference = 'Continue'   # native tools (pip) write warnings to stderr; failures are checked by exit code
$ProgressPreference = 'SilentlyContinue'
[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12

$Base   = Join-Path ([Environment]::GetFolderPath('MyDocuments')) 'capstone_vespai'
$Venv   = Join-Path $Base 'venv'
$VPy    = Join-Path $Venv 'Scripts\python.exe'
$Yolo   = Join-Path $Base 'yolov5'
$Data   = Join-Path $Base 'vespai'
$Out    = Join-Path $Base 'out'
New-Item -ItemType Directory -Force -Path $Base, $Out | Out-Null
Start-Transcript -Path (Join-Path $Base 'j1_log.txt') -Force | Out-Null

$VESPAI_COMMIT = '004f3d8930d19affd04f5d112224107c5d81eec4'   # andrw3000/vespai, 2026-09-15
$YOLO_COMMIT   = '23701eac7a7b160e478ba4bbef966d0af9348251'   # ultralytics/yolov5, pinned by VespAI
$WEIGHTS_SHA   = '1FFF0BDE968690917E6136077BF144DDA2E03CCCAA5AE0648CF2BF5CCE423694'
$RAW_VESPAI    = "https://raw.githubusercontent.com/andrw3000/vespai/$VESPAI_COMMIT"
$RAW_TEAM      = 'https://raw.githubusercontent.com/britams/-capstone-project-repo/main/vision/scripts/run_vespai_examples.py'

function Step($msg) { Write-Host ''; Write-Host "==== $msg" -ForegroundColor Cyan }
function Get-Url($url, $dest) {
    if (Test-Path $dest) { return }
    New-Item -ItemType Directory -Force -Path (Split-Path $dest) -ErrorAction Stop | Out-Null
    Invoke-WebRequest -Uri $url -OutFile $dest -UseBasicParsing -ErrorAction Stop
}
function Try-Python($exe, $pyArgs) {
    try {
        $v = & $exe @pyArgs -c "import sys;print('%d.%d' % sys.version_info[:2])" 2>$null
        if ($LASTEXITCODE -eq 0 -and $v -match '^\d+\.\d+$') { return $v }
    } catch {}
    return $null
}

try {
    # 1. Python
    Step '1/6 Find Python'
    $route = $null; $pyExe = $null; $pyArgs = @()
    foreach ($ver in @('-3.12', '-3.11')) {
        $v = Try-Python 'py' @($ver)
        if ($v) { $pyExe = 'py'; $pyArgs = @($ver); $route = 'A'; break }
    }
    if (-not $route) {
        $v = Try-Python 'py' @()
        if ($v) { $pyExe = 'py'; $route = 'B' }
        else {
            $v = Try-Python 'python' @()
            if ($v) { $pyExe = 'python'; $route = 'B' }
        }
    }
    if (-not $route) { throw 'Python not found. Install Python 3.12 from python.org (check "Add python.exe to PATH") and run again.' }
    Write-Host "Python $v  -> route $route  (A = torch 2.3.1 like the paper era, B = latest torch)"

    # 2. venv + packages
    Step '2/6 Virtual environment + packages (first run downloads about 300 MB)'
    if (-not (Test-Path $VPy)) { & $pyExe @pyArgs -m venv $Venv; if ($LASTEXITCODE) { throw 'venv failed' } }
    & $VPy -m pip install --upgrade pip --quiet --disable-pip-version-check
    $common = @('setuptools<80', 'pandas', 'matplotlib', 'seaborn', 'pyyaml', 'requests', 'scipy', 'tqdm', 'pillow', 'psutil', 'filetype')
    if ($route -eq 'A') {
        $pkgs = @('torch==2.3.1', 'torchvision==0.18.1', 'numpy<2', 'opencv-python==4.10.0.84') + $common
    } else {
        $pkgs = @('torch', 'torchvision', 'numpy', 'opencv-python') + $common
    }
    & $VPy -m pip install @pkgs --quiet --disable-pip-version-check
    if ($LASTEXITCODE) { throw 'pip install failed. If your Python is 3.13 or newer, install Python 3.12 and run again.' }

    # 3. YOLOv5 at the pinned commit (zip, no git needed)
    Step '3/6 YOLOv5 (pinned 2022-09-11 commit)'
    if (-not (Test-Path (Join-Path $Yolo 'hubconf.py'))) {
        $zip = Join-Path $Base 'yolov5.zip'
        Get-Url "https://github.com/ultralytics/yolov5/archive/$YOLO_COMMIT.zip" $zip
        Expand-Archive -Path $zip -DestinationPath $Base -Force -ErrorAction Stop
        if (Test-Path $Yolo) { Remove-Item -Recurse -Force $Yolo }
        Rename-Item (Join-Path $Base "yolov5-$YOLO_COMMIT") 'yolov5' -ErrorAction Stop
        Remove-Item $zip
    }

    # 4. VespAI weights + example frames (only the files we need)
    Step '4/6 VespAI weights and example frames'
    $w = Join-Path $Data 'models\yolov5-params\yolov5s-all-data.pt'
    Get-Url "$RAW_VESPAI/models/yolov5-params/yolov5s-all-data.pt" $w
    $hash = (Get-FileHash $w -Algorithm SHA256).Hash
    if ($hash -ne $WEIGHTS_SHA) { Remove-Item $w; throw "Weights hash mismatch ($hash). File deleted, NOT loaded." }
    Write-Host 'weights SHA-256 OK'
    $ex = 'images/example-detections'
    foreach ($sp in @(@{n='velutina'; k=15}, @{n='crabro'; k=6})) {
        foreach ($i in 1..$sp.k) {
            foreach ($pair in @(@('frames', 'jpeg'), @('labels', 'txt'))) {
                $rel = "$ex/$($sp.n)/$($pair[0])/frame-$i.$($pair[1])"
                Get-Url "$RAW_VESPAI/$rel" (Join-Path $Data ($rel -replace '/', '\'))
            }
        }
    }

    # 5. Team script (always refresh)
    Step '5/6 Team run script'
    $runner = Join-Path $Base 'run_vespai_examples.py'
    if (Test-Path $runner) { Remove-Item $runner }
    Get-Url $RAW_TEAM $runner

    # 6. Run
    Step '6/6 Run detection'
    $env:YOLOv5_AUTOINSTALL = 'False'      # stop YOLOv5 from pip-installing things by itself
    $env:PYTHONIOENCODING = 'utf-8'
    if ($route -eq 'B') { $env:TORCH_FORCE_NO_WEIGHTS_ONLY_LOAD = '1' }   # torch >= 2.6 + 2022 YOLOv5
    & $VPy $runner $Yolo $w (Join-Path $Data ($ex -replace '/', '\')) $Out
    if ($LASTEXITCODE) { throw 'Detection script failed - see the error above.' }

    Write-Host ''
    Write-Host 'DONE. Send these 2 files to Claude (drag into the chat):' -ForegroundColor Green
    Write-Host "  $(Join-Path $Out 'summary.txt')"
    Write-Host "  $(Join-Path $Out 'result.tsv')"
    Start-Process explorer.exe $Out
}
catch {
    Write-Host ''
    Write-Host "FAILED: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host "Send this file to Claude: $(Join-Path $Base 'j1_log.txt')"
}
finally {
    Stop-Transcript | Out-Null
}

# run_all.ps1 — 펌웨어 시뮬레이션 빌드 + 실행 (서현 CAP-AI-43)
# 사용: PowerShell 에서  .\run_all.ps1      (zig 가 없으면: winget install zig.zig)
# 결과: 두 시뮬레이터 모두 FAIL 0 이면 종료 코드 0
$ErrorActionPreference = "Continue"   # Stop 이면 컴파일러 경고(stderr)도 오류로 처리됨 (PowerShell 5.1)
$here = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $here
$zig = (Get-Command zig -ErrorAction SilentlyContinue).Source
if (-not $zig) { $zig = (Get-ChildItem "$env:LOCALAPPDATA\Microsoft\WinGet\Packages" -Recurse -Filter zig.exe -ErrorAction SilentlyContinue | Select-Object -First 1).FullName }
if (-not $zig) { throw "zig 를 못 찾음. winget install zig.zig 후 PowerShell 을 새로 여세요." }
[Console]::OutputEncoding = [Text.Encoding]::UTF8
$bad = 0
foreach ($n in "sim_motion", "sim_doors") {
  Write-Host "=== 빌드 $n"
  & $zig c++ -std=c++17 -Wall -Wextra -Wno-unused-function -Wno-unused-variable -I. "$n.cpp" -o "$n.exe"
  if ($LASTEXITCODE -ne 0) { throw "$n 빌드 실패" }
  & ".\$n.exe"
  if ($LASTEXITCODE -ne 0) { $bad++ }
}
if ($bad) { Write-Host "`n실패한 시뮬레이터 $bad 개"; exit 1 } else { Write-Host "`n모두 통과" }

<#
.SYNOPSIS
  Run ai_inspect.jsx in Adobe Illustrator (Windows) for one or more .ai files.

.EXAMPLE
  pwsh run_illustrator.ps1 -Path "D:\work\logo.ai","D:\work\pack.ai" -Out "D:\case\ai" -Scale 100

  Exports every artboard as PNG and writes <stem>.illustrator.json per file:
  artboard names and sizes, layers, fonts, spot colours, linked files (with
  broken-link check), and text. Never saves any document.

  If Illustrator is already running, files the user has open are left open;
  only files this script opened are closed, and Illustrator is not quit.
  If this script launched Illustrator, it quits it afterwards.
#>
param(
  [Parameter(Mandatory)][string[]]$Path,
  [Parameter(Mandatory)][string]$Out,
  [int]$Scale = 100
)
$ErrorActionPreference = "Stop"
$jsx = Join-Path $PSScriptRoot "ai_inspect.jsx"
New-Item -ItemType Directory -Force -Path $Out | Out-Null
$outDir = (Resolve-Path $Out).Path -replace '\\', '/'

$wasRunning = [bool](Get-Process -Name Illustrator -ErrorAction SilentlyContinue)

function Connect-Illustrator {
  for ($try = 1; $try -le 3; $try++) {
    try { return New-Object -ComObject Illustrator.Application }
    catch {
      # A previous instance may still be shutting down (CO_E_SERVER_EXEC_FAILURE).
      Write-Warning "Illustrator did not respond (attempt $try): $($_.Exception.Message)"
      $deadline = (Get-Date).AddSeconds(60)
      while ((Get-Process -Name Illustrator -ErrorAction SilentlyContinue) -and -not $wasRunning -and (Get-Date) -lt $deadline) {
        Start-Sleep -Seconds 2
      }
    }
  }
  throw "Could not start or attach to Illustrator. Is it installed and licensed?"
}

$ai = Connect-Illustrator
try {
  foreach ($p in $Path) {
    $full = (Resolve-Path $p).Path -replace '\\', '/'
    $res = $ai.DoJavaScriptFile($jsx, [object[]]@($full, $outDir, "$Scale"), 1)
    $res
  }
}
finally {
  if (-not $wasRunning -and $ai.Documents.Count -eq 0) {
    $ai.Quit()
    # Illustrator takes a few seconds to exit; wait so a follow-up run can launch cleanly.
    $deadline = (Get-Date).AddSeconds(30)
    while ((Get-Process -Name Illustrator -ErrorAction SilentlyContinue) -and (Get-Date) -lt $deadline) { Start-Sleep -Milliseconds 500 }
  }
}

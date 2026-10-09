# DEMANDER UNIVERSAL Windows launcher — requires Python 3.11+
$ErrorActionPreference = 'Stop'
Set-Location -LiteralPath $PSScriptRoot
Write-Host 'DEMANDER UNIVERSAL v0.3.0-alpha // DPC-1' -ForegroundColor Cyan
python -m demander inspect .
if ($LASTEXITCODE -ne 0) { throw 'Inspection failed' }
Write-Host 'Executing built-in Demander verification tests from this trusted bundle.' -ForegroundColor Yellow
python -m demander verify . --contract examples/demander.contract.json --execute
if ($LASTEXITCODE -ne 0) { throw "Verification reported non-QUALIFIED status: $LASTEXITCODE" }
python -m demander report .demander/latest/receipt.json
Write-Host "Receipt: $PSScriptRoot\.demander\latest\receipt.json" -ForegroundColor Green

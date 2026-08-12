$ErrorActionPreference = "Stop"

$runner = Join-Path $PSScriptRoot "kh-lab.py"

if (Get-Command py -ErrorAction SilentlyContinue) {
    & py -3 $runner @args
    exit $LASTEXITCODE
}

if (Get-Command python -ErrorAction SilentlyContinue) {
    & python $runner @args
    exit $LASTEXITCODE
}

Write-Error "Python 3 is required to run Knowledge Hub interactive labs."
exit 2

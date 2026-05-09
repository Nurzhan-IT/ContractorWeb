# build_tailwind.ps1 — Compile Tailwind CSS for production
# Run this whenever you add new Tailwind classes to templates or JS files.
# The compiled output (static/css/tailwind.css) must be committed to git.

$binary = Join-Path $PSScriptRoot "tailwindcss.exe"
$downloadUrl = "https://github.com/tailwindlabs/tailwindcss/releases/download/v3.4.19/tailwindcss-windows-x64.exe"

if (-not (Test-Path $binary)) {
    Write-Host "Tailwind CLI not found. Downloading v3.4.19..."
    Invoke-WebRequest -Uri $downloadUrl -OutFile $binary
    Write-Host "Downloaded."
}

Set-Location $PSScriptRoot
& $binary -i static/css/tailwind_input.css -o static/css/tailwind.css --minify

if ($LASTEXITCODE -eq 0) {
    $size = [math]::Round((Get-Item "static/css/tailwind.css").Length / 1KB, 1)
    Write-Host "Done. Output: static/css/tailwind.css ($size KB)"
} else {
    Write-Host "Build failed (exit code $LASTEXITCODE)" -ForegroundColor Red
    exit 1
}

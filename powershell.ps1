# Navigate to the ui folder and run bun build
Set-Location -Path "ui" -ErrorAction Stop

bun install

bun run build

# Check if bun build was successful
if ($LASTEXITCODE -ne 0) {
    Write-Error "bun build failed"
    exit 1
}

# Navigate back to the original directory
Set-Location -Path ".."

# Run poetry install in the current folder
poetry install

# Check if poetry install was successful
if ($LASTEXITCODE -ne 0) {
    Write-Error "poetry install failed"
    exit 1
}

Write-Output "Build and installation completed successfully."
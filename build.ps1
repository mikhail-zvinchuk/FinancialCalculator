# PowerShell equivalent of build.sh

# Error handling function
function Test-LastExitCode {
    param (
        [string]$ErrorMessage
    )
    if ($LASTEXITCODE -ne 0) {
        Write-Error $ErrorMessage
        exit $LASTEXITCODE
    }
}

# Navigate to the ui folder
try {
    Push-Location .\ui
    Write-Host "Changed directory to ui"
} catch {
    Write-Error "Failed to change directory to ui"
    exit 1
}

# Install and build UI dependencies
Write-Host "Installing UI dependencies..."
bun install
Test-LastExitCode "bun install failed"

Write-Host "Building UI..."
bun run build
Test-LastExitCode "bun build failed"

# Navigate back to the original directory
Pop-Location
Write-Host "Changed back to root directory"

# Run poetry install in the current folder
Write-Host "Installing Python dependencies..."
poetry install
Test-LastExitCode "poetry install failed"

Write-Host "Build and installation completed successfully." -ForegroundColor Green 
# PowerShell script to start the application

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

# Function to start the Flask backend
function Start-FlaskBackend {
    Write-Host "Starting Flask backend..." -ForegroundColor Cyan
    
    # Activate virtual environment if it exists, create if it doesn't
    if (-not (Test-Path ".venv")) {
        Write-Host "Creating virtual environment..." -ForegroundColor Yellow
        python -m venv .venv
        Test-LastExitCode "Failed to create virtual environment"
    }
    
    # Activate virtual environment
    .\.venv\Scripts\Activate
    
    # Set Flask environment variables
    $env:FLASK_APP = "app.py"
    $env:FLASK_DEBUG = "1"
    $env:PYTHONUNBUFFERED = "1"  # Ensure Python output is not buffered
    
    # Start Flask in a new window with debug mode enabled
    Start-Process powershell -ArgumentList "-NoExit", "-Command", {
        .\.venv\Scripts\Activate
        Write-Host "Starting Flask server..." -ForegroundColor Green
        python -u app.py  # -u flag ensures unbuffered output
    }
}

# Function to start the Vue frontend
function Start-VueFrontend {
    Write-Host "Starting Vue frontend..." -ForegroundColor Cyan
    
    try {
        Push-Location .\ui
        
        # Start the development server in a new window
        Start-Process powershell -ArgumentList "-NoExit", "-Command", {
            Write-Host "Starting Vue development server..." -ForegroundColor Green
            npm run dev
        }
        
        Pop-Location
    } catch {
        Write-Error "Failed to start Vue frontend"
        exit 1
    }
}

# Main execution
Write-Host "Starting Financial Calculator application..." -ForegroundColor Magenta

# Start backend
Start-FlaskBackend

# Give the backend a moment to start
Start-Sleep -Seconds 2

# Start frontend
Start-VueFrontend

Write-Host "Both services have been started. You can access the application at http://localhost:5173" -ForegroundColor Green
Write-Host "Press Ctrl+C in the respective windows to stop the services." -ForegroundColor Yellow 
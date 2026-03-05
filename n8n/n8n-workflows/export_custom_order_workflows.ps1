# Extract-CakeOrderWorkflows.ps1
$InputFile = Join-Path $PSScriptRoot "n8n_exports\all_workflows.json"
$OutputFile = Join-Path $PSScriptRoot "Cake_Order_Manager_Workflows.json"

if (Test-Path $InputFile) {
    Write-Host "Processing all_workflows.json..." -ForegroundColor Cyan
    
    # Load JSON and filter for the prefix
    $RawData = Get-Content -Raw -Path $InputFile | ConvertFrom-Json
    $Filtered = $RawData | Where-Object { $_.name -like "Cake Order Manager*" }

    if ($Filtered.Count -gt 0) {
        # Export with high depth to preserve nested n8n node parameters
        $Filtered | ConvertTo-Json -Depth 100 | Set-Content -Path $OutputFile
        Write-Host "Success: $($Filtered.Count) workflows extracted to $OutputFile" -ForegroundColor Green
    } else {
        Write-Warning "No workflows found matching the prefix 'Cake Order Manager'."
    }
} else {
    Write-Error "File 'all_workflows.json' not found in the current directory."
}
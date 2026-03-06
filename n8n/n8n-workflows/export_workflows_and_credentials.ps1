# Export-N8n.ps1
$OutputDir     = Join-Path $PSScriptRoot "n8n_exports"
$ContainerName = "n8n_app"
$ContainerPath = "/home/node/.n8n-files/workflows/n8n_exports"

New-Item -ItemType Directory -Force -Path $OutputDir | Out-Null

Write-Host "Exporting workflows..."
docker exec $ContainerName n8n export:workflow --all --output=$ContainerPath/all_workflows.json
if ($LASTEXITCODE -ne 0) { Write-Error "Workflow export failed."; exit 1 }

Write-Host "Exporting credentials..."
docker exec $ContainerName n8n export:credentials --all --decrypted --output=$ContainerPath/all_credentials.json
if ($LASTEXITCODE -ne 0) { Write-Error "Credentials export failed."; exit 1 }

Write-Host "Copying files from container..."
docker cp "${ContainerName}:${ContainerPath}/all_workflows.json"   (Join-Path $OutputDir "all_workflows.json")
docker cp "${ContainerName}:${ContainerPath}/all_credentials.json" (Join-Path $OutputDir "all_credentials.json")


Write-Host "Done. Files saved to: $OutputDir"
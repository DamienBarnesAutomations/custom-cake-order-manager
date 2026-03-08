# Export-N8n.ps1
$OutputDir     = Join-Path $PSScriptRoot "n8n_exports"
$SplitDir      = Join-Path $OutputDir "workflows"
$ContainerName = "n8n_app"
$ContainerPath = "/home/node/.n8n-files/workflows/n8n_exports"

New-Item -ItemType Directory -Force -Path $OutputDir | Out-Null
New-Item -ItemType Directory -Force -Path $SplitDir  | Out-Null

# ---- Export all_workflows.json and all_credentials.json from container ----
Write-Host "Exporting workflows..."
docker exec $ContainerName n8n export:workflow --all --output=$ContainerPath/all_workflows.json
if ($LASTEXITCODE -ne 0) { Write-Error "Workflow export failed."; exit 1 }

Write-Host "Exporting credentials..."
docker exec $ContainerName n8n export:credentials --all --decrypted --output=$ContainerPath/all_credentials.json
if ($LASTEXITCODE -ne 0) { Write-Error "Credentials export failed."; exit 1 }

# ---- Write the Node.js splitter script to a temp file and copy into container ----
$tempScript = Join-Path $env:TEMP "n8n_split.js"
$utf8NoBom  = [System.Text.UTF8Encoding]::new($false)

[System.IO.File]::WriteAllText($tempScript, @'
const fs   = require('fs');
const path = require('path');

const exportDir = '/home/node/.n8n-files/workflows/n8n_exports';
const splitDir  = path.join(exportDir, 'workflows');

if (!fs.existsSync(splitDir)) fs.mkdirSync(splitDir, { recursive: true });

fs.readdirSync(splitDir)
  .filter(f => f.endsWith('.json'))
  .forEach(f => fs.unlinkSync(path.join(splitDir, f)));

const workflows = JSON.parse(fs.readFileSync(path.join(exportDir, 'all_workflows.json'), 'utf8'));

let saved = 0;
for (const wf of workflows) {
  const name = wf.name;
  delete wf.versionCounter;

  const safeName = name
    .replace(/[\\/:*?"<>|]/g, '_')
    .trim()
    .replace(/\s+/g, '_');

  const outFile = path.join(splitDir, safeName + '.json');
  fs.writeFileSync(outFile, JSON.stringify(wf, null, 4), 'utf8');
  console.log('  Saved: ' + safeName + '.json');
  saved++;
}

console.log('\nDone. ' + saved + ' workflows split.');
'@, $utf8NoBom)

Write-Host "Splitting workflows inside container..."
docker cp $tempScript "${ContainerName}:/tmp/n8n_split.js"
docker exec $ContainerName node /tmp/n8n_split.js
if ($LASTEXITCODE -ne 0) { Write-Error "Splitting failed."; exit 1 }

# ---- Copy the already-split files out of the container ----
Write-Host "Copying files from container..."
docker cp "${ContainerName}:${ContainerPath}/all_workflows.json"   (Join-Path $OutputDir "all_workflows.json")
docker cp "${ContainerName}:${ContainerPath}/all_credentials.json" (Join-Path $OutputDir "all_credentials.json")
docker cp "${ContainerName}:${ContainerPath}/workflows/."          $SplitDir

Write-Host "`nDone. Workflows saved to: $SplitDir"
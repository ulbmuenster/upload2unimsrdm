### Bulk Upload: Uploading Multiple Subfolders

Upload each subfolder of a directory as a separate zipped dataset:

```bash
#!/bin/bash

# Set your token (or use .env file)
export INVENIORDM_TOKEN="your-api-token"

# Directory containing subfolders to upload
BASE_DIR="/path/to/parent/folder"

# Loop through each subfolder
for folder in "$BASE_DIR"/*/ ; do
  # Get the folder name (without path)
  folder_name=$(basename "$folder")
  
  echo "Uploading: $folder_name"
  
  # Upload the folder as a zipped dataset
  upload2unimsrdm \
    --system datastore \
    --title "$folder_name" \
    --files "$folder" \
    --zip-directory \
    --description "Dataset: $folder_name"
  
  echo "Completed: $folder_name"
  echo "---"
done

echo "All uploads completed!"
```

You can also add more metadata in the loop:

```bash
for folder in "$BASE_DIR"/*/ ; do
  folder_name=$(basename "$folder")
  
  upload2unimsrdm \
    --system datastore \
    --title "$folder_name" \
    --files "$folder" \
    --zip-directory \
    --description "Automated upload of $folder_name dataset" \
    --keywords "batch-upload" --keywords "automated"
done
```

**Windows PowerShell equivalent:**

```powershell
# Set your token (or use .env file)
$env:INVENIORDM_TOKEN = "your-api-token"

# Directory containing subfolders to upload
$BASE_DIR = "C:\path\to\parent\folder"

# Loop through each subfolder
Get-ChildItem -Path $BASE_DIR -Directory | ForEach-Object {
  $folder_name = $_.Name
  $folder_path = $_.FullName
  
  Write-Host "Uploading: $folder_name"
  
  # Upload the folder as a zipped dataset
  upload2unimsrdm `
    --system datastore `
    --title "$folder_name" `
    --files "$folder_path" `
    --zip-directory `
    --description "Dataset: $folder_name"
  
  Write-Host "Completed: $folder_name"
  Write-Host "---"
}

Write-Host "All uploads completed!"
```

**Windows Command Prompt (cmd.exe) equivalent:**

```batch
@echo off
REM Set your token (or use .env file)
set INVENIORDM_TOKEN=your-api-token

REM Directory containing subfolders to upload
set BASE_DIR=C:\path\to\parent\folder

REM Loop through each subfolder
for /D %%F in ("%BASE_DIR%\*") do (
  echo Uploading: %%~nxF
  
  upload2unimsrdm ^
    --system datastore ^
    --title "%%~nxF" ^
    --files "%%F" ^
    --zip-directory ^
    --description "Dataset: %%~nxF"
  
  echo Completed: %%~nxF
  echo ---
)

echo All uploads completed!
```
## Quick Start

```bash
# Install with uv (recommended)
curl -LsSf https://astral.sh/uv/install.sh | sh
cd upload2unimsrdm
uv pip install -e .

# Upload your data
upload2unimsrdm --token YOUR_TOKEN --title "My Dataset" --system datastore --files /path/to/data
```

## Installation

### Option 1: Using uv (Recommended)

```bash
# Install uv if you don't have it
curl -LsSf https://astral.sh/uv/install.sh | sh

# Clone and install
git clone https://github.com/yourusername/upload2unimsrdm.git
cd upload2unimsrdm
uv pip install -e .
```

### Option 2: Using pip

```bash
git clone https://github.com/yourusername/upload2unimsrdm.git
cd upload2unimsrdm
pip install -e .
```

### Option 3: Standalone Executable

Download pre-built executables from the [Releases](../../releases) page, or build your own:

```bash
./build_executable.sh
# Executable will be in dist/upload2unimsrdm
```

## Usage


### Using Environment Variables

```bash
export INVENIORDM_TOKEN="your-api-token"

# Now you can omit the token
upload2unimsrdm --system datastore --title "My Data" --files /path/to/data
```

## How It Works

1. **Creates a draft** - Creates a new draft record via the InvenioRDM API
2. **Uploads files** - Uploads all files with progress tracking
3. **Returns URL** - Provides the draft URL for review and publishing

The tool follows the [InvenioRDM REST API](https://inveniordm.docs.cern.ch/reference/rest_api_drafts_records/) workflow:

- POST to `/api/records` to create a draft
- POST to `/api/records/{id}/draft/files` to initialize file uploads
- PUT to `/api/records/{id}/draft/files/{filename}/content` to upload content
- POST to `/api/records/{id}/draft/files/{filename}/commit` to finalize each file

## Building Standalone Executables

### Quick Build (Current Platform)

```bash
./build_executable.sh
```

### Manual Build

```bash
uv pip install pyinstaller
pyinstaller --onefile --name upload2unimsrdm src/upload2unimsrdm/cli.py
```

### Cross-Platform Builds

Build executables on each target platform:

- **Linux**: Run `./build_executable.sh` on Linux
- **macOS**: Run `./build_executable.sh` on macOS  
- **Windows**: Run `pyinstaller --onefile --name upload2unimsrdm.exe src\upload2unimsrdm\cli.py`


## Development

### Running Tests

```bash
uv pip install pytest pytest-cov
pytest
```

### Code Structure

The project is organized into focused modules:

- `cli.py` - Click-based command-line interface
- `uploader.py` - Main upload orchestration logic
- `api_client.py` - Low-level HTTP client for InvenioRDM
- `utils.py` - File collection and utility functions

## Documentation

- [API Documentation](https://inveniordm.docs.cern.ch/reference/rest_api_drafts_records/) - InvenioRDM REST API reference
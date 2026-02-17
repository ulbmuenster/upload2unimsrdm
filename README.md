# upload2unimsrdm

`upload2unimsrdm` is a command-line tool (so no graphical interface) for uploading data to the Uni Münster InvenioRDM-based repositories [**datasafe**](https://datasafe.uni-muenster.de) (archive, data is deleted after 10 years, only accessible from within the University network) and [**datastore**](https://datastore.uni-muenster.de) (FAIR, DOI registration, public).

## Disclaimer

This tool is provided without any warranties or guarantees (“as-is”). Use is at your own risk; in particular, data loss cannot be ruled out. Please contact your IT support team at the University of Münster if you need assistance with setup or operation. We cannot provide general support for operation, but we are happy to answer technical questions from technical contacts regarding use.

See [Advanced Usage.md](./Advanced%20Usage.md) and [Developer.md](./Developer.md) for further information.

## Installation

### Linux

1. Download the tool:
   - Either via browser: <https://github.com/ulbmuenster/upload2unimsrdm/releases>
   - Or via cURL/wget: `curl -L https://github.com/ulbmuenster/upload2unimsrdm/releases/download/0.1.0/upload2unimsrdm --output upload2unimsrdm`
2. Open a terminal and navigate to the folder where the file was downloaded, e.g., `cd $HOME/Downloads`
3. Make the file executable: `chmod +x upload2unimsrdm`
4. Run the tool: `./upload2unimsrdm`

Optional: Move the uploader to `/usr/bin` to make it accessible globally: `sudo mv upload2unimsrdm /usr/bin`

### Windows

1. Download the uploader: <https://github.com/ulbmuenster/upload2unimsrdm/releases/download/0.1.0/upload2unimsrdm.exe> and place it on the desktop.
2. Open the Start menu -> type `cmd` and open the command prompt.
3. Type `cd Desktop` and press <kbd>Enter</kbd>.
4. Test the tool by running: `upload2unimsrdm`
![](assets/1024-896.png)
5. Start the upload: Type `upload2unimsrdm --system`, followed by a space and the system to upload to, then a space and `--token`, followed by your API key (without `<>`, paste it via right-click or Ctrl+V), then a space followed by `--title` and the title you want the dataset to have, and then another space followed by `--files`. Here, you can simply drag and drop the file/folder into the window after a space. Confirm by pressing <kbd>Enter</kbd>.

## Usage

### Basic Usage

```bash
# Upload to datastore
upload2unimsrdm \
  --token "YOUR_TOKEN" \
  --system datastore \
  --title "My Data" \
  --files /path/to/data
```

**Important**: In order to proceed you need at least one creator and a publishing date. You always need to add the relevant metadata in the Web UI after uploading your data. The tool will set the current year if no publication date was passed (only possible via metadata file).

### Command-Line Arguments

#### Required

- `--token` - Your InvenioRDM API token (or set `INVENIORDM_TOKEN`)
- `--title` - Title for the draft record
- `--files` - Path to file or folder to upload
- `--system` - RDM repository to use: `datasafe` or `datastore`

> **Note:** The draft is created with default metadata. You can add more metadata (description, creators, keywords, etc.) through the web interface after the upload completes.

### Upload with Advanced Metadata

Add detailed metadata using CLI options:

```bash
upload2unimsrdm \
  --system datastore \
  --title "My Research Dataset" \
  --files data.csv \
  --description "A comprehensive dataset from our research" \
  --keywords physics --keywords experiment
```

Or use a complete metadata file:

```bash
upload2unimsrdm \
  --system datastore \
  --files data.csv \
  --metadata-file metadata.json
```

See [`metadata_example.json`](./metadata_example.json) for the full InvenioRDM metadata structure.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

MIT License - see [LICENSE](LICENSE) file for details.

## Acknowledgments

Built for the University of Münster's Research Data Management systems
based on the [InvenioRDM](https://inveniosoftware.org/products/rdm/) platform.

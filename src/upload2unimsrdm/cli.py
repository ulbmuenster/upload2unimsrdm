# -*- coding: utf-8 -*-
#
# Copyright (C) 2025 University of Münster.
#
# upload2unimsrdm is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

import sys
import click
import json
import yaml
from pathlib import Path
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table

# Use absolute imports for PyInstaller compatibility
try:
    from upload2unimsrdm.uploader import InvenioRDMUploader
    from upload2unimsrdm.utils import collect_files, format_size
    from upload2unimsrdm.utils import zip_directory as create_zip
    from upload2unimsrdm.conf import SYSTEMS
except ImportError:
    from .uploader import InvenioRDMUploader
    from .utils import collect_files, format_size
    from .utils import zip_directory as create_zip
    from .conf import SYSTEMS
from dotenv import load_dotenv, find_dotenv
import os

console = Console()


def get_help_text():
    """Generate dynamic help text with current system URLs."""
    return f"""Upload data to one of the research data repositories of University of Münster.

\b
To get an API token, visit:
  - datasafe:  {SYSTEMS["datasafe"]}/account/settings/applications/tokens/new/
  - datastore: {SYSTEMS["datastore"]}/account/settings/applications/tokens/new/

Basic usage:\n
  upload2unimsrdm --system datastore --token <YOUR_TOKEN> --title "My Data" --files "/path/to/file"\n
"""


@click.command(
    context_settings=dict(help_option_names=['-h', '--help']),
    help=get_help_text()
)
@click.option(
    "--token",
    envvar="INVENIORDM_TOKEN",
    required=False,
    help="API token for authentication. Can also be set via INVENIORDM_TOKEN environment variable. (required)",
)
@click.option(
    "--title",
    required=False,
    help="Title of the draft record (required)",
)
@click.option(
    "--files",
    required=False,
    type=click.Path(exists=True),
    help="Path to file or folder to upload (required)",
)
@click.option(
    "--system",
    required=False,
    show_choices=False,
    type=click.Choice(["datasafe", "datastore", "dev"], case_sensitive=False),
    help="RDM platform to use (required). Choices: datasafe, datastore.",
)
@click.option(
    "--zip-directory",
    is_flag=True,
    default=False,
    help="If input is a directory, zip it before uploading instead of uploading individual files",
)
@click.option(
    "--description",
    required=False,
    help="Description of the dataset",
)
@click.option(
    "--keywords",
    required=False,
    multiple=True,
    help="Keywords/subjects (can be specified multiple times, e.g., --keywords physics --keywords data)",
)
@click.option(
    "--metadata-file",
    required=False,
    type=click.Path(exists=True),
    hidden=True,
    help="JSON or YAML file with complete InvenioRDM metadata structure (overrides other metadata options)",
)
@click.pass_context
def main(ctx, token, title, files, system, zip_directory, description, keywords, metadata_file):
    try:
        # If no arguments provided at all, show help
        if not any([title, files, system, token]):
            console.print(ctx.get_help())
            sys.exit(0)

        # Check for missing required parameters
        missing = []
        if not title:
            missing.append("--title")
        if not files:
            missing.append("--files")
        if not system:
            missing.append("--system")

        if missing:
            console.print(f"\n[red]✗ Error:[/red] Missing required option(s): {', '.join(missing)}")
            console.print("\n[dim]Use --help to see all available options[/dim]")
            sys.exit(2)

        # Try to load .env

        env_file = find_dotenv(usecwd=True)
        if env_file:
            load_dotenv(env_file, override=False)
            console.print(f"[dim]Loaded .env from {env_file}[/dim]")

        if not token:
            token = os.environ.get("INVENIORDM_TOKEN")

        if not token:
            # if still no token, not via CLI or Env: show error
            console.print("\n[red]✗ Error:[/red] Missing option '--token'.")
            console.print("\n[yellow]To get an API token:[/yellow]")
            console.print(f"  • datasafe:  https://datasafe.uni-muenster.de/account/settings/applications/tokens/new/")
            console.print(f"  • datastore: https://datastore.uni-muenster.de/account/settings/applications/tokens/new/")
            console.print("\n[yellow]You can provide the token via:[/yellow]")
            console.print("  • Command line: --token YOUR_TOKEN")
            console.print("  • Environment variable: INVENIORDM_TOKEN=YOUR_TOKEN")
            console.print("  • .env file: INVENIORDM_TOKEN=YOUR_TOKEN")
            sys.exit(2)

        # Use the selected system
        base_url = SYSTEMS[system.lower()]
        # Disable SSL verification for dev (self-signed certificates)
        verify_ssl = system.lower() != "dev"

        # Initialize uploader
        uploader = InvenioRDMUploader(base_url=base_url, token=token, verify_ssl=verify_ssl)

        # Collect files to upload
        files_path = Path(files)
        zip_created = False
        temp_zip_path = None

        # Handle directory zipping if requested
        if zip_directory and files_path.is_dir():
            console.print(f"[cyan]Zipping directory: {files_path.name}. This can take some time![/cyan]")
            temp_zip_path = create_zip(files_path, output_name=files_path.name)
            console.print(f"[green]✓ Created zip file:[/green] {temp_zip_path.name} ({format_size(temp_zip_path.stat().st_size)})")
            file_list = [temp_zip_path]
            files_path = temp_zip_path
            zip_created = True
        else:
            file_list = collect_files(files_path)

        if not file_list:
            console.print("[red]✗ Error: No files found to upload[/red]")
            sys.exit(1)
        # if file list if >100 we cant upload it without zipping, so we show an error
        if len(file_list) > 100 and not zip_directory:
            console.print(f"[red]✗ Error: Found {len(file_list)} files. Uploading more than 100 files without zipping is not supported.[/red]")
            console.print("[yellow]Consider using the --zip-directory option to zip the folder before uploading.[/yellow]")
            sys.exit(1)
        console.print(f"[cyan]Found {len(file_list)} file(s) to upload[/cyan]")

        # Build metadata
        if metadata_file:
            # Load metadata from file
            console.print(f"[cyan]Loading metadata from: {metadata_file}[/cyan]")
            metadata = load_metadata_file(metadata_file)
        else:
            # Build metadata from CLI options
            metadata = build_metadata_from_options(
                title=title,
                description=description,
                keywords=keywords
            )

        # Create draft with progress spinner
        console.print("\n[bold cyan]Creating draft record...[/bold cyan]")
        with Progress(
            SpinnerColumn(),
            TextColumn("[bold cyan]Creating draft..."),
            transient=False
        ) as progress:
            progress.add_task("draft", total=None)
            draft_id, draft_url = uploader.create_draft(metadata, system)
        console.print(f"[green]✓ Draft created:[/green] [bold]{draft_id}[/bold]")

        # Upload files
        console.print("\n[bold cyan]Uploading files...[/bold cyan]")
        uploader.upload_files(draft_id, file_list, files_path)

        # Clean up temporary zip file if created
        if zip_created and temp_zip_path and temp_zip_path.exists():
            temp_zip_path.unlink()
            console.print(f"[dim]Cleaned up temporary zip file[/dim]")

        # Success!
        success_panel = Panel(
            f"[green]✓ Upload completed successfully![/green]\n\n"
            f"[bold]Draft URL:[/bold] [link={draft_url}]{draft_url}[/link]\n\n"
            f"[yellow]You can now:[/yellow]\n"
            f"  1. Review your draft in the web interface\n"
            f"  2. Add more metadata if needed\n"
            f"  3. Publish the record when ready",
            title="[bold green]Success[/bold green]",
            border_style="green",
            expand=False
        )
        console.print("\n")
        console.print(success_panel)

    except KeyboardInterrupt:
        console.print("\n\n[yellow]Upload cancelled by user[/yellow]")
        sys.exit(1)
    except click.exceptions.MissingParameter as e:
        if '--token' in str(e):
            console.print(f"\n[red]✗ Error:[/red] {e}")
            console.print("\n[yellow]To get an API token:[/yellow]")
            console.print(f"  • datasafe:  https://datasafe.uni-muenster.de/account/settings/applications/tokens/new/")
            console.print(f"  • datastore: https://datastore.uni-muenster.de/account/settings/applications/tokens/new/")
        else:
            console.print(f"\n[red]✗ Error:[/red] {e}")
        sys.exit(1)
    except Exception as e:
        console.print(f"\n[red]✗ Error:[/red] {e}")
        sys.exit(1)


def load_metadata_file(filepath: str) -> dict:
    """Load metadata from JSON or YAML file.

    Args:
        filepath: Path to metadata file

    Returns:
        Dictionary with metadata
    """
    path = Path(filepath)

    with open(path, 'r') as f:
        if path.suffix.lower() in ['.json']:
            return json.load(f)
        elif path.suffix.lower() in ['.yaml', '.yml']:
            try:
                return yaml.safe_load(f)
            except ImportError:
                raise RuntimeError("Error loading YAML file.")
        else:
            raise ValueError(f"Unsupported metadata file format: {path.suffix}. Use .json or .yaml")


def build_metadata_from_options(title: str, description: str = None, keywords: tuple = None) -> dict:
    """Build InvenioRDM metadata from CLI options.

    Args:
        title: Title of the record
        description: Description text
        keywords: Tuple of keyword strings

    Returns:
        Dictionary with InvenioRDM metadata structure
    """
    metadata = {
        "title": title,
    }

    # Add description if provided
    if description:
        metadata["description"] = description

    # Add keywords/subjects if provided
    if keywords:
        metadata["subjects"] = [{"subject": kw} for kw in keywords]

    return metadata


if __name__ == "__main__":
    main()

# -*- coding: utf-8 -*-
#
# Copyright (C) 2025 University of Münster.
#
# upload2unimsrdm is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

from pathlib import Path
from typing import List
import zipfile
import tempfile
from rich.progress import Progress, BarColumn, TextColumn


def collect_files(path: Path) -> List[Path]:
    """Collect all files from a path (file or directory).

    Args:
        path: Path to a file or directory

    Returns:
        List of file paths
    """
    if path.is_file():
        return [path]
    elif path.is_dir():
        # Recursively collect all files
        files = []
        for item in path.rglob('*'):
            if item.is_file():
                # Skip hidden files and common unwanted files
                if not item.name.startswith('.') and item.name not in ['__pycache__', '.DS_Store']:
                    files.append(item)
        return sorted(files)
    else:
        return []


def format_size(size_bytes: int) -> str:
    """Format file size in human-readable format.

    Args:
        size_bytes: Size in bytes

    Returns:
        Formatted size string
    """
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.1f} PB"


def zip_directory(directory: Path, output_name: str = None) -> Path:
    """Create a zip file from a directory.

    Args:
        directory: Path to the directory to zip
        output_name: Optional name for the zip file (without .zip extension).
                    If not provided, uses the directory name.

    Returns:
        Path to the created zip file
    """
    if not directory.is_dir():
        raise ValueError(f"Path {directory} is not a directory")

    # Determine output filename
    if output_name is None:
        output_name = directory.name

    # Create zip file in a temporary directory
    temp_dir = Path(tempfile.gettempdir())
    zip_path = temp_dir / f"{output_name}.zip"

    # Remove existing zip file if it exists
    if zip_path.exists():
        zip_path.unlink()

    # First, collect all files to get a count for the progress bar
    files_to_zip = []
    for item in directory.rglob('*'):
        if item.is_file():
            # Skip hidden files and common unwanted files
            if not item.name.startswith('.') and item.name not in ['__pycache__', '.DS_Store']:
                files_to_zip.append(item)

    # Create the zip file with progress tracking
    with Progress(
        TextColumn("[bold blue]{task.fields[status]}", justify="left"),
        BarColumn(bar_width=None),
        "[progress.percentage]{task.percentage:>3.1f}%",
    ) as progress:
        task_id = progress.add_task("Zipping...", status=f"Zipping {len(files_to_zip)} files", total=len(files_to_zip))
        
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for item in files_to_zip:
                # Add file with relative path from the directory
                arcname = item.relative_to(directory)
                zipf.write(item, arcname)
                progress.update(task_id, advance=1)

    return zip_path

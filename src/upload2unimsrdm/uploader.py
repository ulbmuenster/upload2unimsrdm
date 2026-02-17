# -*- coding: utf-8 -*-
#
# Copyright (C) 2025 University of Münster.
#
# upload2unimsrdm is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

import base64
import hashlib
from pathlib import Path
from rich.progress import Progress, BarColumn, DownloadColumn, TransferSpeedColumn, TimeRemainingColumn, TextColumn
from typing import Dict, List, Tuple
import requests

# Use absolute imports for PyInstaller compatibility
try:
    from upload2unimsrdm.api_client import InvenioRDMClient
except ImportError:
    from .api_client import InvenioRDMClient
from datetime import datetime


class InvenioRDMUploader:
    """Handles uploading data to InvenioRDM repositories."""

    # Default part size for multipart uploads (100 MB)
    DEFAULT_PART_SIZE = 100 * 1024 * 1024

    def __init__(self, base_url: str, token: str, verify_ssl: bool = True, part_size: int = None):
        """Initialize the uploader.

        Args:
            base_url: Base URL of the InvenioRDM instance
            token: API authentication token
            verify_ssl: Whether to verify SSL certificates (default: True)
            part_size: Size of each part for multipart uploads (default: 100 MB)
        """
        self.client = InvenioRDMClient(base_url, token, verify_ssl=verify_ssl)
        self.part_size = part_size or self.DEFAULT_PART_SIZE
        self.verify_ssl = verify_ssl

    def create_draft(self, metadata: Dict, system: str) -> Tuple[str, str]:
        """Create a new draft record.

        Args:
            metadata: Dictionary containing metadata fields (title, description, etc.)
            system: The system being used (datasafe, datastore, or dev)

        Returns:
            Tuple of (draft_id, draft_url)
        """
        # Build the metadata structure required by InvenioRDM
        # If metadata has complete InvenioRDM structure (from file), use it directly
        if "metadata" in metadata and "access" in metadata:
            # Complete metadata structure from file
            draft_data = metadata
        else:
            # Build from simplified metadata structure
            pub_date = metadata.get("publication_date")
            if pub_date is None or str(pub_date).strip() == "":
                pub_date = str(datetime.now().year)
            else:
                pub_date = str(pub_date)

            rdm_metadata = {
                "title": metadata.get("title", "Untitled"),
                "resource_type": {"id": metadata.get("resource_type", "dataset")},
                "publication_date": pub_date,
                "publisher": "Universität Münster",
            }

            # Add optional fields if provided
            if "description" in metadata:
                rdm_metadata["description"] = metadata["description"]

            if "subjects" in metadata:
                rdm_metadata["subjects"] = metadata["subjects"]

            if "rights" in metadata:
                rdm_metadata["rights"] = metadata["rights"]

            # Handle creators - only add if provided in metadata
            if "creators" in metadata:
                rdm_metadata["creators"] = metadata["creators"]

            draft_data = {
                "access": {
                    "record": "restricted" if system == "datasafe" else "public",
                    "files": "restricted" if system == "datasafe" else "public"
                },
                "files": {
                    "enabled": True
                },
                "metadata": rdm_metadata
            }

        response = self.client.post("/api/records", json=draft_data)

        # Validate response structure
        if not isinstance(response, dict):
            raise RuntimeError(f"Unexpected response when creating draft: {response!r}")

        if "id" not in response or "links" not in response or "self_html" not in response.get("links", {}):
            # Provide response contents to help debugging (may be HTML or error text)
            raise RuntimeError(f"Unexpected or invalid draft response: {response!r}")

        draft_id = response["id"]
        draft_url = response["links"]["self_html"]

        return draft_id, draft_url

    def upload_files(self, draft_id: str, files: List[Path], base_path: Path):
        """Upload files to the draft record with multipart upload and progress tracking.

        Args:
            draft_id: ID of the draft record
            files: List of file paths to upload
            base_path: Base path for computing relative paths
        """
        # Step 1: Initialize all files with multipart transfer metadata
        files_to_initialize = []
        for file_path in files:
            filename = self._get_relative_path(file_path, base_path)
            file_size = file_path.stat().st_size

            # Calculate number of parts
            number_of_parts = file_size // self.part_size
            if file_size % self.part_size > 0:
                number_of_parts += 1

            files_to_initialize.append({
                "key": filename,
                "size": file_size,
                "metadata": {
                    "description": "Uploaded file.",
                },
                "transfer": {
                    "type": "M",
                    "parts": number_of_parts,
                    "part_size": self.part_size,
                },
            })

        # Initialize all files at once
        init_response = self.client.post(
            f"/api/records/{draft_id}/draft/files",
            json=files_to_initialize
        )

        # Step 2: Upload file content with progress tracking
        with Progress(
            TextColumn("[bold blue]{task.fields[filename]}", justify="right"),
            BarColumn(bar_width=None),
            "[progress.percentage]{task.percentage:>3.1f}%",
            "•",
            DownloadColumn(),
            "•",
            TransferSpeedColumn(),
            "•",
            TimeRemainingColumn(),
        ) as progress:
            for file_path in files:
                filename = self._get_relative_path(file_path, base_path)

                # Find the corresponding entry in the response
                file_entry = None
                for entry in init_response.get("entries", []):
                    if entry["key"] == filename:
                        file_entry = entry
                        break

                if not file_entry:
                    raise RuntimeError(f"File entry not found for {filename}")

                # Upload with multipart if needed
                task_id = progress.add_task("upload", filename=filename, total=file_path.stat().st_size)
                self._upload_multipart_file(draft_id, file_path, file_entry, progress, task_id)

    def _upload_multipart_file(self, draft_id: str, file_path: Path, file_entry: Dict, progress: Progress, task_id):
        """Upload a single file using multipart upload to S3 with progress tracking.

        Args:
            draft_id: ID of the draft record
            file_path: Path to the file to upload
            file_entry: File entry metadata from initialization response
            progress: Rich progress instance
            task_id: Task ID for progress tracking
        """
        filename = file_entry["key"]
        file_size = file_entry["size"]
        part_size = file_entry["transfer"]["part_size"]
        number_of_parts = file_entry["transfer"]["parts"]
        parts = file_entry["links"]["parts"]

        # Upload each part directly to S3
        with open(file_path, 'rb') as f:
            for part_info in parts:
                part_no = part_info["part"]
                part_url = part_info["url"]

                # Calculate the size of this part
                if part_no < number_of_parts:
                    size_of_part = part_size
                elif part_no == number_of_parts and file_size % part_size == 0:
                    size_of_part = part_size
                else:
                    size_of_part = file_size % part_size

                # Seek to the correct position and read the part
                f.seek((part_no - 1) * part_size)
                part_content = f.read(size_of_part)

                # Calculate MD5 checksum for the part
                part_checksum = base64.b64encode(
                    hashlib.md5(part_content).digest()
                ).decode('utf-8')

                # Upload the part directly to S3
                response = requests.put(
                    part_url,
                    data=part_content,
                    headers={
                        "Content-Length": str(size_of_part),
                        "Content-MD5": part_checksum,
                    },
                    verify=self.verify_ssl
                )

                if response.status_code != 200:
                    raise RuntimeError(f"Failed to upload part {part_no}: {response.text}")

                # Update progress
                progress.update(task_id, advance=len(part_content))

        # Commit the file upload
        self.client.post(f"/api/records/{draft_id}/draft/files/{filename}/commit")

    def _get_relative_path(self, file_path: Path, base_path: Path) -> str:
        """Get relative path for a file.

        Args:
            file_path: Full path to the file
            base_path: Base path to compute relative path from

        Returns:
            Relative path as string
        """
        if base_path.is_file():
            # If base is a file, just return the filename
            return file_path.name
        else:
            # If base is a directory, return relative path
            try:
                return str(file_path.relative_to(base_path))
            except ValueError:
                # If file is not relative to base, just return name
                return file_path.name

# -*- coding: utf-8 -*-
#
# Copyright (C) 2025 University of Münster.
#
# upload2unimsrdm is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

import requests
import urllib3
from typing import Dict, Optional


class InvenioRDMClient:
    """HTTP client for InvenioRDM REST API."""

    def __init__(self, base_url: str, token: str, verify_ssl: bool = True):
        """Initialize the API client.

        Args:
            base_url: Base URL of the InvenioRDM instance
            token: API authentication token
            verify_ssl: Whether to verify SSL certificates (default: True)
        """
        self.base_url = base_url.rstrip('/')
        self.verify_ssl = verify_ssl
        self.session = requests.Session()
        self.session.headers.update({
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json',
        })

        # Disable SSL warnings for dev environments
        if not verify_ssl:
            urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

    def post(self, endpoint: str, json: Optional[Dict] = None, **kwargs) -> Dict:
        """Make a POST request.

        Args:
            endpoint: API endpoint path
            json: JSON data to send
            **kwargs: Additional arguments for requests

        Returns:
            Response JSON

        Raises:
            requests.HTTPError: If request fails
        """
        url = f"{self.base_url}{endpoint}"
        response = self.session.post(url, json=json, verify=self.verify_ssl, **kwargs)

        # Handle authentication errors with friendly messages
        if response.status_code in (401, 403):
            raise requests.HTTPError(
                f"Authentication failed: Your API token is likely wrong or missing. "
                f"Please check your token and try again.",
                response=response
            )

        response.raise_for_status()
        # Some endpoints may return empty or non-JSON responses (e.g. HTML error pages).
        if not response.content:
            return {}
        try:
            return response.json()
        except ValueError as e:
            # Include response text to help debugging when the server returns non-JSON
            raise RuntimeError(
                f"Failed to parse JSON response from {url} (status {response.status_code}): {response.text!r}"
            ) from e

    def put(self, endpoint: str, data=None, headers: Optional[Dict] = None, **kwargs) -> Dict:
        """Make a PUT request.

        Args:
            endpoint: API endpoint path
            data: Data to send (for file uploads)
            headers: Additional headers
            **kwargs: Additional arguments for requests

        Returns:
            Response JSON

        Raises:
            requests.HTTPError: If request fails
        """
        url = f"{self.base_url}{endpoint}"

        # Merge headers
        req_headers = self.session.headers.copy()
        if headers:
            req_headers.update(headers)

        response = self.session.put(url, data=data, headers=req_headers, verify=self.verify_ssl, **kwargs)

        # Handle authentication errors with friendly messages
        if response.status_code in (401, 403):
            raise requests.HTTPError(
                f"Authentication failed: Your API token is likely wrong or missing. "
                f"Please check your token and try again.",
                response=response
            )

        response.raise_for_status()
        if not response.content:
            return {}
        try:
            return response.json()
        except ValueError as e:
            raise RuntimeError(
                f"Failed to parse JSON response from {url} (status {response.status_code}): {response.text!r}"
            ) from e

    def get(self, endpoint: str, **kwargs) -> Dict:
        """Make a GET request.

        Args:
            endpoint: API endpoint path
            **kwargs: Additional arguments for requests

        Returns:
            Response JSON

        Raises:
            requests.HTTPError: If request fails
        """
        url = f"{self.base_url}{endpoint}"
        response = self.session.get(url, verify=self.verify_ssl, **kwargs)

        # Handle authentication errors with friendly messages
        if response.status_code in (401, 403):
            raise requests.HTTPError(
                f"Authentication failed: Your API token is likely wrong or missing. "
                f"Please check your token and try again.",
                response=response
            )

        response.raise_for_status()
        if not response.content:
            return {}
        try:
            return response.json()
        except ValueError as e:
            raise RuntimeError(
                f"Failed to parse JSON response from {url} (status {response.status_code}): {response.text!r}"
            ) from e

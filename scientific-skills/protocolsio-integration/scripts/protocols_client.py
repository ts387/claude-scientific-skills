#!/usr/bin/env python3
"""
Protocols.io API Client

A convenient client for interacting with the Protocols.io API that
automatically loads your access token from the configuration file.

Usage:
    from protocols_client import ProtocolsClient

    # Initialize (token loaded automatically)
    client = ProtocolsClient()

    # Search for protocols
    results = client.search_protocols(key="CRISPR", page_size=10)

    # Get a specific protocol
    protocol = client.get_protocol(protocol_id=12345)

    # Create a new protocol
    new_protocol = client.create_protocol(
        title="My Protocol",
        description="Protocol description"
    )

Author: Claude Scientific Skills
License: MIT
"""

import os
import sys
import requests
import time
from pathlib import Path
from typing import Dict, List, Optional, Any


class ProtocolsClient:
    """Client for Protocols.io API with automatic token loading."""

    BASE_URL = "https://protocols.io/api/v3"
    RATE_LIMIT_DELAY = 0.6  # 100 requests per minute = 0.6s between requests

    def __init__(self, token: Optional[str] = None):
        """
        Initialize Protocols.io client.

        Args:
            token: Access token (if None, loads from config file)
        """
        self.token = token or self._load_token()
        if not self.token:
            raise ValueError(
                "No access token found. Run setup_config.py to configure your token:\n"
                "  python setup_config.py --token YOUR_TOKEN"
            )

        self.last_request_time = 0

    def _load_token(self) -> Optional[str]:
        """Load access token from config file."""
        # Try to load from config file
        config_path = Path(__file__).parent.parent / ".protocols_config"

        if config_path.exists():
            try:
                with open(config_path, 'r') as f:
                    for line in f:
                        if line.startswith('PROTOCOLS_IO_TOKEN='):
                            return line.split('=', 1)[1].strip()
            except Exception:
                pass

        # Try environment variable as fallback
        return os.environ.get('PROTOCOLS_IO_TOKEN')

    def _rate_limit(self):
        """Ensure requests don't exceed rate limit."""
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        if time_since_last < self.RATE_LIMIT_DELAY:
            time.sleep(self.RATE_LIMIT_DELAY - time_since_last)
        self.last_request_time = time.time()

    def _make_request(
        self,
        method: str,
        endpoint: str,
        params: Optional[Dict] = None,
        json_data: Optional[Dict] = None,
        files: Optional[Dict] = None,
        data: Optional[Dict] = None,
        max_retries: int = 3
    ) -> Dict[str, Any]:
        """
        Make API request with retry logic.

        Args:
            method: HTTP method (GET, POST, PUT, DELETE)
            endpoint: API endpoint path
            params: Query parameters
            json_data: JSON body data
            files: Files for multipart upload
            data: Form data
            max_retries: Maximum retry attempts

        Returns:
            JSON response as dictionary
        """
        url = f"{self.BASE_URL}{endpoint}"
        headers = {"Authorization": f"Bearer {self.token}"}

        if json_data and not files:
            headers["Content-Type"] = "application/json"

        for attempt in range(max_retries):
            try:
                self._rate_limit()

                response = requests.request(
                    method=method,
                    url=url,
                    headers=headers,
                    params=params,
                    json=json_data,
                    files=files,
                    data=data,
                    timeout=30
                )

                if response.status_code in [200, 201]:
                    return response.json()
                elif response.status_code == 429:  # Rate limit
                    wait_time = int(response.headers.get('Retry-After', 60))
                    print(f"Rate limited. Waiting {wait_time}s...")
                    time.sleep(wait_time)
                elif response.status_code >= 500:  # Server error
                    wait_time = 2 ** attempt
                    print(f"Server error. Waiting {wait_time}s before retry...")
                    time.sleep(wait_time)
                else:
                    response.raise_for_status()

            except requests.exceptions.Timeout:
                if attempt < max_retries - 1:
                    wait_time = 2 ** attempt
                    print(f"Request timeout. Waiting {wait_time}s...")
                    time.sleep(wait_time)
                else:
                    raise

        raise Exception(f"Failed after {max_retries} retries")

    # ==================== Protocol Operations ====================

    def search_protocols(
        self,
        key: Optional[str] = None,
        filter: str = "public",
        page_size: int = 10,
        page_id: int = 0,
        order_field: str = "date",
        order_dir: str = "desc",
        content_format: str = "html"
    ) -> Dict[str, Any]:
        """
        Search for protocols.

        Args:
            key: Search keyword
            filter: Filter type (public, user_public, user_private)
            page_size: Results per page (max 50)
            page_id: Page number (0-indexed)
            order_field: Sort field (date, name, id, activity)
            order_dir: Sort direction (asc, desc)
            content_format: Content format (json, html, markdown)

        Returns:
            Search results with protocols
        """
        params = {
            "filter": filter,
            "page_size": min(page_size, 50),
            "page_id": page_id,
            "order_field": order_field,
            "order_dir": order_dir,
            "content_format": content_format
        }

        if key:
            params["key"] = key

        return self._make_request("GET", "/protocols", params=params)

    def get_protocol(
        self,
        protocol_id: int,
        content_format: str = "html"
    ) -> Dict[str, Any]:
        """
        Get detailed information about a protocol.

        Args:
            protocol_id: Protocol ID
            content_format: Content format (json, html, markdown)

        Returns:
            Protocol details including all steps
        """
        return self._make_request(
            "GET",
            f"/protocols/{protocol_id}",
            params={"content_format": content_format}
        )

    def create_protocol(
        self,
        title: str,
        description: Optional[str] = None,
        tags: Optional[List[str]] = None,
        authors: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Create a new protocol.

        Args:
            title: Protocol title
            description: Protocol description
            tags: List of tags
            authors: List of author names

        Returns:
            Created protocol data
        """
        data = {"title": title}

        if description:
            data["description"] = description
        if tags:
            data["tags"] = tags
        if authors:
            data["authors"] = authors

        return self._make_request("POST", "/protocols", json_data=data)

    def update_protocol(
        self,
        protocol_id: int,
        title: Optional[str] = None,
        description: Optional[str] = None,
        tags: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Update an existing protocol.

        Args:
            protocol_id: Protocol ID
            title: New title (optional)
            description: New description (optional)
            tags: New tags (optional)

        Returns:
            Updated protocol data
        """
        data = {}
        if title:
            data["title"] = title
        if description:
            data["description"] = description
        if tags:
            data["tags"] = tags

        return self._make_request(
            "PATCH",
            f"/protocols/{protocol_id}",
            json_data=data
        )

    def publish_protocol(self, protocol_id: int) -> Dict[str, Any]:
        """
        Publish a protocol and issue a DOI.

        Args:
            protocol_id: Protocol ID

        Returns:
            Published protocol with DOI
        """
        return self._make_request("POST", f"/protocols/{protocol_id}/publish")

    # ==================== Protocol Steps ====================

    def add_step(
        self,
        protocol_id: int,
        title: str,
        description: Optional[str] = None,
        step_number: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Add a step to a protocol.

        Args:
            protocol_id: Protocol ID
            title: Step title
            description: Step description
            step_number: Position (if None, adds to end)

        Returns:
            Created step data
        """
        data = {"title": title}

        if description:
            data["description"] = description
        if step_number is not None:
            data["step_number"] = step_number

        return self._make_request(
            "POST",
            f"/protocols/{protocol_id}/steps",
            json_data=data
        )

    # ==================== Workspace Operations ====================

    def list_workspaces(self) -> Dict[str, Any]:
        """
        List all accessible workspaces.

        Returns:
            List of workspaces
        """
        return self._make_request("GET", "/workspaces")

    def get_workspace(self, workspace_id: int) -> Dict[str, Any]:
        """
        Get workspace details.

        Args:
            workspace_id: Workspace ID

        Returns:
            Workspace details
        """
        return self._make_request("GET", f"/workspaces/{workspace_id}")

    # ==================== File Operations ====================

    def upload_file(
        self,
        workspace_id: int,
        file_path: str,
        folder_id: str = "root",
        description: Optional[str] = None,
        tags: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Upload a file to a workspace.

        Args:
            workspace_id: Workspace ID
            file_path: Path to file to upload
            folder_id: Destination folder (default: "root")
            description: File description
            tags: Comma-separated tags

        Returns:
            Uploaded file data
        """
        data = {"folder_id": folder_id}

        if description:
            data["description"] = description
        if tags:
            data["tags"] = tags

        with open(file_path, "rb") as f:
            files = {"file": f}
            return self._make_request(
                "POST",
                f"/workspaces/{workspace_id}/files/upload",
                files=files,
                data=data
            )

    # ==================== Comments/Discussions ====================

    def get_protocol_comments(
        self,
        protocol_id: int
    ) -> Dict[str, Any]:
        """
        Get all comments on a protocol.

        Args:
            protocol_id: Protocol ID

        Returns:
            List of comments
        """
        return self._make_request("GET", f"/protocols/{protocol_id}/comments")

    def add_comment(
        self,
        protocol_id: int,
        comment: str,
        parent_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Add a comment to a protocol.

        Args:
            protocol_id: Protocol ID
            comment: Comment text
            parent_id: Parent comment ID (for replies)

        Returns:
            Created comment data
        """
        data = {"comment": comment}
        if parent_id:
            data["parent_id"] = parent_id

        return self._make_request(
            "POST",
            f"/protocols/{protocol_id}/comments",
            json_data=data
        )


def main():
    """Example usage of the Protocols.io client."""
    import argparse

    parser = argparse.ArgumentParser(description="Protocols.io API Client")
    parser.add_argument("--search", help="Search for protocols")
    parser.add_argument("--get", type=int, help="Get protocol by ID")
    parser.add_argument("--workspaces", action="store_true", help="List workspaces")

    args = parser.parse_args()

    try:
        client = ProtocolsClient()

        if args.search:
            results = client.search_protocols(key=args.search)
            print(f"Found {results['total']} protocols")
            for protocol in results.get('items', []):
                print(f"- [{protocol['id']}] {protocol['title']}")

        elif args.get:
            protocol = client.get_protocol(args.get)
            print(f"Title: {protocol['protocol']['title']}")
            print(f"DOI: {protocol['protocol'].get('doi', 'N/A')}")

        elif args.workspaces:
            workspaces = client.list_workspaces()
            print(f"Workspaces ({len(workspaces['items'])}):")
            for ws in workspaces['items']:
                print(f"- [{ws['id']}] {ws['name']}")

        else:
            parser.print_help()

    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()

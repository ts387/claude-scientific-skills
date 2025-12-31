#!/usr/bin/env python3
"""
Protocols.io Configuration Setup Script

This script helps configure your Protocols.io access token once,
then it will be automatically loaded for all future uses.

Usage:
    python setup_config.py [--token YOUR_TOKEN]

Author: Claude Scientific Skills
License: MIT
"""

import os
import sys
import argparse
from pathlib import Path


def get_config_path():
    """Get the path to the config file."""
    # Store config in the skill directory
    skill_dir = Path(__file__).parent.parent
    return skill_dir / ".protocols_config"


def save_token(token: str) -> bool:
    """
    Save access token to config file.

    Args:
        token: The Protocols.io access token

    Returns:
        True if successful, False otherwise
    """
    try:
        config_path = get_config_path()

        # Write token to file
        with open(config_path, 'w') as f:
            f.write(f"PROTOCOLS_IO_TOKEN={token}\n")

        # Set secure file permissions (user read/write only)
        os.chmod(config_path, 0o600)

        print(f"✓ Token saved to {config_path}")
        print(f"✓ File permissions set to 600 (secure)")
        return True

    except Exception as e:
        print(f"✗ Error saving token: {e}", file=sys.stderr)
        return False


def load_token() -> str:
    """
    Load access token from config file.

    Returns:
        The access token, or None if not found
    """
    config_path = get_config_path()

    if not config_path.exists():
        return None

    try:
        with open(config_path, 'r') as f:
            for line in f:
                if line.startswith('PROTOCOLS_IO_TOKEN='):
                    return line.split('=', 1)[1].strip()
    except Exception:
        return None

    return None


def test_token(token: str) -> bool:
    """
    Test if the token works by making a simple API request.

    Args:
        token: The access token to test

    Returns:
        True if token is valid, False otherwise
    """
    try:
        import requests

        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(
            "https://protocols.io/api/v3/protocols",
            headers=headers,
            params={"filter": "public", "page_size": 1}
        )

        if response.status_code == 200:
            print("✓ Token is valid and working!")
            return True
        elif response.status_code == 401:
            print("✗ Token is invalid or expired")
            return False
        else:
            print(f"⚠ Unexpected response: {response.status_code}")
            return False

    except ImportError:
        print("⚠ requests library not installed, skipping token validation")
        print("  Install with: uv pip install requests")
        return None
    except Exception as e:
        print(f"✗ Error testing token: {e}")
        return False


def validate_setup() -> bool:
    """
    Validate that the configuration is set up correctly.

    Returns:
        True if setup is valid, False otherwise
    """
    print("Validating setup...")
    print()

    # Check if token is configured
    token = load_token()
    if not token:
        print("✗ No access token configured")
        print()
        print("To set up your access token:")
        print("1. Log into protocols.io at https://www.protocols.io/")
        print("2. Go to your Profile Settings")
        print("3. Look for 'API' or 'Developer' section")
        print("4. Copy your CLIENT_ACCESS_TOKEN")
        print("5. Run this script with --token flag:")
        print("   python setup_config.py --token YOUR_TOKEN")
        print()
        return False
    else:
        # Mask the token for display
        masked = token[:8] + "..." + token[-4:] if len(token) > 12 else "***"
        print(f"✓ Access token is configured ({masked})")

    # Test the token
    test_result = test_token(token)

    print()
    if test_result:
        print("✓ Setup is complete! Your token will be automatically loaded.")
        return True
    else:
        print("⚠ Token is configured but may not be working properly")
        return False


def main():
    """Main entry point for the setup script."""
    parser = argparse.ArgumentParser(
        description="Setup Protocols.io access token configuration",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Set up your access token
  python setup_config.py --token YOUR_TOKEN_HERE

  # Validate existing setup
  python setup_config.py --validate

How to get your access token:
  1. Log into protocols.io (https://www.protocols.io/)
  2. Go to Profile Settings
  3. Find the API or Developer section
  4. Copy your CLIENT_ACCESS_TOKEN

Once configured, the token will be automatically loaded when you use
the protocols_client.py module.
        """
    )

    parser.add_argument(
        "--token",
        help="Your Protocols.io CLIENT_ACCESS_TOKEN"
    )

    parser.add_argument(
        "--validate",
        action="store_true",
        help="Validate existing setup"
    )

    args = parser.parse_args()

    # If no arguments, show validation
    if not args.token and not args.validate:
        args.validate = True

    # Handle token setup
    if args.token:
        print("Setting up Protocols.io access token...")
        if save_token(args.token):
            print()
            print("✓ Configuration complete!")
            print()
            print("Your token is now saved and will be automatically loaded.")
            print("You can test it with: python setup_config.py --validate")
            print()

            # Test the token
            test_token(args.token)

    # Validate setup
    if args.validate:
        if not validate_setup():
            return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())

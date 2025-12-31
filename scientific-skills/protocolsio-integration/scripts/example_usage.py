#!/usr/bin/env python3
"""
Example usage of the Protocols.io client with automatic token loading.

This demonstrates how easy it is to use the client after running setup_config.py once.

Author: Claude Scientific Skills
License: MIT
"""

from protocols_client import ProtocolsClient


def example_search():
    """Example: Search for CRISPR protocols."""
    print("=" * 60)
    print("Example 1: Search for CRISPR protocols")
    print("=" * 60)

    client = ProtocolsClient()
    results = client.search_protocols(key="CRISPR", page_size=5)

    print(f"\nFound {results.get('total', 0)} CRISPR protocols")
    print("\nTop 5 results:")

    for protocol in results.get('items', []):
        print(f"\n[{protocol['id']}] {protocol['title']}")
        print(f"  DOI: {protocol.get('doi', 'N/A')}")
        print(f"  URL: {protocol.get('uri', 'N/A')}")


def example_get_protocol():
    """Example: Get details of a specific protocol."""
    print("\n" + "=" * 60)
    print("Example 2: Get protocol details")
    print("=" * 60)

    client = ProtocolsClient()

    # Search for a protocol first
    results = client.search_protocols(key="PCR", page_size=1)

    if results.get('items'):
        protocol_id = results['items'][0]['id']
        print(f"\nFetching details for protocol {protocol_id}...")

        protocol = client.get_protocol(protocol_id)
        p = protocol.get('protocol', {})

        print(f"\nTitle: {p.get('title')}")
        print(f"DOI: {p.get('doi', 'N/A')}")
        print(f"Steps: {len(p.get('steps', []))}")
        print(f"Description: {p.get('description', 'N/A')[:200]}...")


def example_list_workspaces():
    """Example: List accessible workspaces."""
    print("\n" + "=" * 60)
    print("Example 3: List your workspaces")
    print("=" * 60)

    client = ProtocolsClient()
    workspaces = client.list_workspaces()

    print(f"\nYou have access to {len(workspaces.get('items', []))} workspace(s):")

    for ws in workspaces.get('items', []):
        print(f"\n[{ws['id']}] {ws['name']}")
        print(f"  Role: {ws.get('role', 'N/A')}")


def example_create_protocol():
    """Example: Create a new protocol (commented out to avoid accidental creation)."""
    print("\n" + "=" * 60)
    print("Example 4: Create a new protocol (commented out)")
    print("=" * 60)

    print("\nTo create a protocol, uncomment the code below:")
    print("""
    client = ProtocolsClient()

    new_protocol = client.create_protocol(
        title="My New Protocol",
        description="This is a test protocol",
        tags=["test", "example"]
    )

    print(f"Created protocol: {new_protocol['protocol']['id']}")
    """)


def main():
    """Run all examples."""
    print("\n")
    print("╔" + "=" * 58 + "╗")
    print("║" + " " * 10 + "Protocols.io Client Examples" + " " * 20 + "║")
    print("╚" + "=" * 58 + "╝")
    print()

    try:
        # Run examples
        example_search()
        example_get_protocol()
        example_list_workspaces()
        example_create_protocol()

        print("\n" + "=" * 60)
        print("All examples completed successfully!")
        print("=" * 60)

    except ValueError as e:
        print(f"\nError: {e}")
        print("\nPlease run setup_config.py first to configure your access token:")
        print("  python setup_config.py --token YOUR_TOKEN")

    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()

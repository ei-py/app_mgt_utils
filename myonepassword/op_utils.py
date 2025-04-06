"""
1Password utility functions for retrieving credentials using the local 1Password CLI.
"""
import os
import json
import subprocess
import argparse
from typing import Optional, Dict

def get_credential_by_username(username: Optional[str] = None, credential_name: Optional[str] = None, vault: Optional[str] = None) -> Dict[str, str]:
    """
    Retrieve 1Password credentials by username or credential name using the local 1Password CLI.
    
    Args:
        username (str, optional): The username to search for
        credential_name (str, optional): The name of the credential to search for
        vault (str, optional): The vault name to search in. If None, searches in all vaults.
    
    Returns:
        Dict[str, str]: A dictionary containing the credentials with keys 'username' and 'password'
    
    Raises:
        ValueError: If the credential is not found, if 1Password CLI is not installed,
                   or if neither username nor credential_name is provided
    """
    if not username and not credential_name:
        raise ValueError("Either username or credential_name must be provided")
    
    # Check if op CLI is installed
    try:
        subprocess.run(['op', '--version'], capture_output=True, check=True)
    except (subprocess.SubprocessError, FileNotFoundError):
        raise ValueError("1Password CLI (op) is not installed or not in PATH")
    
    # Build the search command
    if credential_name:
        # Search by item title
        search_cmd = ['op', 'item', 'get', credential_name, '--format', 'json']
        if vault:
            search_cmd.extend(['--vault', vault])
    else:
        # Search by username
        search_cmd = ['op', 'item', 'search', f'username:{username}', '--format', 'json']
        if vault:
            search_cmd.extend(['--vault', vault])
    
    try:
        # Execute the search command
        result = subprocess.run(search_cmd, capture_output=True, text=True, check=True)
        items = json.loads(result.stdout)
        
        # Handle both single item and list responses
        if isinstance(items, dict):
            items = [items]
        
        if not items:
            search_by = "credential name" if credential_name else "username"
            search_value = credential_name if credential_name else username
            raise ValueError(f"No credentials found for {search_by}: {search_value}")
        
        # Get the first matching item
        item = items[0]
        
        # Extract username and password from the item
        credentials = {
            'username': '',
            'credential': ''
        }
        
        # Parse the fields from the item
        for field in item.get('fields', []):
            if field.get('label', '').lower() == 'username':
                credentials['username'] = field.get('value', '')
            elif field.get('label', '').lower() == 'credential':
                credentials['credential'] = field.get('value', '')
        
        if not credentials['username'] or not credentials['credential']:
            raise ValueError(f"Username or password not found in the credential item")
        
        return credentials
    
    except subprocess.CalledProcessError as e:
        if e.returncode == 1 and "not signed in" in e.stderr:
            raise ValueError("Not signed in to 1Password CLI. Please run 'op signin' first.")
        raise ValueError(f"1Password CLI error: {e.stderr}")
    except json.JSONDecodeError:
        raise ValueError("Failed to parse 1Password CLI output")

def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description='Retrieve credentials from 1Password using local CLI')
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--username', '-u', help='Username to search for')
    group.add_argument('--credential-name', '-c', help='Credential name to search for')
    parser.add_argument('--vault', '-v', help='Vault name to search in')
    return parser.parse_args()

if __name__ == "__main__":
    args = parse_args()
    try:
        credentials = get_credential_by_username(
            username=args.username,
            credential_name=args.credential_name,
            vault=args.vault
        )
        print(f"Username: {credentials['username']}")
        print(f"Credential: {credentials['credential']}")
    except ValueError as e:
        print(f"Error: {str(e)}")
        exit(1)
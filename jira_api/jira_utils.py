"""
Jira API utility functions for interacting with Jira.
"""
import os
import sys
from typing import Optional

# Add the parent directory to the path so we can import the 1Password utility
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from myonepassword import get_credential_by_username

def get_jira_api_key(credential_name: str = "jira_api_key", vault: Optional[str] = None) -> str:
    """
    Retrieve the Jira API key from 1Password.
    
    Args:
        credential_name (str, optional): The name of the credential in 1Password. Defaults to "jira_api_key".
        vault (str, optional): The vault name to search in. If None, searches in all vaults.
    
    Returns:
        str: The Jira API key
    
    Raises:
        ValueError: If the credential is not found or if there's an error retrieving it
    """
    try:
        # Get the credential from 1Password
        credential = get_credential_by_username(credential_name=credential_name, vault=vault)
        
        # Return the credential value (which is the API key)
        return credential['credential']
    
    except ValueError as e:
        raise ValueError(f"Failed to retrieve Jira API key: {str(e)}")
    except Exception as e:
        raise ValueError(f"Unexpected error retrieving Jira API key: {str(e)}")

if __name__ == "__main__":
    # Simple test when run directly
    try:
        api_key = get_jira_api_key()
        print(f"Jira API Key: {api_key}")
    except ValueError as e:
        print(f"Error: {str(e)}")
        exit(1) 
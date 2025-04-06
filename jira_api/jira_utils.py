"""
Jira API utility functions for interacting with Jira.
"""
import os
import sys
from typing import Optional, Dict, Any
from jira import JIRA

# Add the parent directory to the path so we can import the 1Password utility
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.myonepassword import get_credential_by_username

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

def connect_to_jira(server_url: str, email: str, api_key: Optional[str] = None, vault: Optional[str] = None) -> JIRA:
    """
    Connect to Jira using API credentials.
    
    Args:
        server_url (str): The URL of the Jira server (e.g., 'https://your-domain.atlassian.net')
        email (str): The email address associated with the Jira account
        api_key (str, optional): The Jira API key. If not provided, it will be retrieved from 1Password.
        vault (str, optional): The vault name to search in for the API key. If None, searches in all vaults.
    
    Returns:
        JIRA: A JIRA client instance
    
    Raises:
        ValueError: If the connection fails or if required credentials are missing
    """
    try:
        # Get the API key if not provided
        if api_key is None:
            api_key = get_jira_api_key(vault=vault)
        
        # Create and return the JIRA client
        return JIRA(
            server=server_url,
            basic_auth=(email, api_key)
        )
    
    except Exception as e:
        raise ValueError(f"Failed to connect to Jira: {str(e)}")

def get_project(project_key: str, server_url: str, email: str, api_key: Optional[str] = None, vault: Optional[str] = None) -> Dict[str, Any]:
    """
    Retrieve a project from Jira.
    
    Args:
        project_key (str): The key of the project to retrieve (e.g., 'PROJ')
        server_url (str): The URL of the Jira server
        email (str): The email address associated with the Jira account
        api_key (str, optional): The Jira API key. If not provided, it will be retrieved from 1Password.
        vault (str, optional): The vault name to search in for the API key. If None, searches in all vaults.
    
    Returns:
        Dict[str, Any]: Project information
    
    Raises:
        ValueError: If the project cannot be retrieved or if required credentials are missing
    """
    try:
        # Connect to Jira
        jira = connect_to_jira(server_url, email, api_key, vault)
        
        # Retrieve the project
        project = jira.project(project_key)
        
        # Return project information
        project_info = {
            'key': getattr(project, 'key', None),
            'name': getattr(project, 'name', None),
            'description': getattr(project, 'description', None),
            'lead': getattr(project.lead, 'displayName', None) if hasattr(project, 'lead') else None,
            'url': getattr(project, 'self', None),
            'projectTypeKey': getattr(project, 'projectTypeKey', None),
            'simplified': getattr(project, 'simplified', None),
            'style': getattr(project, 'style', None),
            'favourite': getattr(project, 'favourite', None),
            'isPrivate': getattr(project, 'isPrivate', None)
        }
        
        # Remove None values
        project_info = {k: v for k, v in project_info.items() if v is not None}
        
        return project_info
    
    except Exception as e:
        raise ValueError(f"Failed to retrieve project {project_key}: {str(e)}")

if __name__ == "__main__":
    # Simple test when run directly
    try:
        # These values should be configured based on your Jira instance
        SERVER_URL = "https://your-domain.atlassian.net"  # Replace with your Jira server URL
        EMAIL = "your-email@example.com"  # Replace with your email
        
        # Get project information
        project_info = get_project("PROJ", SERVER_URL, EMAIL)  # Replace "PROJ" with your project key
        print(f"Project Information: {project_info}")
    
    except ValueError as e:
        print(f"Error: {str(e)}")
        exit(1) 
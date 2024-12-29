import json
import os
import sys 

# Constants for file names
GLOBAL_SETTINGS_FILE = "ezqmglobal.json"
LOCAL_SETTINGS_FILE = "ezqmlocal.json"

def get_global_settings_path():
    """Get the path of the global settings file."""
    return os.path.join(os.path.dirname(os.path.abspath(sys.argv[0])), GLOBAL_SETTINGS_FILE)

def get_local_settings_path():
    """Get the path of the local settings file in the current directory."""
    return os.path.join(os.getcwd(), LOCAL_SETTINGS_FILE)

def read_config(file_path):
    """
    Read configuration from a JSON file.
    Returns the configuration as a dictionary.
    """
    if not os.path.exists(file_path):
        return {}
    with open(file_path, 'r') as file:
        try:
            return json.load(file)
        except json.JSONDecodeError:
            raise ValueError(f"Error parsing JSON in {file_path}")

def write_config(file_path, config_data):
    """
    Write configuration to a JSON file.
    Creates the file if it doesn't exist.
    """
    with open(file_path, 'w') as file:
        json.dump(config_data, file, indent=4)

def read_global_settings():
    """Read and return the global settings."""
    return read_config(get_global_settings_path())

def write_global_settings(config_data):
    """Write data to the global settings file."""
    write_config(get_global_settings_path(), config_data)

def read_local_settings():
    """Read and return the local settings."""
    return read_config(get_local_settings_path())

def write_local_settings(config_data):
    """Write data to the local settings file."""
    write_config(get_local_settings_path(), config_data)

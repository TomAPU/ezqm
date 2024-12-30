import json
import os
import sys
from typing import Any, Dict, List
from .printing import print_fail, print_succ, print_status

# Constants for file names
GLOBAL_SETTINGS_FILE = "ezqmglobal.json"
LOCAL_SETTINGS_FILE = "ezqmlocal.json"


def get_global_settings_path():
    """
    Get the path of the global settings file in the user's ~/.config directory.
    Ensure the directory exists.
    """
    config_dir = os.path.join(os.path.expanduser("~"), ".config")
    os.makedirs(config_dir, exist_ok=True)  # Create directory if it doesn't exist
    return os.path.join(config_dir, GLOBAL_SETTINGS_FILE)


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
    with open(file_path, "r") as file:
        try:
            return json.load(file)
        except json.JSONDecodeError:
            raise ValueError(f"Error parsing JSON in {file_path}")


def write_config(file_path, config_data):
    """
    Write configuration to a JSON file.
    Creates the file if it doesn't exist.
    """
    with open(file_path, "w") as file:
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


########################## SCHEMA VALIDATION ##########################

LOCAL_SCHEMA = {
    "src": {"required": True, "path_type": "directory"},
    "vmlinux": {"required": True, "path_type": "file"},
    "bzImage": {"required": True, "path_type": "file"},
    "gdbport": {"required": True, "type": int},
    "qemuport": {"required": True, "type": int},
    "sshport": {"required": True, "type": int},
    "kernelparam": {"required": True, "type": str},
    "outputfile": {"required": True, "type": str},
    "additionalcmd": {"required": True, "type": list, "list_type": str},
    "snapshot_file": {"required": False, "path_type": "file"}
}

GLOBAL_SCHEMA = {
    "diskimage": {"required": True, "path_type": "file"},
    "sshkey": {"required": True, "path_type": "file"},
    "snapshotfolder": {"required": False, "path_type": "directory"}
}


def validate_keys_exist(
    settings: Dict[str, Any], required_keys: List[str], settings_name: str
) -> None:
    """
    Validate that all required keys exist in the given settings dictionary.
    """
    missing = [key for key in required_keys if key not in settings]
    if missing:
        raise ValueError(
            f"Missing required key(s) in {settings_name}: {', '.join(missing)}"
        )


def validate_path(path: str, path_type: str, key_name: str) -> None:
    """
    Validate that a path exists and is of the specified type (file or directory).
    """
    if not path:
        raise ValueError(f"Key '{key_name}' cannot be empty.")

    if path_type not in ("file", "directory"):
        raise ValueError(
            f"Invalid path_type '{path_type}'. Must be 'file' or 'directory'."
        )

    if path_type == "file" and not os.path.isfile(path):
        raise ValueError(f"Key '{key_name}': File '{path}' does not exist.")
    elif path_type == "directory" and not os.path.isdir(path):
        raise ValueError(f"Key '{key_name}': Directory '{path}' does not exist.")


def validate_type(value: Any, expected_type: type, key_name: str) -> None:
    """
    Validate that a given value is of the expected Python type.
    """
    if not isinstance(value, expected_type):
        raise TypeError(
            f"Key '{key_name}' must be of type {expected_type.__name__}, "
            f"got {type(value).__name__} instead."
        )


def validate_list_elements(lst: List[Any], expected_type: type, key_name: str) -> None:
    """
    Validate that all elements in a list are of the specified type.
    """
    if not all(isinstance(item, expected_type) for item in lst):
        raise TypeError(
            f"All elements in '{key_name}' must be of type {expected_type.__name__}."
        )


def validate_settings(
    settings: Dict[str, Any], schema: Dict[str, Dict[str, Any]], settings_name: str
) -> None:
    """
    Validate a settings dictionary against a schema.

    :param settings: The dictionary with user-defined/config values.
    :param schema: A dict describing how to validate each key.
    :param settings_name: A human-readable name for the settings (used in error messages).
    """

    # 1. Ensure all required keys exist
    required_keys = [k for k, v in schema.items() if v.get("required")]
    validate_keys_exist(settings, required_keys, settings_name)

    # 2. For each key in the schema, run validations (if the key is present)
    for key, rules in schema.items():
        # If key is optional and doesn't exist, skip
        if key not in settings:
            continue

        value = settings[key]

        # If there's a type check, do that
        if "type" in rules:
            validate_type(value, rules["type"], key)

        # If it's a list and "list_type" is specified, check each element
        if rules.get("type") is list and "list_type" in rules:
            validate_list_elements(value, rules["list_type"], key)

        # If there's a path check, do that
        if "path_type" in rules:
            validate_path(value, rules["path_type"], key)


def check_local_settings() -> None:
    """
    Check if local settings are configured correctly.
    """
    try:
        local_settings = read_local_settings()  # you already have this function
        validate_type(local_settings, dict, "local_settings")
        validate_settings(local_settings, LOCAL_SCHEMA, "local settings")
        print_succ("Local settings look good.")
    except Exception as exc:
        print_fail(f"Error in local settings: {exc}")
        raise


def check_global_settings() -> None:
    """
    Check if global settings are configured correctly.
    """
    try:
        global_settings = read_global_settings()  # you already have this function
        validate_type(global_settings, dict, "global_settings")
        validate_settings(global_settings, GLOBAL_SCHEMA, "global settings")
        print_succ("Global settings look good.")
    except Exception as exc:
        print_fail(f"Error in global settings: {exc}")
        raise
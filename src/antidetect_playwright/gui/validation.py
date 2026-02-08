"""Input validation utilities for GUI forms."""

from typing import TypeAlias

from .constants import (
    MAX_PROFILE_NAME_LENGTH,
    MAX_FOLDER_NAME_LENGTH,
    MAX_TAG_NAME_LENGTH,
    MAX_NOTE_LENGTH,
)

ValidationResult: TypeAlias = tuple[bool, str]
"""Type alias for validation results: (is_valid, error_message)"""


def validate_profile_name(name: str) -> ValidationResult:
    """Validate profile name.

    Args:
        name: Profile name to validate.

    Returns:
        Tuple of (is_valid, error_message).
        If valid, error_message is empty string.

    Examples:
        >>> validate_profile_name("My Profile")
        (True, "")
        >>> validate_profile_name("")
        (False, "Profile name cannot be empty")
        >>> validate_profile_name("x" * 150)
        (False, "Profile name too long (max 100 characters)")
    """
    name = name.strip()

    if not name:
        return False, "Profile name cannot be empty"

    if len(name) > MAX_PROFILE_NAME_LENGTH:
        return False, f"Profile name too long (max {MAX_PROFILE_NAME_LENGTH} characters)"

    # Check for invalid characters
    invalid_chars = ['<', '>', ':', '"', '/', '\\', '|', '?', '*']
    if any(char in name for char in invalid_chars):
        return False, f"Profile name contains invalid characters: {invalid_chars}"

    return True, ""


def validate_folder_name(name: str) -> ValidationResult:
    """Validate folder name.

    Args:
        name: Folder name to validate.

    Returns:
        Tuple of (is_valid, error_message).

    Examples:
        >>> validate_folder_name("Work")
        (True, "")
        >>> validate_folder_name("")
        (False, "Folder name cannot be empty")
    """
    name = name.strip()

    if not name:
        return False, "Folder name cannot be empty"

    if len(name) > MAX_FOLDER_NAME_LENGTH:
        return False, f"Folder name too long (max {MAX_FOLDER_NAME_LENGTH} characters)"

    # Check for invalid characters (same as profile)
    invalid_chars = ['<', '>', ':', '"', '/', '\\', '|', '?', '*']
    if any(char in name for char in invalid_chars):
        return False, f"Folder name contains invalid characters: {invalid_chars}"

    return True, ""


def validate_tag_name(name: str) -> ValidationResult:
    """Validate tag name.

    Args:
        name: Tag name to validate.

    Returns:
        Tuple of (is_valid, error_message).

    Examples:
        >>> validate_tag_name("important")
        (True, "")
        >>> validate_tag_name("")
        (False, "Tag name cannot be empty")
    """
    name = name.strip()

    if not name:
        return False, "Tag name cannot be empty"

    if len(name) > MAX_TAG_NAME_LENGTH:
        return False, f"Tag name too long (max {MAX_TAG_NAME_LENGTH} characters)"

    # Tags should be simpler (no special characters except dash and underscore)
    if not all(c.isalnum() or c in ['-', '_', ' '] for c in name):
        return False, "Tag name can only contain letters, numbers, spaces, hyphens, and underscores"

    return True, ""


def validate_notes(notes: str) -> ValidationResult:
    """Validate notes content.

    Args:
        notes: Notes text to validate.

    Returns:
        Tuple of (is_valid, error_message).

    Examples:
        >>> validate_notes("Some notes here")
        (True, "")
        >>> validate_notes("x" * 15000)
        (False, "Notes too long (max 10000 characters)")
    """
    if len(notes) > MAX_NOTE_LENGTH:
        return False, f"Notes too long (max {MAX_NOTE_LENGTH} characters)"

    return True, ""


def validate_url(url: str, allow_empty: bool = True) -> ValidationResult:
    """Validate URL format.

    Args:
        url: URL to validate.
        allow_empty: Whether empty string is valid.

    Returns:
        Tuple of (is_valid, error_message).

    Examples:
        >>> validate_url("https://example.com")
        (True, "")
        >>> validate_url("not-a-url")
        (False, "Invalid URL format")
    """
    if not url.strip():
        if allow_empty:
            return True, ""
        return False, "URL cannot be empty"

    # Basic URL validation
    if not any(url.startswith(proto) for proto in ["http://", "https://", "about:", "file://"]):
        return False, "Invalid URL format (must start with http://, https://, about:, or file://)"

    return True, ""


def validate_port(port: int | str) -> ValidationResult:
    """Validate network port number.

    Args:
        port: Port number to validate (int or string).

    Returns:
        Tuple of (is_valid, error_message).

    Examples:
        >>> validate_port(8080)
        (True, "")
        >>> validate_port(70000)
        (False, "Port must be between 1 and 65535")
        >>> validate_port("invalid")
        (False, "Port must be a number")
    """
    try:
        port_num = int(port)
    except (ValueError, TypeError):
        return False, "Port must be a number"

    if not 1 <= port_num <= 65535:
        return False, "Port must be between 1 and 65535"

    return True, ""


def validate_proxy_host(host: str) -> ValidationResult:
    """Validate proxy hostname or IP address.

    Args:
        host: Hostname or IP to validate.

    Returns:
        Tuple of (is_valid, error_message).

    Examples:
        >>> validate_proxy_host("proxy.example.com")
        (True, "")
        >>> validate_proxy_host("192.168.1.1")
        (True, "")
        >>> validate_proxy_host("")
        (False, "Proxy host cannot be empty")
    """
    if not host or not host.strip():
        return False, "Proxy host cannot be empty"

    # Basic validation - check for obviously invalid characters
    if any(c in host for c in ['<', '>', '"', "'", '`', '\\n', '\\r']):
        return False, "Proxy host contains invalid characters"

    return True, ""

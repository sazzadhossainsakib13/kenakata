"""
KenaKata Accounts & Security Utilities
Canonical mobile normalization and security helpers.
"""
import re


def normalize_bd_mobile(mobile_str):
    """
    Normalize any valid Bangladesh mobile number into canonical 11-digit format: 01XXXXXXXXX.
    Accepts:
      +8801XXXXXXXXX (14 chars)
      8801XXXXXXXXX  (13 chars)
      01XXXXXXXXX    (11 chars)
      Formatted with spaces, hyphens, dots, parentheses (e.g. +880 1711-223344)
    Returns:
      Canonical 11-digit string starting with 013-019 (e.g., '01711223344')
      or None if invalid.
    """
    if not mobile_str:
        return None

    cleaned = re.sub(r'[\s\-\(\)\.]', '', str(mobile_str).strip())
    if cleaned.startswith('+880'):
        cleaned = cleaned[4:]
    elif cleaned.startswith('880'):
        cleaned = cleaned[3:]
    elif cleaned.startswith('+88'):
        cleaned = cleaned[3:]

    # If 10 digits starting with 1[3-9], prepend 0
    if len(cleaned) == 10 and cleaned[0] in '1' and cleaned[1] in '3456789':
        cleaned = '0' + cleaned

    # Valid Bangladesh mobile is exactly 11 digits: 01[3-9]\d{8}
    if re.fullmatch(r'01[3-9]\d{8}', cleaned):
        return cleaned

    return None


def validate_bd_mobile(mobile_str):
    """Check whether a mobile string is a valid Bangladesh mobile number."""
    return normalize_bd_mobile(mobile_str) is not None

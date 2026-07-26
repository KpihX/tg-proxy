"""
Custom exceptions for tg-proxy. Prevents stack traces and hides secrets.
"""


class TgProxyError(Exception):
    """Base exception for all tg-proxy errors."""

    def __init__(self, message: str):
        super().__init__(message)

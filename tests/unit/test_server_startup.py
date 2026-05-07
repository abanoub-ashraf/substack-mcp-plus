# ABOUTME: Unit tests for MCP server startup behavior before account authentication
# ABOUTME: Ensures tool discovery does not require a valid Substack session

import asyncio
from unittest.mock import AsyncMock, MagicMock, patch

from src.server import SubstackMCPServer


def test_server_init_does_not_create_auth_handler():
    """Server startup should not require account authentication."""
    with patch("src.server.AuthHandler") as auth_handler_class:
        server = SubstackMCPServer()

    auth_handler_class.assert_not_called()
    assert server.auth_handler is None


def test_get_authenticated_client_creates_auth_handler_lazily():
    """Account tools should initialize auth only when they need a client."""
    client = object()
    auth_handler = MagicMock()
    auth_handler.authenticate = AsyncMock(return_value=client)

    with patch("src.server.AuthHandler", return_value=auth_handler) as auth_class:
        server = SubstackMCPServer()
        assert auth_class.call_count == 0

        authenticated_client = asyncio.run(server._get_authenticated_client())

    assert authenticated_client is client
    auth_class.assert_called_once_with()
    auth_handler.authenticate.assert_awaited_once_with()

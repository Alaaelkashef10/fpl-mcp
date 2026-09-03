import os
from typing import Any

import httpx
from mcp.server.fastmcp import FastMCP

BASE_URL = "https://fantasy.premierleague.com/api"
DEFAULT_MANAGER_ID = os.getenv("FPL_DEFAULT_MANAGER_ID", "")
HOST = os.getenv("HOST", "0.0.0.0")
PORT = int(os.getenv("PORT", "8000"))

mcp = FastMCP("FPL MCP", stateless_http=True, json_response=True)


def _get(path: str) -> Any:
    with httpx.Client(timeout=20.0, follow_redirects=True) as client:
        response = client.get(f"{BASE_URL}/{path.lstrip('/')}")
        response.raise_for_status()
        return response.json()


def _manager_id(manager_id: str | None = None) -> str:
    value = manager_id or DEFAULT_MANAGER_ID
    if not value:
        raise ValueError("manager_id is required")
    return value


@mcp.tool
def get_fpl_status() -> Any:
    """Return the current FPL bootstrap/status data."""
    return _get("bootstrap-static/")


@mcp.tool
def get_players() -> Any:
    """Return all FPL players and current game metadata."""
    return _get("bootstrap-static/")


@mcp.tool
def get_fixtures(gameweek: int | None = None) -> Any:
    """Return FPL fixtures, optionally filtered by gameweek."""
    fixtures = _get("fixtures/")
    if gameweek is None:
        return fixtures
    return [fixture for fixture in fixtures if fixture.get("event") == gameweek]


@mcp.tool
def get_manager(manager_id: str | None = None) -> Any:
    """Return a manager's FPL entry summary."""
    return _get(f"entry/{_manager_id(manager_id)}/")


@mcp.tool
def get_manager_history(manager_id: str | None = None) -> Any:
    """Return a manager's season history and chips."""
    return _get(f"entry/{_manager_id(manager_id)}/history/")


@mcp.tool
def get_manager_picks(gameweek: int, manager_id: str | None = None) -> Any:
    """Return a manager's squad picks for a gameweek."""
    return _get(f"entry/{_manager_id(manager_id)}/event/{gameweek}/picks/")


@mcp.tool
def get_manager_transfers(manager_id: str | None = None) -> Any:
    """Return a manager's transfer history."""
    return _get(f"entry/{_manager_id(manager_id)}/transfers/")


@mcp.tool
def get_player_summary(player_id: int) -> Any:
    """Return a player's detailed FPL history and fixtures."""
    return _get(f"element-summary/{player_id}/")


@mcp.tool
def get_live_gameweek(gameweek: int) -> Any:
    """Return live FPL data for a gameweek."""
    return _get(f"event/{gameweek}/live/")


if __name__ == "__main__":
    mcp.run(
        transport="streamable-http",
        host=HOST,
        port=PORT,
    )

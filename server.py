"""FPL MCP server for Claude + Composio.

Exposes read-only tools over the public Fantasy Premier League API.
"""

from __future__ import annotations

import os
from typing import Any

import httpx
from mcp.server.fastmcp import FastMCP

BASE_URL = "https://fantasy.premierleague.com/api"
DEFAULT_MANAGER_ID = os.getenv("FPL_DEFAULT_MANAGER_ID", "")

mcp = FastMCP("FPL MCP", stateless_http=True, json_response=True)


def _get(path: str, params: dict[str, Any] | None = None) -> Any:
    url = f"{BASE_URL}/{path.lstrip('/')}"
    with httpx.Client(timeout=20.0, follow_redirects=True) as client:
        response = client.get(url, params=params)
        response.raise_for_status()
        return response.json()


def _manager_id(manager_id: int | None) -> int:
    value = manager_id if manager_id is not None else DEFAULT_MANAGER_ID
    if not value:
        raise ValueError("manager_id is required unless FPL_DEFAULT_MANAGER_ID is configured")
    return int(value)


@mcp.tool()
def get_fpl_status() -> dict[str, Any]:
    """Return current Gameweek status and season metadata from FPL."""
    data = _get("bootstrap-static/")
    events = data.get("events", [])
    current = next((e for e in events if e.get("is_current")), None)
    next_event = next((e for e in events if e.get("is_next")), None)
    return {
        "current_gameweek": current,
        "next_gameweek": next_event,
        "events_count": len(events),
        "season": data.get("game_settings", {}).get("season"),
    }


@mcp.tool()
def get_players() -> list[dict[str, Any]]:
    """Return the current FPL player dataset with prices, ownership and core stats."""
    return _get("bootstrap-static/").get("elements", [])


@mcp.tool()
def get_fixtures(gameweek: int | None = None) -> list[dict[str, Any]]:
    """Return all FPL fixtures, optionally restricted to one Gameweek."""
    params = {"event": gameweek} if gameweek is not None else None
    return _get("fixtures/", params=params)


@mcp.tool()
def get_manager(manager_id: int | None = None) -> dict[str, Any]:
    """Return an FPL manager profile. Uses the configured default manager when omitted."""
    return _get(f"entry/{_manager_id(manager_id)}/")


@mcp.tool()
def get_manager_history(manager_id: int | None = None) -> dict[str, Any]:
    """Return season history and chip usage for an FPL manager."""
    return _get(f"entry/{_manager_id(manager_id)}/history/")


@mcp.tool()
def get_manager_picks(gameweek: int, manager_id: int | None = None) -> dict[str, Any]:
    """Return a manager's squad, captain, vice-captain, bench and active chip for a Gameweek."""
    return _get(f"entry/{_manager_id(manager_id)}/event/{int(gameweek)}/picks/")


@mcp.tool()
def get_manager_transfers(manager_id: int | None = None) -> list[dict[str, Any]]:
    """Return transfer history for an FPL manager."""
    return _get(f"entry/{_manager_id(manager_id)}/transfers/")


@mcp.tool()
def get_player_summary(player_id: int) -> dict[str, Any]:
    """Return detailed season and historical data for one FPL player."""
    return _get(f"element-summary/{int(player_id)}/")


@mcp.tool()
def get_live_gameweek(gameweek: int) -> dict[str, Any]:
    """Return live player points/statistics for a Gameweek."""
    return _get(f"event/{int(gameweek)}/live/")


if __name__ == "__main__":
    mcp.run(transport="streamable-http")

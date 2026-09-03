# FPL MCP

A small read-only Model Context Protocol server exposing Fantasy Premier League data to Claude through Composio.

## Architecture

Claude → Composio → Custom MCP → Official/public FPL API

## Tools

- `get_fpl_status`
- `get_players`
- `get_fixtures`
- `get_manager`
- `get_manager_history`
- `get_manager_picks`
- `get_manager_transfers`
- `get_player_summary`
- `get_live_gameweek`

The server is intentionally a **data layer**. It does not make transfer, captaincy or chip decisions.

## Local run

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python server.py
```

The MCP endpoint is exposed at `/mcp` using Streamable HTTP.

## Default manager

Set `FPL_DEFAULT_MANAGER_ID` to avoid passing the manager ID to every manager-specific tool. Otherwise provide `manager_id` explicitly.

Do not store FPL passwords or session cookies in this repository.

## Deployment

Deploy the container to a host that provides public HTTPS. Then register the resulting `/mcp` endpoint as a Custom MCP in Composio.

The server uses Streamable HTTP, the current recommended network transport for MCP deployments.

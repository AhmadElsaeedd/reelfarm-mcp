# ReelFarm MCP Server

An [MCP (Model Context Protocol)](https://modelcontextprotocol.io/) server for the [ReelFarm API](https://reel.farm/api-docs). Create slideshows, manage automations, publish to TikTok, search Pinterest for images, and more — all from any MCP-compatible AI client.

## Tools

**25 tools** covering the full ReelFarm API:

| Category | Tools |
|---|---|
| **Account** | `get_account` |
| **Slideshows** | `generate_slideshow`, `create_slideshow`, `slideshow_status` |
| **Automations** | `create_automation`, `list_automations`, `get_automation`, `update_automation`, `delete_automation`, `run_automation` |
| **Schedules** | `add_schedule`, `update_schedule`, `delete_schedule` |
| **Videos** | `list_videos`, `get_video`, `get_video_analytics`, `publish_video_via_automation` |
| **TikTok** | `publish_to_tiktok`, `list_tiktok_accounts`, `list_tiktok_posts` |
| **Collections** | `list_collections`, `get_collection_images` |
| **Library** | `list_library_niches`, `search_library`, `get_library_profile` |
| **Pinterest** | `search_pinterest` |

## Prerequisites

- Python 3.10+
- [uv](https://docs.astral.sh/uv/getting-started/installation/) (recommended) or pip
- A ReelFarm account on the **Growth**, **Scale**, or **Enterprise** plan
- A ReelFarm API key — get yours from [Dashboard → Settings → API Keys](https://reel.farm/dashboard)

## Quick Start

Pick your MCP client below. Each section has a complete, copy-paste config. Replace `rf_your_api_key_here` with your actual API key.

---

### Claude Desktop

Open **Claude** → **Settings** → **Developer** → **Edit Config** to open the config file:

| OS | Config path |
|---|---|
| macOS | `~/Library/Application Support/Claude/claude_desktop_config.json` |
| Windows | `%APPDATA%\Claude\claude_desktop_config.json` |

Add `"reelfarm"` inside the `"mcpServers"` object:

```json
{
  "mcpServers": {
    "reelfarm": {
      "command": "uvx",
      "args": ["reelfarm-mcp-server"],
      "env": {
        "REELFARM_API_KEY": "rf_your_api_key_here"
      }
    }
  }
}
```

Restart Claude Desktop. You should see a hammer icon in the chat input indicating the tools are loaded.

<details>
<summary>Using a local clone instead of the published package</summary>

```json
{
  "mcpServers": {
    "reelfarm": {
      "command": "uv",
      "args": [
        "run",
        "--directory", "/absolute/path/to/reelfarm-mcp",
        "reelfarm-mcp"
      ],
      "env": {
        "REELFARM_API_KEY": "rf_your_api_key_here"
      }
    }
  }
}
```

</details>

---

### Claude Code (CLI)

```bash
claude mcp add reelfarm \
  -e REELFARM_API_KEY=rf_your_api_key_here \
  -- uvx reelfarm-mcp-server
```

Verify it's registered:

```bash
claude mcp list
```

<details>
<summary>Using a local clone instead</summary>

```bash
claude mcp add reelfarm \
  -e REELFARM_API_KEY=rf_your_api_key_here \
  -- uv run --directory /absolute/path/to/reelfarm-mcp reelfarm-mcp
```

</details>

---

### Cursor

Open **Settings** → **MCP** → **Add new MCP server**, or manually edit `.cursor/mcp.json` in your project root:

```json
{
  "mcpServers": {
    "reelfarm": {
      "command": "uvx",
      "args": ["reelfarm-mcp-server"],
      "env": {
        "REELFARM_API_KEY": "rf_your_api_key_here"
      }
    }
  }
}
```

Reload the window (`Cmd+Shift+P` → **Developer: Reload Window**) and you'll see the tools in the MCP panel.

<details>
<summary>Using a local clone instead</summary>

```json
{
  "mcpServers": {
    "reelfarm": {
      "command": "uv",
      "args": [
        "run",
        "--directory", "/absolute/path/to/reelfarm-mcp",
        "reelfarm-mcp"
      ],
      "env": {
        "REELFARM_API_KEY": "rf_your_api_key_here"
      }
    }
  }
}
```

</details>

---

### Windsurf

Open **Windsurf Settings** → **Cascade** → **MCP** → **Add Server** → **Add custom server**, or edit `~/.codeium/windsurf/mcp_config.json`:

```json
{
  "mcpServers": {
    "reelfarm": {
      "command": "uvx",
      "args": ["reelfarm-mcp-server"],
      "env": {
        "REELFARM_API_KEY": "rf_your_api_key_here"
      }
    }
  }
}
```

---

### VS Code (Copilot)

Add to your user or workspace settings (`.vscode/mcp.json`):

```json
{
  "servers": {
    "reelfarm": {
      "command": "uvx",
      "args": ["reelfarm-mcp-server"],
      "env": {
        "REELFARM_API_KEY": "rf_your_api_key_here"
      }
    }
  }
}
```

---

### Any other MCP client (generic stdio)

The server communicates over **stdio**. Point your MCP client at:

```bash
REELFARM_API_KEY=rf_your_api_key_here uvx reelfarm-mcp-server
```

Or if installed via pip:

```bash
REELFARM_API_KEY=rf_your_api_key_here reelfarm-mcp
```

---

## Installation (alternative to uvx)

If you prefer installing the package directly rather than using `uvx`:

```bash
pip install reelfarm-mcp-server
```

Then use `"command": "reelfarm-mcp"` (no args) in any of the configs above instead of `uvx`.

## Usage Examples

Once connected, you can ask your AI assistant things like:

- "Generate a slideshow about 5 morning habits, casual tone, 6 slides"
- "List my automations and show which ones are active"
- "Create an automation that posts fitness slideshows to TikTok every day at 2pm Pacific"
- "Show me my TikTok post analytics for the last 30 days sorted by views"
- "Search Pinterest for aesthetic coffee images"
- "What niches are available in the slideshow library?"
- "How many credits do I have left?"

## API Rate Limits

- **20 requests** per 60-second sliding window
- **Max 3 slideshows** generating simultaneously

## Development

```bash
git clone https://github.com/reelfarm/reelfarm-mcp.git
cd reelfarm-mcp
uv sync

# Run the server locally
REELFARM_API_KEY=rf_your_key uv run reelfarm-mcp
```

## Troubleshooting

| Problem | Fix |
|---|---|
| `uvx: command not found` | Install uv: `curl -LsSf https://astral.sh/uv/install.sh \| sh` |
| Tools don't appear after config change | Restart the app (Claude Desktop, Cursor, etc.) |
| `REELFARM_API_KEY is not set` | Double-check the `env` block in your config — the key must start with `rf_` |
| `FastMCP.__init__() got an unexpected keyword argument` | Your `mcp` SDK is outdated or too new. Run `uv sync` to get compatible versions |
| Server seems to hang when run directly | This is normal — MCP servers communicate over stdio and produce no terminal output. Your MCP client launches it automatically |

## License

MIT — see [LICENSE](LICENSE).

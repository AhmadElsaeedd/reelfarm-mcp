# ReelFarm MCP Server

An [MCP (Model Context Protocol)](https://modelcontextprotocol.io/) server for the [ReelFarm API](https://reel.farm/api-docs). Create slideshows, manage automations, publish to TikTok, search Pinterest for images, and more — all from Claude, Cursor, or any MCP client.

## Features

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
- A ReelFarm account on the **Growth**, **Scale**, or **Enterprise** plan
- A ReelFarm API key (get it from Dashboard → Settings → API Keys)

## Installation

### Using pip

```bash
pip install reelfarm-mcp-server
```

### From source

```bash
git clone https://github.com/YOUR_USERNAME/reelfarm-mcp-server.git
cd reelfarm-mcp-server
pip install -e .
```

## Configuration

Set your API key as an environment variable:

```bash
export REELFARM_API_KEY=rf_your_api_key_here
```

### Claude Desktop

Add to your Claude Desktop config (`~/Library/Application Support/Claude/claude_desktop_config.json` on macOS):

```json
{
  "mcpServers": {
    "reelfarm": {
      "command": "reelfarm-mcp",
      "env": {
        "REELFARM_API_KEY": "rf_your_api_key_here"
      }
    }
  }
}
```

### Claude Code

```bash
claude mcp add reelfarm -- reelfarm-mcp
```

Then set `REELFARM_API_KEY` in your environment.

### Cursor

Add to your Cursor MCP settings (`.cursor/mcp.json`):

```json
{
  "mcpServers": {
    "reelfarm": {
      "command": "reelfarm-mcp",
      "env": {
        "REELFARM_API_KEY": "rf_your_api_key_here"
      }
    }
  }
}
```

## Usage Examples

Once connected, you can ask Claude things like:

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
git clone https://github.com/YOUR_USERNAME/reelfarm-mcp-server.git
cd reelfarm-mcp-server
pip install -e ".[dev]"

# Run the server locally
REELFARM_API_KEY=rf_your_key reelfarm-mcp
```

## License

MIT — see [LICENSE](LICENSE).

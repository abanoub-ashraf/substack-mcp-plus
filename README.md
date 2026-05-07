# Substack MCP Plus

An MCP server for Substack that lets AI clients work with your publication and research public Substack content.

It supports:
- authenticated account tools for drafts, publishing, scheduling, previews, sections, and post analytics
- public research tools for finding, analyzing, and studying Substack posts and publications
- content strategy tools for ideas, hooks, repurposing, gap analysis, and series planning

This project is unofficial and is not affiliated with Substack Inc.

## What You Can Do

With your own Substack account:
- create formatted drafts
- update drafts
- publish immediately
- schedule future posts
- list drafts, published posts, and scheduled posts
- preview drafts
- upload images
- inspect sections
- read post content
- get post analytics

With public Substack content:
- research a topic across Substack
- analyze a public post URL
- analyze a publication URL
- create a study plan around a topic
- extract coding lessons from public posts

For strategy:
- analyze your own posts
- generate post ideas
- repurpose posts into other formats
- run content gap analysis
- improve titles and hooks
- plan a series

## Requirements

- `Node.js >= 16`
- `Python >= 3.10`
- a Substack publication URL such as `https://yourpublication.substack.com`

## Install

Install globally with npm:

```bash
npm install -g @abanoub-ashraf/substack-mcp-plus
```

This installs two commands:

```bash
substack-mcp-plus
substack-mcp-plus-setup
```

## First-Time Setup

Run the setup wizard:

```bash
substack-mcp-plus-setup
```

The setup flow will:
- open a browser
- let you sign in to Substack
- handle CAPTCHA/manual login flow
- store an encrypted browser session locally for later use

The local auth file lives at `~/.substack-mcp-plus/auth.json`. The setup stores
the browser session cookie jar after login, not your Substack password.

If Substack sends an email sign-in link, open or paste that link in the same
browser window opened by `substack-mcp-plus-setup`. That same-browser step is
what lets the setup capture the final authenticated session.

If your client later says authentication failed, run the setup again.

## MCP Client Config

Use this server in any MCP client that supports a stdio server definition.

Server block:

```json
{
  "mcpServers": {
    "substack-mcp-plus": {
      "command": "substack-mcp-plus",
      "env": {
        "SUBSTACK_PUBLICATION_URL": "https://YOUR_PUBLICATION.substack.com"
      }
    }
  }
}
```

If your GUI client does not inherit your shell `PATH`, use an absolute path instead:

```bash
which substack-mcp-plus
```

Then replace `"substack-mcp-plus"` with the full path to the binary.

### Client Notes

- Claude Desktop
  Config file locations:
  - macOS: `~/Library/Application Support/Claude/claude_desktop_config.json`
  - Windows: `%APPDATA%\\Claude\\claude_desktop_config.json`
  - Linux: `~/.config/Claude/claude_desktop_config.json`
- Claude Code
  Add the same `mcpServers.substack-mcp-plus` block to `~/.claude.json`.
- Codex
  Add this to `~/.codex/config.toml`:

  ```toml
  [mcp_servers.substack-mcp-plus]
  command = "substack-mcp-plus"

  [mcp_servers.substack-mcp-plus.env]
  SUBSTACK_PUBLICATION_URL = "https://YOUR_PUBLICATION.substack.com"
  ```
- Cursor
  Add the same server block anywhere Cursor expects MCP server JSON.
- Antigravity
  Add the same server block anywhere Antigravity expects MCP server JSON.
- Windsurf
  Add the same server block anywhere Windsurf expects MCP server JSON.
- Generic MCP client
  Use the same stdio definition if the client supports `command` + `env`.

After updating the config, fully restart the client.

## Tool List

### Publishing and Account Tools

- `create_formatted_post`
- `update_post`
- `publish_post`
- `schedule_post`
- `list_drafts`
- `list_published`
- `list_scheduled_posts`
- `get_post_content`
- `get_post_analytics`
- `duplicate_post`
- `preview_draft`
- `upload_image`
- `delete_draft`
- `get_sections`
- `get_subscriber_count`

### Public Research Tools

- `research_substack`
- `research_substack_post`
- `research_substack_publication`
- `study_topic_on_substack`
- `extract_coding_lessons`

### Strategy Tools

- `analyze_my_posts`
- `generate_post_ideas`
- `repurpose_post`
- `content_gap_analysis`
- `title_and_hook_optimizer`
- `series_planner`

## Example Prompts

### Account Workflows

- `List my latest drafts`
- `Show me my scheduled posts`
- `Get the content of draft 123456`
- `Create a draft titled "Why SwiftUI image caching matters" with markdown content`
- `Schedule draft 123456 for 2026-03-12T09:00:00Z`
- `Show analytics for published post 123456`

### Research Workflows

- `Research Substack for swiftui image caching`
- `Research this Substack post: https://www.oneusefulthing.org/p/change-blindness`
- `Research this publication: https://oneusefulthing.substack.com`
- `Study SwiftUI performance on Substack`
- `Extract coding lessons from https://example.substack.com/p/some-post`

### Strategy Workflows

- `Analyze my posts`
- `Generate post ideas for indie iOS app marketing`
- `Repurpose my latest draft into a Twitter thread`
- `Improve the title and hook for post 123456`
- `Plan a 5-part series on Swift concurrency`

## Notes About Confirmation

Some write actions are intentionally confirmation-oriented. For high-impact actions like create, update, publish, schedule, duplicate, and delete, the client should confirm before the final action is sent.

## Known Limitations

These are the current honest limits, not marketing wallpaper:

- `get_subscriber_count` may return an unavailable state if Substack does not expose a reliable count through publication metadata, page markup, or section data.
- Public research works best on focused queries such as `swiftui image caching` or `ios concurrency` rather than very broad topics.
- Broad-topic discovery can still have lower recall than niche queries.
- `study_topic_on_substack` and `extract_coding_lessons(query=...)` depend on the quality of the underlying discovery results.
- Public research tools only work on public pages that are reachable and parseable.

## Troubleshooting

### Command not found

Your client may not inherit your shell `PATH`.

Find the installed binary:

```bash
which substack-mcp-plus
```

Then use the absolute path in the client config.

### Authentication failed

Run setup again:

```bash
substack-mcp-plus-setup
```

If Substack sent a sign-in email, paste the email link into the same setup
browser window before closing it.

### MCP shows connected but tools do not appear

This is usually a client session cache issue.

Do this:
- fully quit the MCP client
- reopen it
- start a fresh session

### Research results are weak or empty

Try a narrower query.

Better:
- `swiftui image loading`
- `swiftui asyncimage`
- `ios monetization`

Usually weaker:
- `AI for work`
- `coding`
- `productivity`

### GUI client still cannot launch the server

Use an absolute command path instead of `substack-mcp-plus`.

## Development

Install editable Python dependencies in the project venv:

```bash
./venv/bin/python -m pip install -e '.[dev]'
```

Run tests:

```bash
./venv/bin/python -m pytest -q
```

Run the server directly:

```bash
node src/index.js
```

## Security

- Do not commit tokens, passwords, or private keys.
- Prefer interactive setup over hardcoded credentials.
- Stored browser session data is encrypted under `~/.substack-mcp-plus/`.
- Use obvious placeholders in configs and examples.
- Re-run authentication if a stored Substack session expires.

See [SECURITY.md](SECURITY.md) for project security notes.

## License

[MIT](LICENSE)

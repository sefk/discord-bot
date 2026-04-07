# discord-bot

A Discord bot that bridges a Discord channel to Claude Code. Send messages from Discord, get responses back. A local tmux session shows a live log of the conversation.

## How it works

- Each Discord message invokes `claude -p --continue` as a subprocess, capturing the response directly from stdout
- Conversation context is preserved across messages via Claude's `--continue` flag
- The bot runs in a tmux session (`discord-bot`)
- A second tmux session (`claude`) tails the log at `/tmp/claude-vm.log` — attach to it to watch tool use and conversation history in real time

## Prerequisites

- [Claude Code](https://claude.ai/code) CLI installed and authenticated
- Python 3 with `discord.py` (`pip install -r requirements.txt`)
- tmux
- A Discord bot token (see Setup below)

## Setup

### 1. Discord bot

1. Go to [discord.com/developers/applications](https://discord.com/developers/applications) → **New Application**
2. **Bot** → **Add Bot** → copy the token
3. Under **Privileged Gateway Intents**, enable **Message Content Intent**
4. **OAuth2 → URL Generator** → scope: `bot`, permissions: `Send Messages` + `Read Message History`
5. Open the generated URL and invite the bot to your server

### 2. Environment

Add to `~/.zsh_secret`:

```sh
export DISCORD_WEBHOOK_URL=<your-webhook-url>   # for Claude Code hooks (optional)
export DISCORD_BOT_TOKEN=<your-bot-token>
```

### 3. Claude Code hooks (optional)

To get pinged in Discord when Claude stops or needs input, add to Claude Code's `settings.json`:

```json
{
  "hooks": {
    "Notification": [{"command": "curl -s -X POST $DISCORD_WEBHOOK_URL -H 'Content-Type: application/json' -d '{\"content\": \"**[Claude needs input]**\"}'"}],
    "Stop": [{"command": "curl -s -X POST $DISCORD_WEBHOOK_URL -H 'Content-Type: application/json' -d '{\"content\": \"**[Claude stopped]**\"}'"}]
  }
}
```

## Running manually

```sh
zsh ./sandbox/claude-vm.sh start
tmux attach -t claude   # watch the log
```

## Auto-start on login

A LaunchAgent is installed at `~/Library/LaunchAgents/com.sefkbot.claude-discord.plist`. It runs `sandbox/claude-vm.sh start` (from the repo root) at login, which starts both tmux sessions if they aren't already running.

To reload after changes:

```sh
launchctl unload ~/Library/LaunchAgents/com.sefkbot.claude-discord.plist
launchctl load ~/Library/LaunchAgents/com.sefkbot.claude-discord.plist
```

Startup logs: `/tmp/claude-discord-startup.log`
Claude conversation log: `/tmp/claude-vm.log`

## Configuration

In `bot.py`:

| Variable | Default | Description |
|---|---|---|
| `CHANNEL_NAME` | `bot` | Discord channel to listen on. |
| `LOG_FILE` | `/tmp/claude-vm.log` | Path to the conversation log (tailed by the `claude` tmux session). |
| `MAX_LEN` | `2000` | Discord message length limit for chunking long responses. |

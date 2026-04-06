# discord-bot

A Discord bot that bridges a Discord channel to an interactive Claude Code session running in tmux. Send messages from Discord, get responses back. The same Claude session is also visible and interactive in a local Ghostty terminal.

## How it works

- Claude runs interactively in a tmux session (`claude`)
- The bot runs in a second tmux session (`discord-bot`)
- Messages posted in the `#bot` channel are sent to Claude via `tmux send-keys`
- The bot polls `tmux capture-pane` until output stabilizes, then posts the response back to Discord
- You can attach to the `claude` session locally at any time to watch or type alongside it

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
# Start Claude session
tmux new-session -d -s claude 'claude --dangerously-skip-permissions'

# Attach in Ghostty to watch/interact locally
tmux attach -t claude

# Start the bot (in a separate terminal)
source ~/.zsh_secret
tmux new-session -d -s discord-bot 'cd ~/src/discord-bot && python3 bot.py'
```

## Auto-start on login

A LaunchAgent is installed at `~/Library/LaunchAgents/com.sefkbot.claude-discord.plist`. It runs `start.sh` (in this directory) at login, which starts both tmux sessions if they aren't already running.

To reload after changes:

```sh
launchctl unload ~/Library/LaunchAgents/com.sefkbot.claude-discord.plist
launchctl load ~/Library/LaunchAgents/com.sefkbot.claude-discord.plist
```

Startup logs: `/tmp/claude-discord-startup.log`

## Tuning

In `bot.py`:

| Variable | Default | Description |
|---|---|---|
| `STABLE_SECS` | `2.0` | Seconds of no pane change before response is considered complete. Increase if responses feel cut off. |
| `POLL_SECS` | `0.5` | How often to check the pane. |
| `TIMEOUT_SECS` | `300` | Max wait time before giving up. |
| `CHANNEL_NAME` | `bot` | Discord channel to listen on. |
| `TMUX_SESSION` | `claude` | tmux session name for the Claude process. |

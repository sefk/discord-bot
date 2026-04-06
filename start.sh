#!/bin/zsh -l
source $HOME/.zsh_secret

# Start Claude session if not already running
if ! tmux has-session -t claude 2>/dev/null; then
    tmux new-session -d -s claude 'claude --dangerously-skip-permissions'
    sleep 2  # give Claude a moment to initialize
fi

# Start Discord bot if not already running
if ! tmux has-session -t discord-bot 2>/dev/null; then
    tmux new-session -d -s discord-bot "cd $HOME/src/discord-bot && python3 bot.py"
fi

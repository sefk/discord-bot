#!/bin/zsh -l
source $HOME/.zsh_secret
VERB=${1:-start}
if [[ $VERB == start || $VERB == restart ]]; then
    ssh-add ~/.ssh/sefkbot-github-20260331
fi

do_stop() {
    tmux kill-session -t claude 2>/dev/null && echo "Stopped: claude" || echo "Not running: claude"
    tmux kill-session -t discord-bot 2>/dev/null && echo "Stopped: discord-bot" || echo "Not running: discord-bot"
}

do_start() {
    if ! tmux has-session -t claude 2>/dev/null; then
        touch /tmp/claude-vm.log
        tmux new-session -d -s claude 'tail -f /tmp/claude-vm.log'
        echo "Started: claude"
    else
        echo "Already running: claude"
    fi

    if ! tmux has-session -t discord-bot 2>/dev/null; then
        tmux new-session -d -s discord-bot "cd $HOME/src/discord-bot/sandbox && python3 bot.py >> /tmp/discord-bot.log 2>&1"
        echo "Started: discord-bot"
    else
        echo "Already running: discord-bot"
    fi
}

do_status() {
    tmux has-session -t claude 2>/dev/null && echo "Running: claude" || echo "Stopped: claude"
    tmux has-session -t discord-bot 2>/dev/null && echo "Running: discord-bot" || echo "Stopped: discord-bot"
}

case $VERB in
    start)   do_start ;;
    stop)    do_stop ;;
    restart) do_stop; do_start ;;
    status)  do_status ;;
    tail)    tail -f /tmp/claude-vm.log ;;
    help)    echo "Usage: $0 {start|stop|restart|status|tail|help}" ;;
    *) echo "Usage: $0 {start|stop|restart|status|tail|help}"; exit 1 ;;
esac

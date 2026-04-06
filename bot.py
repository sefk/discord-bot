#!/usr/bin/env python3
import discord
import asyncio
import subprocess
import os
import time

TOKEN = os.environ['DISCORD_BOT_TOKEN']
CHANNEL_NAME = 'bot'
TMUX_SESSION = 'claude'
MAX_LEN = 2000
STABLE_SECS = 2.0   # seconds of no change = Claude is done
POLL_SECS = 0.5
TIMEOUT_SECS = 300

intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)


def tmux_capture():
    result = subprocess.run(
        ['tmux', 'capture-pane', '-p', '-t', TMUX_SESSION],
        capture_output=True, text=True,
    )
    return result.stdout


def tmux_send(text):
    # -l sends literal characters (handles special chars safely)
    subprocess.run(['tmux', 'send-keys', '-t', TMUX_SESSION, '-l', text])
    subprocess.run(['tmux', 'send-keys', '-t', TMUX_SESSION, 'Enter'])


def extract_response(sent, after):
    lines = after.split('\n')
    # Find the last line that contains what we sent
    msg_idx = None
    for i in range(len(lines) - 1, -1, -1):
        if sent.strip() in lines[i]:
            msg_idx = i
            break
    if msg_idx is None:
        return after.strip()
    response_lines = lines[msg_idx + 1:]
    # Strip trailing prompt/empty lines
    while response_lines and (not response_lines[-1].strip()
                               or response_lines[-1].strip().startswith('>')):
        response_lines.pop()
    return '\n'.join(response_lines).strip()


async def wait_for_stable():
    """Poll pane until content stops changing for STABLE_SECS."""
    await asyncio.sleep(1.0)  # let Claude start processing
    last = tmux_capture()
    last_change = time.monotonic()
    start = time.monotonic()

    while time.monotonic() - start < TIMEOUT_SECS:
        await asyncio.sleep(POLL_SECS)
        current = tmux_capture()
        if current != last:
            last = current
            last_change = time.monotonic()
        elif time.monotonic() - last_change >= STABLE_SECS:
            return current

    return tmux_capture()  # timeout fallback


@client.event
async def on_ready():
    print(f'Logged in as {client.user}')


@client.event
async def on_message(message):
    if message.author.bot:
        return
    if message.channel.name != CHANNEL_NAME:
        return

    async with message.channel.typing():
        tmux_send(message.content)
        after = await wait_for_stable()
        response = extract_response(message.content, after)

    if not response:
        response = '(no response captured)'

    for i in range(0, len(response), MAX_LEN):
        await message.channel.send(response[i:i + MAX_LEN])


client.run(TOKEN)

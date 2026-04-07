#!/usr/bin/env python3
import discord
import asyncio
import subprocess
import os

TOKEN = os.environ['DISCORD_BOT_TOKEN']
CHANNEL_NAME = 'bot'
MAX_LEN = 2000
LOG_FILE = '/tmp/claude-vm.log'

intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)


def run_claude(message):
    env = os.environ.copy()
    env['CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC'] = '1'

    with open(LOG_FILE, 'a') as log:
        log.write(f'\n--- User: {message}\n--- Claude:\n')
        log.flush()
        result = subprocess.run(
            ['claude', '-p', '--dangerously-skip-permissions', '--continue', message],
            stdout=subprocess.PIPE,
            stderr=log,
            text=True,
            env=env,
        )
        log.write(result.stdout)
        log.write('\n')

    return result.stdout.strip() or '(no response)'


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
        loop = asyncio.get_event_loop()
        response = await loop.run_in_executor(None, run_claude, message.content)

    for i in range(0, len(response), MAX_LEN):
        await message.channel.send(response[i:i + MAX_LEN])


client.run(TOKEN)

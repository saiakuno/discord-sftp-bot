import paramiko
import json
import asyncio
import discord
import os

HOST = os.getenv("SFTP_HOST")
PORT = int(os.getenv("SFTP_PORT", "2022"))
USERNAME = os.getenv("SFTP_USER")
PASSWORD = os.getenv("SFTP_PASS")
REMOTE_PATH = os.getenv("SFTP_JSON_PATH")

intents = discord.Intents.default()
client = discord.Client(intents=intents)

async def update_status():
    while True:
        try:
            transport = paramiko.Transport((HOST, PORT))
            transport.connect(username=USERNAME, password=PASSWORD)
            sftp = paramiko.SFTPClient.from_transport(transport)

            with sftp.open(REMOTE_PATH, 'r') as remote_file:
                data = json.load(remote_file)

            sftp.close()
            transport.close()

            year = data.get("year", "?")
            season = data.get("season", "?").capitalize()
            day = data.get("day", "?")
            players = data.get("onlinePlayers", [])

            players_list = ", ".join(players) if players else "No one"
            status_message = f"Year {year}, {season} {day} | Online: {players_list}"

            await client.change_presence(activity=discord.Game(name=status_message))
            print("Updated status:", status_message)

        except Exception as e:
            print("Error reading JSON or updating status:", e)

        await asyncio.sleep(15)

@client.event
async def on_ready():
    print(f'Logged in as {client.user}')
    client.loop.create_task(update_status())

client.run(os.getenv("DISCORD_TOKEN"))

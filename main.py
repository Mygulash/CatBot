#importing libraries
import discord
import datetime
from discord.ext import tasks, commands
from discord import app_commands
import aiohttp
import os
import json
from dotenv import load_dotenv

#basic discord bot setup
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='/', intents=intents)

#defying the time that the bot sends the memes :D
target_time = datetime.time(hour=4, minute=0, second=0, tzinfo=datetime.timezone.utc)

#Creating a set where will the userids be stored
DATA_FILE = "users.json"
users = {}

def load_users():
    global users
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            raw_data = json.load(f)
            users = {int(user_id): amount for user_id, amount in raw_data.items()}
    else:
        users = {}

def save_users():
    with open(DATA_FILE, "w") as f:
        json.dump(users, f, indent=4)

load_users()

#Discord bot token 
load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

#starts the bot
@bot.event
async def on_ready():
    print(f'We have logged in as {bot.user}')

    try:
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} commands")
    except Exception as e:
        print(f"Error syncing commands: {e}")

    if not send_catmeme.is_running():
        send_catmeme.start()

#creates a command that tells the user some information about CatBot
@bot.tree.command(name="catinfo", description="Information about CatBot")
async def catinfo(interaction: discord.Interaction):
    embed = discord.Embed(
        title="🐾 CatBot Information", 
        description="I am CatBot and I send you cute cat memes every day!",
        color=discord.Color.blue()
    )
    embed.add_field(name="Developer", value="<@722839649046757497>", inline=True)
    embed.set_thumbnail(url=bot.user.display_avatar.url) 
    await interaction.response.send_message(embed=embed, ephemeral=True)

#creates a command for subscribing
@bot.tree.command(name = "subscribe", description = "Subscribe to receive cat memes every day!")
@app_commands.describe(amount = "The amount of memes you want to receive (1-10)")
async def subscribe(interaction: discord.Interaction, amount: app_commands.Range[int, 1, 10] = 1):
    if interaction.user.id in users:
        await interaction.response.send_message("You are already subscribed to receive memes ✨🐈", ephemeral=True)
        return
    users[interaction.user.id] = amount
    save_users()
    await interaction.response.send_message("You have subscribed to receive memes! ✨", ephemeral=True)

#creates a command for unsubscribing
@bot.tree.command(name = "unsubscribe", description = "Unsubscribe from receiving cat memes every day")
async def unsubscribe(interaction: discord.Interaction):
    if interaction.user.id not in users:
        await interaction.response.send_message("🟥You are not subscribed to receive memes D:", ephemeral=True)
        return
    del users[interaction.user.id]
    save_users()
    await interaction.response.send_message("You have unsubscribed from receiving memes :(", ephemeral=True)

#creates a command for chaning the amount of memes the user receives
@bot.tree.command(name = "changeamount", description = "Set the amount of memes you want to receive every day!")
@app_commands.describe(amount = "The amount of memes you want to receive (1-10)")
async def changeamount(interaction: discord.Interaction, amount: app_commands.Range[int, 1, 10]):
    if interaction.user.id not in users:
        await interaction.response.send_message("🟥You are not subscribed to receive memes D:", ephemeral=True)
        return
    users[interaction.user.id] = amount
    save_users()
    await interaction.response.send_message(f"🐈You have set the amount of cat memes to **{amount}**", ephemeral=True)

#creates a command to check how many memes does the user receive
@bot.tree.command(name = "checkamount", description = "Check the amount of memes you are receiving every day :O")
async def checkamount(interaction: discord.Interaction):
    if interaction.user.id not in users:
        await interaction.response.send_message("🟥You are not subscribed to receive memes D:", ephemeral=True)
        return
    amount = users[interaction.user.id]
    await interaction.response.send_message(f"🐈You are receiving **{amount}** cat memes every day!", ephemeral=True)

#creates a command to check the number of users
@bot.tree.command(name = "usersnum", description = "Check the number of subscribed users!")
async def usersnum(interaction: discord.Interaction):
    await interaction.response.send_message(f"📈Number of subscribed users: **{len(users)}**", ephemeral=True)

#creates a command that writes  the list of commands 
@bot.tree.command(name = "cathelp", description = "Check the list of commands")
async def cathelp(interaction: discord.Interaction):
    embed = discord.Embed(title="CatBot commands:", color=discord.Color.blue())
    embed.add_field(name="/catinfo", value="Get information about CatBot", inline=False)
    embed.add_field(name="/subscribe", value="Subscribe to receive cat memes!", inline=False)
    embed.add_field(name="/unsubscribe", value="Unsubscribe from receiving cat memes :(", inline=False)
    embed.add_field(name="/changeamount", value="Change the amount of cat memes you receive", inline=False)
    embed.add_field(name="/checkamount", value="Check the amount of cat memes you are receiving", inline=False)
    embed.add_field(name="/usersnum", value="Check the number of subscribed users :O", inline=False)
    embed.add_field(name="/cathelp", value="Check the list of commands", inline=False)
    await interaction.response.send_message(embed=embed, ephemeral=True)

#creates the main loop that send the meme evyry day on the specific time
@tasks.loop(time=target_time)
async def send_catmeme():
    print("ok1")

    if not users:
        return

    max_memes = max(users.values())

    async with aiohttp.ClientSession() as session:
        async with session.get(f"https://meme-api.com/gimme/Catmemes/{max_memes}") as response:
            print(response.status)
            if response.status == 200:
                data = await response.json()
                memes_urls = data.get("memes", [])

                for user_id, requested_memes in users.items():
                    user = await bot.fetch_user(user_id)

                    try:
                        users_memes = memes_urls[:requested_memes]

                        embeds = []
                        for meme in users_memes:
                            embed = discord.Embed(title=meme["title"], color=discord.Color.blue())
                            embed.set_image(url=meme["url"])
                            embeds.append(embed)

                        await user.send(embeds=embeds)
                    
                    except discord.Forbidden:
                        print(f"Could not send meme to {user.name} (ID: {user.id}). They might have DMs disabled.")

bot.run(TOKEN)

#importing libraries
import discord
import datetime
from discord.ext import tasks, commands
import aiohttp
import os
from dotenv import load_dotenv

#basic discord bot setup
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

#defying the time that the bot sends the memes :D
target_time = datetime.time(hour=12, minute=29, second=0, tzinfo=datetime.timezone.utc)

#Creating a set where will the userids be stored
users = set()

#Discord bot token 
load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

#starts the bot
@bot.event
async def on_ready():
    print(f'We have logged in as {bot.user}')
    if not send_catmeme.is_running():
        send_catmeme.start()

#creates a command for subscribing
@bot.command()
async def subscribe(ctx):
    users.add(ctx.author.id)
    await ctx.send("You have subscribed to receive memes!" + str(datetime.datetime.now()))

#creates a command for unsubscribing
@bot.command()
async def unsubscribe(ctx):
    users.discard(ctx.author.id)
    await ctx.send("You have unsubscribed from receiving memes.")

#creates a command to check the number of users
@bot.command()
async def usersnum(ctx):
    await ctx.send(f"Number of subscribed users: {len(users)}")

#creates the main loop that send the meme evyry day on the specific time
@tasks.loop(time=target_time)
async def send_catmeme():
    print("ok1")
    async with aiohttp.ClientSession() as session:
        async with session.get("https://meme-api.com/gimme/Catmemes") as response:
            print(response.status)
            if response.status == 200:
                data = await response.json()
                meme_url = data['url']

                for user_id in users:
                    print("ok2")
                    user = await bot.fetch_user(user_id)
                    await user.send(meme_url)

bot.run(TOKEN)

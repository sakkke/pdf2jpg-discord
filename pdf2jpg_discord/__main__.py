import discord
import os # default module
from dotenv import load_dotenv

import aiohttp
import tempfile
from pdf2image import convert_from_path
import io

load_dotenv() # load all the variables from the env file
intents = discord.Intents.default()
intents.message_content = True
bot = discord.Bot(intents=intents)

@bot.event
async def on_ready():
    print(f"{bot.user} is ready and online!")

@bot.event
async def on_message(message: discord.Message):
    if message.author == bot.user:
        return

    for attachment in message.attachments:
        if attachment.filename.endswith(".pdf"):
            async with aiohttp.ClientSession() as session:
                url = attachment.url
                async with session.get(url) as response:
                    if response.status == 200:
                        binary = await response.read()
                        with tempfile.NamedTemporaryFile(delete=False) as file:
                            file.write(binary)
                            pages = convert_from_path(file.name)
                            files: list[discord.File] = []
                            for i, page in enumerate(pages, 1):
                                with io.BytesIO(binary) as stream:
                                    page.save(stream, format="JPEG")
                                    stream.seek(0)
                                    files.append(discord.File(stream, "image.jpg"))
                                    if i % 10 == 0:
                                        await message.channel.send(files=files)
                                        files = []
                                    elif len(pages) == i:
                                        await message.channel.send(files=files)

@bot.slash_command(name="hello", description="Say hello to the bot")
async def hello(ctx: discord.ApplicationContext):
    await ctx.respond("Hey!")

bot.run(os.getenv('TOKEN')) # run the bot with the token

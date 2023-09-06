import discord
import os
import re
from discord.ext import commands
from dotenv import load_dotenv
from googletrans import Translator
from langdetect import detect
from server import run

load_dotenv()

intents = discord.Intents.all()
bot = commands.Bot(command_prefix='!', intents=intents)
translator = Translator()


def is_japanese_sentence(text):
    # Use langdetect to check if the language is likely Japanese
    try:
        return detect(text) == 'ja'
    except:
        return False

def translate_japanese_to_english(japanese_sentence):
    translated = translator.translate(japanese_sentence, src='ja', dest='en')
    return translated.text
    
def en_to_ja(s):
    return translator.translate(s, src='en', dest='ja').text

@bot.event
async def on_ready():
    print(f'{bot.user.name} has connected to Discord!')

@bot.event
async def on_message(message: discord.Message):
    if message.author == bot.user:
        return  # Don't respond to messages sent by the bot itself

    content = message.content

    if re.search(r"\bcanva\b", content):
        await message.reply("*canvas")

    if is_japanese_sentence(content):
        await message.add_reaction("🇯🇵")
        await message.reply(f"Japanese sentence detected. Translation:\n{translate_japanese_to_english(content)}")

    await bot.process_commands(message)

@bot.command(aliases=["trans"])
async def translate(ctx, *, sentence):
    await ctx.message.reply(en_to_ja(sentence))


if __name__ == "__main__":
    run()
    bot.run(os.getenv('DISCORD_TOKEN'))
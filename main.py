import discord
import os
import re
import requests
import sys
from discord.ext import commands
from dotenv import load_dotenv
# from googletrans import Translator
from langdetect import detect
from deepseek import get_response, translate, anime_girl
from server import setup
from utils import *

load_dotenv()

intents = discord.Intents.all()
bot = commands.Bot(command_prefix='!', intents=intents)
translator = None

is_beta = '--beta' in sys.argv

def is_japanese_sentence(text):
    # Use langdetect to check if the language is likely Japanese
    try:
        return detect(text) == 'ja'
    except:
        return False
    
def is_chinese_sentence(text):
    # Use langdetect to check if the language is likely Japanese
    try:
        return detect(text) in ['zh-cn', 'zh-tw']
    except:
        return False

def translate_japanese_to_english(japanese_sentence):
    translated = translator.translate(japanese_sentence, src='ja', dest='en')
    return translated.text
    
async def en_to_ja(s):
    return (await translate(s, "English", "Japanese"))

def filter_thinking(text, show_thinking=True):
    # if the message includes </think>, remove anything inside <think> and </think>
    # if show_thinking is True, remove the tags but keep the content, and add a thinking emoji

    if "</think>" in text:
        # Replace
        text = re.sub(r"^.*?</think>", "", text)

    else:
        text = "🤔 " + (text.replace("<think>", "").strip() if show_thinking else "")

    return text

@bot.event
async def on_ready():
    # await setup(bot)

    print(f'{bot.user.name} has connected to Discord!')

@bot.event
async def on_message(message: discord.Message):
    if message.author == bot.user:
        return  # Don't respond to messages sent by the bot itself

    content = message.content

    if re.search(r"\bcanva\b", content):
        await message.reply("*canvas")

    if message.channel.id == 1346382017599897640:
        generator = await anime_girl(content)

        msg = None
        full_content = ""

        i = 0
        refresh = True

        async for part in generator:
            part_content = part["message"]["content"]
            
            if len(full_content) + len(part_content) > 2000:
                full_content = part_content
                refresh = True
            else:
                full_content += part_content

            i += 1

            if i % 3 != 0:
                continue

            if not full_content:
                continue

            if refresh:
                msg = await message.reply((full_content))
                refresh = False
            else:
                await msg.edit(content=(full_content))


        await msg.edit(content=(full_content))

        return

    if is_chinese_sentence(content):
        await message.add_reaction("🇨🇳")
        await message.reply(f"Chinese sentence detected. Translation:\n{await translate(content, "Chinese", "English")}")
    elif is_japanese_sentence(content):
        await message.add_reaction("🇯🇵")
        await message.reply(f"Japanese sentence detected. Translation:\n{await translate(content, "Japanese", "English")}")

    await bot.process_commands(message)

@bot.command(aliases=["trans", "t"])
async def _translate(ctx: commands.Context, target_lang, *, sentence):
    await ctx.message.reply(await translate(sentence, get_source_lang(sentence), target_lang))

@bot.command(aliases=["manualtranslate", "mantrans", "mt"])
async def _manual_translate(ctx: commands.Context, lang1, lang2, *, sentence):
    await ctx.message.reply(await translate(sentence, lang1, lang2))

@bot.command(aliases=["prompt"])
async def llama(ctx: commands.Context, *, prompt_input):
    generator = await get_response(prompt_input)

    message = None
    full_content = ""

    i = 0
    refresh = True

    async for part in generator:
        part_content = part["message"]["content"]
        
        if len(full_content) + len(part_content) > 2000:
            full_content = part_content
            refresh = True
        else:
            full_content += part_content

        i += 1

        if i % 3 != 0:
            continue

        if not full_content:
            continue

        if refresh:
            message = await ctx.reply((full_content))
            refresh = False
        else:
            await message.edit(content=(full_content))


    await message.edit(content=(full_content))

@bot.command(aliases=["nimi"])
async def toki(ctx, lang, *, sentence=""):
    response = requests.get("https://linku.la/jasima/data.json").json()

    # languages = response["languages"]
    languages = ["en", "zh_hans", "zh_hant"]

    lang = lang.lower()
    if lang not in languages:
        sentence = lang + " " + sentence
        lang = "zh_hans"

    data = response["data"]

    definitions = {}

    for word in sentence.strip().split():
        definitions[word] = data[word]["def"][lang]

    await ctx.reply("\n".join(f"- {word}: {definition}" for word, definition in definitions.items()))

if __name__ == "__main__":
    token = os.getenv('DISCORD_TOKEN_BETA') if is_beta else os.getenv('DISCORD_TOKEN')
    bot.run(token)
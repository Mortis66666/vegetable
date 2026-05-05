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
from log import log as print
from polls import add_poll, create_poll, get_poll, rate_poll, messagify_poll

load_dotenv()

intents = discord.Intents.all()
bot = commands.Bot(command_prefix="!", intents=intents)
translator = None

is_beta = "--beta" in sys.argv


def is_japanese_sentence(text):
    # Use langdetect to check if the language is likely Japanese
    try:
        return detect(text) == "ja"
    except:
        return False


def is_chinese_sentence(text):
    # Use langdetect to check if the language is likely Japanese
    try:
        return detect(text) in ["zh-cn", "zh-tw"]
    except:
        return False


def translate_japanese_to_english(japanese_sentence):
    translated = translator.translate(japanese_sentence, src="ja", dest="en")
    return translated.text


async def en_to_ja(s):
    return await translate(s, "English", "Japanese")


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

    print(f"{bot.user.name} has connected to Discord!")


@bot.event
async def on_message(message: discord.Message):
    if message.author == bot.user:
        return  # Don't respond to messages sent by the bot itself

    content = message.content

    if re.search(r"\bcanva\b", content):
        await message.reply("*canvas")

    if (
        message.channel.id == 1346382017599897640
        and not content.startswith("/unanime")
        and not content.startswith("/ua")
    ):
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
        await message.reply(
            f"Chinese sentence detected. Translation:\n{await translate(content, 'Chinese', 'English')}"
        )
    elif is_japanese_sentence(content):
        await message.add_reaction("🇯🇵")
        await message.reply(
            f"Japanese sentence detected. Translation:\n{await translate(content, 'Japanese', 'English')}"
        )

    await bot.process_commands(message)


@bot.command(aliases=["trans", "t"])
async def _translate(ctx: commands.Context, target_lang, *, sentence):
    await ctx.message.reply(
        await translate(sentence, get_source_lang(sentence), target_lang)
    )


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

    await ctx.reply(
        "\n".join(f"- {word}: {definition}" for word, definition in definitions.items())
    )


@bot.command(aliases=["poll", "pl"])
async def _poll(ctx, question, *options):
    poll = create_poll(question, list(options), ctx.author.id)
    poll_embed = messagify_poll(poll, ctx.author)
    poll_message = await ctx.send(embed=poll_embed)

    add_poll(poll_message.id, poll)

    await ctx.message.delete()


@bot.command(aliases=["ratepoll", "rp", "rate", "r"])
async def _rate_poll(ctx, *values):
    try:
        values = list(map(float, values))
    except ValueError:
        return await ctx.reply("Invalid values provided, please provide numbers.")

    poll_message = ctx.message.reference
    print(ctx.message.reference)
    if not poll_message:
        return await ctx.reply("Please reply to a poll message to rate it.")

    message_id = poll_message.message_id

    success, response = rate_poll(message_id, ctx.author.id, values)
    if not success:
        return await ctx.reply(response)

    await ctx.message.delete()

    actual_message = await ctx.channel.fetch_message(message_id)
    poll_data = get_poll(message_id)
    # Fetch the author if stored as ID
    author = None
    if poll_data and "author_id" in poll_data:
        try:
            author = await bot.fetch_user(poll_data["author_id"])
        except:
            pass
    poll_embed = messagify_poll(poll_data, author)
    await actual_message.edit(content=None, embed=poll_embed)


@bot.command(aliases=["ping", "p"])
async def _ping(ctx: commands.Context):
    """Ping the bot to check if it's alive. Also sends the latency."""
    latency = round(bot.latency * 1000)
    await ctx.send(f"Pong! 🏓 **Latency: {latency}ms**")


if __name__ == "__main__":
    token = os.getenv("DISCORD_TOKEN_BETA") if is_beta else os.getenv("DISCORD_TOKEN")
    bot.run(token)

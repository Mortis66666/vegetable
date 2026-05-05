import discord
import json
from functools import reduce
from operator import add

data_file = "polls.json"


def load_polls():
    try:
        with open(data_file, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}


def save_polls(polls):
    with open(data_file, "w") as f:
        json.dump(polls, f)


def get_poll(message_id):
    polls = load_polls()
    return polls.get(str(message_id))


def create_poll(question, options, author_id=None):
    return {
        "question": question,
        "options": options,
        "rates": {},
        "author_id": author_id,
    }


def add_poll(poll_id, poll):
    polls = load_polls()
    polls[str(poll_id)] = poll
    save_polls(polls)


def rate_poll(message_id, user_id, values):
    polls = load_polls()
    poll = polls.get(str(message_id))
    if not poll:
        return False, "Poll not found."

    if len(values) != len(poll["options"]):
        return False, "Invalid number of values provided, expected " + str(
            len(poll["options"])
        )

    if any(v < 0 or v > 5 for v in values):
        return False, "Values must be between 0 and 5."

    poll["rates"][str(user_id)] = values
    save_polls(polls)
    return True, "Rating recorded successfully."


def messagify_poll(poll, author=None):
    question = poll["question"]
    options = poll["options"]
    rates = poll["rates"]

    average_rates = []
    for i in range(len(options)):
        option_rates = [user_rates[i] for user_rates in rates.values()]
        average_rate = sum(option_rates) / len(option_rates) if option_rates else 0
        average_rates.append(average_rate)

    # Determine color based on overall average
    overall_avg = sum(average_rates) / len(average_rates) if average_rates else 0
    if overall_avg >= 4:
        color = 0x4CAF50  # Green
    elif overall_avg >= 3:
        color = 0x2196F3  # Blue
    elif overall_avg >= 2:
        color = 0xFF9800  # Orange
    else:
        color = 0xF44336  # Red

    embed = discord.Embed(title=f"📊 {question}", color=color)

    # Set author if provided
    if author:
        embed.set_author(
            name=author.name, icon_url=author.avatar.url if author.avatar else None
        )

    for i, (option, rate) in enumerate(zip(options, average_rates)):
        # Create a visual bar representation
        bar_length = 20
        filled = int((rate / 5.0) * bar_length)
        bar = "█" * filled + "░" * (bar_length - filled)

        # Star rating
        stars = "⭐" * int(rate) + ("✨" if rate % 1 >= 0.5 else "")

        field_value = f"{bar} {rate:.1f}/5.0\n{stars}"

        embed.add_field(
            name=f"[{i + 1}] {option}",
            value=field_value,
            inline=False,
        )

    # Add footer with number of ratings
    num_votes = len(rates)
    embed.set_footer(text=f"Votes: {num_votes} | Average: {overall_avg:.1f}/5.0")

    return embed

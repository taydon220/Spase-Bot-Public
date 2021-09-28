import datetime
import logging
import os
# noinspection PyUnresolvedReferences
import configloader

from logging.handlers import TimedRotatingFileHandler

import discord
from discord.ext import commands

import db_functions
from message_handler import get_static_response, get_chance_response, get_reaction_response, add_message_to_db, add_chance_to_db


LOGFILE = os.getenv("logfile")
KEY = os.getenv("key")
PREFIX = os.getenv("prefix")
DESCRIPTION = os.getenv("description")
MODE = os.getenv("mode")
ACTIVITY = os.getenv("activity")
DATABASE = os.getenv("database")


rotatingHandler = TimedRotatingFileHandler(LOGFILE, when="d", interval=1, backupCount=14)

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO, handlers=[rotatingHandler])

log = logging.getLogger(__name__)


extensions = ["cogs.media", "cogs.owner", "cogs.fun", "cogs.members", "cogs.amongus"]

bot = commands.Bot(command_prefix=PREFIX, description=DESCRIPTION, case_insensitive=True)


@bot.event
async def on_ready():
    print("   _____                        ____        _   ")
    print("  / ____|                      |  _ \      | |  ")
    print(" | (___  _ __   __ _ ___  ___  | |_) | ___ | |_ ")
    print("  \___ \| '_ \ / _` / __|/ _ \ |  _ < / _ \| __|")
    print("  ____) | |_) | (_| \__ \  __/ | |_) | (_) | |_ ")
    print(" |_____/| .__/ \__,_|___/\___| |____/ \___/ \__|")
    print("        | |                                     ")
    print("        |_|                        By: Taydon220")
    if os.getenv("mode") == "dev":
        print("Developer Mode.")

    table_name = "all_messages"
    activity = discord.Activity(name=os.getenv("activity"), type=discord.ActivityType.watching)
    await bot.change_presence(activity=activity)
    log.info(f'We have logged in as {bot.user}: {datetime.datetime.now()}')
    log.info("___________________________________________________________________\n")
    if not os.path.exists(DATABASE) or not db_functions.table_exists(DATABASE, table_name):
        db_functions.create_table(DATABASE, table_name)
        channel_ids = []
        for channel in bot.get_all_channels():
            if type(channel) == discord.TextChannel or type(channel) == discord.DMChannel:
                channel_ids.append(channel.id)
        log.info(f"{len(channel_ids)} channels found.")

        complete_message_history = []
        for channel_id in channel_ids:
            channel = bot.get_channel(channel_id)
            log.info(f"Collecting history of {channel.name}.")
            history = await channel.history(limit=None).flatten()
            for message in history:
                complete_message_history.append(message)  # List of discord.Message objects
            log.info(f"{channel.name} history loaded.")

        all_messages_sql_values = db_functions.messages_to_sql_values(complete_message_history, table_name)
        # List of tuples (message id, created_at(datetime obj), channel_id, author_id, author_display_name, content)
        db_functions.insert_into_table(DATABASE, table_name, all_messages_sql_values)

    else:  # Compares database most recent date to most recent message date from each channel.
        sql_statement = "SELECT * FROM all_messages ORDER BY created_at DESC LIMIT 1"
        most_recent_message_db = db_functions.select_from_table(DATABASE, sql_statement)
        last_message_date_db = most_recent_message_db[0][0]

        channel_ids = []
        for channel in bot.get_all_channels():
            if type(channel) == discord.TextChannel or type(channel) == discord.DMChannel:
                channel_ids.append(channel.id)

        most_recent_message_all_channels = []
        log.info(f"Fetching most recent messages from {len(channel_ids)} channels!")
        for channel_id in channel_ids:
            channel = bot.get_channel(channel_id)  # Returns discord.Channel object with channel_id.
            log.info(f"{channel.name}: DONE!")
            last = await channel.fetch_message(channel.last_message_id)  # fetch message object.
            most_recent_message_all_channels.append(last)  # List message objects in each channel.

        dates = [message.created_at for message in most_recent_message_all_channels]  # List of datetime objects.
        dates.sort()  # Sorts list in place. Most recent will be in last index.
        most_recent_date_discord = dates[-1]
        log.info("___________________________________________________________________\n")
        log.info(f"Last Database timestamp: {last_message_date_db}")
        log.info(f"Last Discord timestamp: {most_recent_date_discord}")

        if not last_message_date_db == most_recent_date_discord:
            log.info("Timestamps do NOT match! Collecting missed messages.")
            log.info("___________________________________________________________________\n")
            missed_messages = []
            for channel_id in channel_ids:
                channel = bot.get_channel(channel_id)
                history = await channel.history(after=last_message_date_db, limit=None).flatten()
                for message in history:
                    missed_messages.append(message)  # List of discord.Message objects
                log.info(f"{channel.name}: {len(history)} missed messages!")
            log.info("___________________________________________________________________\n")
            missed_messages_sql_values = db_functions.messages_to_sql_values(missed_messages, table_name)
            db_functions.insert_into_table(DATABASE, table_name, missed_messages_sql_values)
            log.info(f"Added {len(missed_messages)} missed message(s) to database.")
        else:
            log.info("Timestamps match! No missed messages.")


@bot.event
async def on_message(message):
    if message.author == bot.user or message.author == bot.get_user(679006394107559947) or message.author == bot.get_user(752222109475799150):
        return
    message_values = (message.created_at, message.id, message.channel.id, message.author.id, message.author.display_name, message.content)

    add_message_to_db(message_values)

    static_response = get_static_response(message.content)
    if static_response is not None:
        await message.channel.send(static_response)
    static_response_sent = True if static_response is not None else False

    reaction_response = get_reaction_response(message.author.id)
    if reaction_response is not None:
        await message.add_reaction(reaction_response)

    if not static_response_sent:
        chance_response = get_chance_response(message.content)
        if chance_response is not None:
            chance_message = await message.channel.send(chance_response)
            chance_message_values = [
                (chance_message.created_at, chance_message.id, chance_message.channel.id, chance_message.content)]
            add_chance_to_db(chance_message_values)

    await bot.process_commands(message)


if __name__ == "__main__":
    for extension in extensions:
        try:
            bot.load_extension(extension)
        except Exception as e:
            log.info(f"Failed to load extension. {e}")


bot.run(KEY, bot=True)

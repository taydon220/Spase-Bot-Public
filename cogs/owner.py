import db_functions
import discord
import os
from discord.ext import commands
from markov import get_past_creations

import logging

log = logging.getLogger(__name__)

DATABASE = os.getenv("database")

class OwnerCog(discord.ext.commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="populate", hidden=True)
    @commands.is_owner()
    async def populate(self, ctx):
        channel_ids = []
        for channel in self.bot.get_all_channels():
            if type(channel) == discord.TextChannel or type(channel) == discord.DMChannel:
                channel_ids.append(channel.id)
        log.info(f"{len(channel_ids)} channels found.")

        complete_message_history = []
        for channel_id in channel_ids:
            channel = self.bot.get_channel(channel_id)
            log.info(f"Collecting history of {channel.name}.")
            history = await channel.history(limit=None).flatten()
            for message in history:
                complete_message_history.append(message)  # List of discord.Message objects
            log.info(f"{channel.name} history loaded.")

        all_messages_sql_values = db_functions.messages_to_sql_values(complete_message_history, "all_messages")  # List of tuples (message id, created_at(datetime obj), channel_id, author_id, author_display_name, content) to add to database.
        db_functions.insert_into_table(DATABASE, "all_messages", all_messages_sql_values)
        await ctx.send("Database populated.")

    @commands.command(name="creations", hidden=True)
    @commands.is_owner()
    async def creations(self, ctx):
        results = get_past_creations(3)
        counter = 1
        await ctx.send("Here are 3 old $random creations.")
        for result in results:
            await ctx.send(f"{counter}) {result[0]}")
            counter += 1

    @commands.command(name="sql", hidden=True, aliases=["overlord", "godking"])
    @commands.is_owner()
    async def sql_selects(self, ctx, query, *argv):
        results = db_functions.select_from_table(DATABASE, query, select_values=str(argv[0])if len(argv)>0 else None)
        if results is None:
            await ctx.send("Nice SQL, you silly head.")
        else:
            await ctx.send(results)


def setup(bot):
    bot.add_cog(OwnerCog(bot))

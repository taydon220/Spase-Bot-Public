import os
import discord
import logging
from discord.ext import commands
from random import randint

log = logging.getLogger(__name__)


class MediaCog(discord.ext.commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(pass_context=True, name="pets", aliases=["layla", "gigi", "rufus", "kiah", "grayson", "luna"])
    async def get_picture(self, ctx):
        pet_name = ctx.message.content.lstrip("$")
        if pet_name == "pets":
            directories = ["layla", "gigi", "rufus", "kiah", "grayson", "luna"]
            pet_name = directories[randint(0, len(directories) - 1)]
        directory = f"./{pet_name.capitalize()}"
        file_names = os.listdir(directory)
        random_file = file_names[randint(0, len(file_names) - 1)]
        await ctx.send(file=discord.File(f"./{directory}/{random_file}"))
        log.info(f"Sent a picture of {pet_name.capitalize()}.")


def setup(bot):
    bot.add_cog(MediaCog(bot))

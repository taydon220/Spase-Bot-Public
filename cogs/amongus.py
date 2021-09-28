import discord
from discord.ext import commands


class AmongUsCog(discord.ext.commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="start", alias=["mute"])
    async def start(self, ctx):
        for member in ctx.guild.get_channel(758515409950474240).members:
            await member.edit(mute=True, deafen=True)

    @commands.command(name="stop", alias=["unmute"])
    async def end(self, ctx):
        for member in ctx.guild.get_channel(758515409950474240).members:
            await member.edit(mute=False, deafen=False)

    @commands.command(name="dead")
    async def dead(self, ctx):
        graveyard = ctx.guild.get_channel(758515488367181865)
        await ctx.author.edit(voice_channel=graveyard)


def setup(bot):
    bot.add_cog(AmongUsCog(bot))

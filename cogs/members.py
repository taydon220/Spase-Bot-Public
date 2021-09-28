import discord
from discord.ext import commands


class MembersCog(discord.ext.commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="request")
    async def request_alert(self, ctx, *, request_data):
        owner = self.bot.get_user(157726512626270208)
        await owner.send(request_data)
        await ctx.send("Your request has been logged.")

def setup(bot):
    bot.add_cog(MembersCog(bot))

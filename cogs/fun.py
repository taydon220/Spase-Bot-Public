import discord
import os
from random import randint
from discord.ext import commands
from spase_stats import message_counter
from markov import respond_db, add_response_to_db, get_past_creations
from spase_quotes import get_quote_and_author_id, get_quote_from_id


import logging

log = logging.getLogger(__name__)

SAE_CHANNEL_ID = 509875543286611968


class FunCog(discord.ext.commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.cooldown(15, 3600, commands.BucketType.user)  # Limited use of 15 times/hour for each user.
    @commands.command(name="quote")
    async def quote(self, ctx, target=None):
        try:
            target_member = await commands.MemberConverter().convert(ctx, target) if target is not None else None
        except commands.BadArgument:
            target_member = None
        if target_member is not None:
            target_id = target_member.id
            quote = get_quote_from_id(target_id)
            await ctx.send(f"It's just like {target_member.mention} always says...")
            await ctx.send(f'"{quote}"')
        else:
            quote, author_id = get_quote_and_author_id()
            author_user = self.bot.get_user(author_id)
            await ctx.send(f"It's just like {author_user.mention} always says...")
            await ctx.send(f'"{quote}"')

    @commands.command(name="whit")
    async def whit(self, ctx):
        await ctx.send(f'{ctx.guild.get_member_named("Spase Queen").mention} is the best wife in the universe!')

    @commands.command(name="log")
    async def for_drew(self, ctx):
        await ctx.send("$log was officially retired on 07/28/2020; Happy now, Drew?")

    @commands.command(name="stats", help="Returns the number of messages sent in current channel and entire server.")
    async def stats(self, ctx, target_member_name=None):
        # transform variables from self,ctx,target to the req'd fields for message_counter()
        caller_author_id = ctx.author.id
        channel_id = ctx.channel.id
        target_author_id = ctx.guild.get_member_named(target_member_name).id if target_member_name is not None else None
        text_channel_ids = []
        for channel in ctx.guild.text_channels:
            text_channel_ids.append(channel.id)

        # invoke business layer
        channel_message_count = message_counter(caller_author_id, channel_id, target_author_id=target_author_id)
        server_message_count = 0
        for id in text_channel_ids:
            server_message_count += message_counter(caller_author_id, id, target_author_id=target_author_id)

        if target_member_name is None:
            await ctx.send(f"You have sent {channel_message_count} messages in this channel and {server_message_count} messages this server.")
        else:
            await ctx.send(f"{target_member_name} has sent {channel_message_count} messages in this channel and {server_message_count} messages this server.")

    @commands.command(name="random")
    async def random(self, ctx, topic=None):
        response = respond_db(topic)
        if response is None:
            await ctx.send("I'm not sure what you mean by that.")
        else:
            while len(response.split(" ")) < 3:
                log.info("Response too short. Adding another chain.")
                response = response.rstrip('.?!') + ', ' + respond_db().lower()
            random_message = await ctx.send(response)
            random_message_values = [(random_message.created_at, random_message.id, random_message.channel.id, random_message.content)]
            add_response_to_db(random_message_values)

    @commands.command(name="roll")
    async def roll_dice(self, ctx, dice="d20"):
        if dice.startswith('d') or dice.startswith('D'):
            sides = int(dice[1:])
            result = randint(1, sides)
            use_an = [8, 11, 18, 80, 81, 82, 83, 84, 85, 86, 87, 88, 89]
            if result in use_an:
                await ctx.send(f"{ctx.author.display_name} rolled a {dice} and got an {result}!")
            else:
                await ctx.send(f"{ctx.author.display_name} rolled a {dice} and got a {result}!")
        else:
            await ctx.sent('Syntax error.')

    @commands.command(name="scream")
    async def scream(self, ctx, *, message='AHHHHHH!!!!!!!!!!!'):
        members = ctx.guild.members
        target = members[randint(0, len(members) - 1)]
        await ctx.send(f'{target.mention} {message}!!!')

    @commands.command(help=' Screams your message at a specific user. (Must put member name in quotations')
    async def scream2(self, ctx, target, *args):
        member = ctx.guild.get_member_named(target)
        message = ' '.join(args)
        await ctx.send(f'{member.mention} {message}!!!')

    @commands.command(name="josh")
    async def josh(self, ctx):
        results = get_past_creations(1)
        random_file = os.listdir("./Josh")[0]
        await ctx.send(file=discord.File(f"./Josh/{random_file}"))
        for result in results:
            await ctx.send(f'"{result[0]}"')

    @commands.command(name="hrimp")
    async def shrimp(self, ctx):
        responses = ["You smell bad.", "Shrimps are dumb.", "Shrimp are bottom feeders and so are you.",
                     "I don't respond to stupid people.", "F shrimp.", "Spase Ninja is cool.", "Not going to happen."]
        await ctx.send(responses[randint(0, len(responses)-1)])


def setup(bot):
    bot.add_cog(FunCog(bot))

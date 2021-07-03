import discord
import emoji
import re
import random
from discord.ext import commands
from datetime import datetime, timedelta
from utils._errors import CannotFindColour, URLNotValid, NoReactionsFound, NoEntryFound, SomethingWentWrong


class DateConverter(commands.Converter):

    async def convert(self, ctx : commands.Context, argument : str) -> datetime:

        try:

            converters = {"s" : 1,
                          "m" : 60,
                          "h" : 3600,
                          "d" : 86400}


            match = re.compile("[^\W\d]").search(argument)
            number, time = [argument[:match.start()], argument[match.start():]]


            if int(number) < 1:
                raise commands.BadArgument


            date = datetime.utcnow()
            date += timedelta(seconds=int(number)*converters[time])

            return date

        except Exception as e:
            print(e)
            raise commands.BadArgument


class Giveaway(commands.Cog):

    def __init__(self, bot):
        self.bot = bot



    async def cog_command_error(self, ctx, error):

        # Gets original attribute of error
        error = getattr(error, "original", error)

        if isinstance(error, CannotFindColour):
            await ctx.send("Cannot find the color you have provided. Please make sure it is a hexadecimal and that the `#` is not included!",delete_after=10)

        elif isinstance(error, URLNotValid):
            await ctx.send("Could not find image. Please make sure that the url ends with a .jpeg/.png or similiar extension.",delete_after=10)


        elif isinstance(error, NoReactionsFound):
            await ctx.send("Something went wrong. Do I have permission to add reactions here?",delete_after=10)

        elif isinstance(error, NoEntryFound):
            await ctx.send("No one entered the giveaway :(", delete_after=10)

        elif isinstance(error, SomethingWentWrong):
            await ctx.send("Something went wrong!", delete_after=10)



    @commands.guild_only()
    @commands.has_permissions(administrator=True)
    @commands.command(name="giveaway", description="Create giveaways")
    async def giveaway(self, ctx, time : DateConverter, colour : str, imageurl : str, *, message : str):

        await ctx.message.delete()


        try:
            hexa = int(colour,16)

        except Exception as e:
            print(e)
            raise CannotFindColour

        embed = discord.Embed(
            title=message,
            description="React to this message to enter the giveaway!",
            color=hexa,
            type="rich",
            timestamp=time
        )

        try:
            embed.set_image(url=imageurl)

        except Exception as e:
            print(e)
            raise URLNotValid


        msg = await ctx.send(embed=embed)
        await msg.add_reaction(emoji.emojize(":fireworks:"))

        await discord.utils.sleep_until(time)

        msg = await ctx.channel.fetch_message(msg.id)

        if len(msg.reactions) == 0:
            raise NoReactionsFound


        reaction = None

        for i in msg.reactions:


            if str(i.emoji) == emoji.emojize(":fireworks:"):

                if i.count <= 1:
                    raise NoEntryFound

                reaction = i



        if not reaction:
            raise SomethingWentWrong

        users = await reaction.users().flatten()

        winner = random.choice([i for i in users if not i.bot])

        embed2 = embed
        embed2.title = "WINNER!!!"
        embed2.description = winner.mention

        await msg.edit(embed=embed2)

        await ctx.send(f"Congratulations {winner.mention}! You have won a giveaway: {msg.jump_url}")






#Setup
def setup(bot):
    bot.add_cog(Giveaway(bot))
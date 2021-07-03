import discord
import re
from discord.ext import commands
from datetime import datetime, timedelta


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




class TempRole(commands.Cog):

    def __init__(self, bot):
        self.bot = bot



    @commands.guild_only()
    @commands.has_permissions(administrator=True)
    @commands.command(name='temprole', description="Command to assign temp role", aliases=['tr'])
    async def temprole(self, ctx, members : commands.Greedy[discord.Member], roles : commands.Greedy[discord.Role], time : DateConverter):


        for member in members:
            await member.add_roles(*roles, reason="Temprole command")


        await ctx.reply("Action In Progress :D")
        await discord.utils.sleep_until(time)

        for member in members:
            await member.remove_roles(*roles)
            removedRoles = '\n - '.join(map(str,roles))

            try:
                await member.send(f"The temporary roles assigned to you in `{ctx.guild.name}` have now been removed!\n``` - {removedRoles}```")

            except Exception as e:
                print(e)
                continue







#Setup
def setup(bot):
    bot.add_cog(TempRole(bot))
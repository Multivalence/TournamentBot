import discord
from discord.ext import commands
import sys
import traceback

class Errors(commands.Cog):

    def __init__(self, bot):
        self.bot = bot


    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):


        # Gets original attribute of error
        error = getattr(error, "original", error)

        if isinstance(error, commands.errors.BadArgument):
            await ctx.send("Bad argument. Please read the help menu for syntax!")
            return

        elif isinstance(error, commands.errors.MissingRequiredArgument):
            await ctx.send("You are missing a required argument")


        elif isinstance(error, discord.Forbidden):

            try:
                await ctx.send("I lack the permissions to do this Action!")

            except discord.Forbidden:
                return


        elif isinstance(error, discord.ext.commands.errors.NoPrivateMessage):
            return


        elif isinstance(error, discord.ext.commands.errors.CheckFailure):
            await ctx.send("This channel does not accept the command you have attempted to invoke!")


        elif isinstance(error, discord.ext.commands.errors.CommandOnCooldown):
            await ctx.send(error)


        elif isinstance(error,discord.ext.commands.errors.ChannelNotFound):
            await ctx.send("Channel not found")

        else:

            # Prints original traceback if it isnt handled
            print('Ignoring exception in command {}:'.format(ctx.command), file=sys.stderr)
            traceback.print_exception(type(error), error, error.__traceback__, file=sys.stderr)



#Setup
def setup(bot):
    bot.add_cog(Errors(bot))
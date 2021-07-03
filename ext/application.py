import discord
import os
import asyncio
from discord.ext import commands
from utils.checks import is_command_channel
from datetime import datetime


class Application(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.appchannel = int(os.environ["APP-CHANNEL"])

        with open('./customize/application_text.txt','r') as textFile:
            self.message = textFile.read()



    @commands.guild_only()
    @commands.check(is_command_channel)
    @commands.cooldown(1,86400, commands.BucketType.user)
    @commands.command(name='apply', description="Command to apply")
    async def apply(self, ctx):

        await ctx.reply("Please check your DM's!")
        await ctx.author.send(self.message)

        def check(m):
            return isinstance(m.channel, discord.DMChannel) and m.author == ctx.author

        try:
            msg = await self.bot.wait_for('message', timeout=7200, check=check)

        except asyncio.TimeoutError:
            await ctx.author.send("Application Timed out! You must wait a day before retrying the application.")


        else:
            await ctx.author.send("Thank you for Applying! An Administrator will get back to you with their decision")

            channel = ctx.guild.get_channel(self.appchannel)

            embed = discord.Embed(
                title="Application",
                description=f"```{msg.content}```",
                color = discord.Colour.default(),
                timestamp=datetime.utcnow()
            )

            embed.set_author(name=f"{ctx.author.name}#{ctx.author.discriminator}", icon_url=ctx.author.avatar_url)


            app = await channel.send(embed=embed)
            await app.add_reaction('👍')
            await app.add_reaction('👎')

            await asyncio.sleep(5)

            def reactioncheck(reaction, user):
                return user.guild_permissions.administrator and str(reaction.emoji) in ('👍','👎')

            try:
                reaction, user = await self.bot.wait_for('reaction_add', timeout=86400.0, check=reactioncheck)

            except asyncio.TimeoutError:
                await channel.send(f"Application by {ctx.author.mention} has expired. Auto Denying!")
                await ctx.author.send("Your Application has been Denied. You may retry after 1 Day. Good Luck!")
                embed.color = discord.Colour.red()
                await app.edit(embed=embed)

            else:
                if str(reaction.emoji) == "👍":
                    embed.color = discord.Colour.green()
                    await app.edit(embed=embed)
                    await ctx.author.send("Your Application has been Accepted! Congratulations. A Staff Member will contact you soon.")
                    await channel.send(f"Accepted {ctx.author.mention}'s Application!",delete_after=10)

                else:
                    embed.color = discord.Colour.red()
                    await app.edit(embed=embed)
                    await ctx.author.send("Your Application has been Denied. You may retry after 1 Day. Good Luck!")
                    await channel.send(f"Denied {ctx.author.mention}'s Application!",delete_after=10)











#Setup
def setup(bot):
    bot.add_cog(Application(bot))
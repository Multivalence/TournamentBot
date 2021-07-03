import discord
import os
import math
from datetime import datetime
import asyncio
from discord.ext import commands
from utils.checks import is_command_channel


class Suggestions(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.suggchannel = int(os.environ["SUGGESTIONS-CHANNEL"])



    async def givexp(self, user : discord.Member, amount : int = 100):

        sql = 'select level, xp from levels where user=?'
        cursor = await self.bot.db.execute(sql, (user.id,))
        result = await cursor.fetchone()



        if not result:

            finalxp = amount

            sql = 'INSERT INTO levels(user) VALUES (?)'
            sql2 = 'UPDATE levels set level = 0 where user = ?'
            sql3 = 'UPDATE levels set xp = ? where user = ?'


            await self.bot.db.execute(sql, (user.id,))
            await self.bot.db.execute(sql2, (user.id,))
            await self.bot.db.execute(sql3, (amount, user.id))
            await self.bot.db.commit()


        else:

            finalxp = result[1] + amount

            sql = 'UPDATE levels set xp = xp + ? where user = ?'
            await self.bot.db.execute(sql, (amount, user.id))
            await self.bot.db.commit()

        try:
            calculated_level = math.floor(math.log(finalxp/100)/math.log(1.5) + 1)

        except ValueError:
            calculated_level = 0


        if calculated_level <= 0:
            sql = 'UPDATE levels set level = 0 where user = ?'
            await self.bot.db.execute(sql, (user.id,))


        else:
            sql = 'UPDATE levels set level = ? where user = ?'
            await self.bot.db.execute(sql, (calculated_level, user.id))

        await self.bot.db.commit()


    @commands.guild_only()
    @commands.check(is_command_channel)
    @commands.cooldown(1,14400, commands.BucketType.user)
    @commands.command(name='suggest', description="Suggest something for the server")
    async def suggest(self, ctx, *, suggestion):

        await ctx.reply("Your suggestion has been sent to the staff team. You will get a response via DM!")

        channel = ctx.guild.get_channel(self.suggchannel)

        embed = discord.Embed(
            title="Suggestion",
            description=f"```{suggestion}```",
            color = discord.Colour.default(),
            timestamp=datetime.utcnow()
        )

        embed.set_author(name=f"{ctx.author.name}#{ctx.author.discriminator}", icon_url=ctx.author.avatar_url)


        sug = await channel.send(embed=embed)
        await sug.add_reaction('👍')
        await sug.add_reaction('👎')

        await asyncio.sleep(5)

        def reactioncheck(reaction, user):
            return user.guild_permissions.administrator and str(reaction.emoji) in ('👍','👎')

        try:
            reaction, user = await self.bot.wait_for('reaction_add', timeout=604800.0, check=reactioncheck)

        except asyncio.TimeoutError:
            await channel.send(f"Suggestion by {ctx.author.mention} has expired. Auto Denying!")
            await ctx.author.send("Your Suggestion has been Denied")
            embed.color = discord.Colour.red()
            await sug.edit(embed=embed)

        else:
            if str(reaction.emoji) == "👍":
                embed.color = discord.Colour.green()
                await sug.edit(embed=embed)
                await ctx.author.send("Your Suggestion has been Accepted! You have been awarded with 100 XP!")
                await self.givexp(ctx.author)
                await channel.send(f"Accepted {ctx.author.mention}'s Suggestion!",delete_after=10)

            else:
                embed.color = discord.Colour.red()
                await sug.edit(embed=embed)
                await ctx.author.send("Your Suggestion has been Denied")
                await channel.send(f"Denied {ctx.author.mention}'s Suggestion!",delete_after=10)







#Setup
def setup(bot):
    bot.add_cog(Suggestions(bot))
import discord
import os
import random
import math
from discord.ext import commands
from utils.checks import is_command_channel


# EQUATIONS
'''
let n = level
xp =  = 100*(1.5**(n-1))

let n = xp
level = [ln(n/100) / ln(1.5)] + 1

'''


class Levels(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

        self.message_cooldown = commands.CooldownMapping.from_cooldown(1.0,60.0, commands.BucketType.user)
        self.bot.loop.create_task(self.getAllLevels())


    async def getAllLevels(self):

        await self.bot.wait_until_ready()

        async with self.bot.db.execute("SELECT * FROM levels") as cursor:
            rows = await cursor.fetchall()

            print("Levels Plugin:",rows)



    @commands.guild_only()
    @commands.has_permissions(administrator=True)
    @commands.command(name='removexp', description= "Command to remove XP", aliases=['rxp'])
    async def removexp(self, ctx, user: discord.Member, amount : int):

        sql = 'select level, xp from levels where user=?'
        cursor = await self.bot.db.execute(sql, (user.id,))
        result = await cursor.fetchone()

        if not result:
            return await ctx.reply("XP from this individual cannot be removed as they don't have any to begin with.")

        _ , xp = result
        finalxp = xp - amount

        if finalxp < 0:
            return await ctx.reply(f"The maximum amount of XP you can take from this individual is: {xp}")

        else:

            sql = 'UPDATE levels set xp = xp - ? where user = ?'
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

            return await ctx.reply(f"Successfully removed {amount} XP from user.")



    @commands.guild_only()
    @commands.has_permissions(administrator=True)
    @commands.command(name='givexp', description= "Command to give XP", aliases=['gxp'])
    async def givexp(self, ctx, user : discord.Member, amount : int):

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


        await ctx.reply(f"Successfully Added {amount} XP to user.")


    @commands.guild_only()
    @commands.check(is_command_channel)
    @commands.command(name='rank',description='Command to check rank')
    async def rank(self, ctx, user : discord.Member = None):

        if not user:
            user = ctx.author

        async with self.bot.db.execute("SELECT level, xp FROM levels WHERE user = ?", (user.id,)) as cursor:
            rows = await cursor.fetchone()

            if rows:
                level, xp = rows

            else:
                level, xp = (0,0)


            embed = discord.Embed(
                title="Rank",
                description=user.mention,
                color=discord.Colour.gold()
            )

            embed.add_field(name="Level", value=level)
            embed.add_field(name="XP", value=xp)
            embed.set_thumbnail(url=user.avatar_url)


            await ctx.send(embed=embed)



    @commands.Cog.listener('on_message')
    async def on_message_sent(self, message):

        x = await self.bot.get_context(message)

        if x.valid:
            return

        if message.author.bot:
            return

        bucket = self.message_cooldown.get_bucket(message)
        retry_after = bucket.update_rate_limit()

        if retry_after:
            return

        addedxp = random.randint(10,15)

        sql = 'select level, xp from levels where user=?'
        cursor = await self.bot.db.execute(sql, (message.author.id,))
        result = await cursor.fetchone()

        if not result:

            sql = 'INSERT INTO levels(user) VALUES (?)'
            sql2 = 'UPDATE levels set level = 0 where user = ?'
            sql3 = 'UPDATE levels set xp = ? where user = ?'


            await self.bot.db.execute(sql, (message.author.id,))
            await self.bot.db.execute(sql2, (message.author.id,))
            await self.bot.db.execute(sql3, (addedxp, message.author.id))
            await self.bot.db.commit()


        else:

            sql = 'UPDATE levels set xp = xp + ? where user = ?'
            await self.bot.db.execute(sql, (addedxp, message.author.id))
            await self.bot.db.commit()

            sql2 = 'SELECT xp, level from levels WHERE user = ?'
            cursor = await self.bot.db.execute(sql2, (message.author.id,))
            result = await cursor.fetchone()


            calculated_level = math.floor(math.log(result[0]/100)/math.log(1.5) + 1)


            if calculated_level <= 0:
                return

            else:
                sql = 'UPDATE levels set level = ? where user = ?'

                await self.bot.db.execute(sql, (calculated_level, message.author.id))
                await self.bot.db.commit()

                if result[1] != calculated_level:
                    await message.author.send(f"Congratulations. You have reached level {calculated_level}")














#Setup
def setup(bot):
    bot.add_cog(Levels(bot))
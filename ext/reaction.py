import discord
import os
from discord.ext import commands
import emoji
from sqlite3 import IntegrityError


class ReactionRole(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.bot.loop.create_task(self.updateReactions())



    async def updateReactions(self):

        await self.bot.wait_until_ready()

        async with self.bot.db.execute("SELECT msgid FROM reactionrole") as cursor:
            rows = await cursor.fetchall()

            try:
                self.rr = [i[0] for i in rows]

            except IndexError:
                self.rr = list()

            print("Reaction Roles Plugin:",self.rr)



    @commands.Cog.listener()
    async def on_raw_message_delete(self, payload):

        if not payload.message_id in self.rr:
            return


        sql = 'DELETE FROM reactionrole WHERE msgid=?'

        async with self.bot.db.execute(sql, (payload.message_id,)) as cursor:
            await self.bot.db.commit()


        self.rr.remove(payload.message_id)





    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):

        if payload.member.bot:
            return

        if not payload.message_id in self.rr:
            return


        guild = self.bot.get_guild(payload.guild_id)
        channel = guild.get_channel(payload.channel_id)
        message = await channel.fetch_message(payload.message_id)

        embed = message.embeds[0]

        for field in embed.fields:
            if field.name == str(payload.emoji):
                role = guild.get_role(int("".join(map(str,[i for i in field.value if i.isdigit()]))))
                await payload.member.add_roles(role)



    @commands.Cog.listener()
    async def on_raw_reaction_remove(self, payload):

        guild = self.bot.get_guild(payload.guild_id)

        member = guild.get_member(payload.user_id)

        if member.bot:
            return

        if not payload.message_id in self.rr:
            return



        channel = guild.get_channel(payload.channel_id)
        message = await channel.fetch_message(payload.message_id)

        embed = message.embeds[0]

        for field in embed.fields:
            if field.name == str(payload.emoji):
                role = guild.get_role(int("".join(map(str,[i for i in field.value if i.isdigit()]))))
                await member.remove_roles(role)







    @commands.guild_only()
    @commands.has_permissions(administrator=True)
    @commands.command(name='reaction',description='Command to add reaction',aliases=['rr'])
    async def reaction(self, ctx, title : str, hexa : str,  roles : commands.Greedy[discord.Role], *reactions):

        reactions = [emoji.emojize(":" + i +  ":") for i in reactions]

        if len(roles) != len(reactions):
            return await ctx.send("You didn't provide enough and/or provided too many roles or reactions!")


        embed = discord.Embed(
            title=title,
            description="React with the emoji associated with a role you want",
            colour=int(hexa,16)
        )

        for i in zip(roles,reactions):
            embed.add_field(value=i[0].mention, name=i[1], inline=False)



        msg = await ctx.send(embed=embed)


        try:
            for reaction in reactions:
                await msg.add_reaction(reaction)

        except discord.errors.HTTPException:
            await msg.delete()
            return await ctx.send("Something went wrong. Please make sure you only use default emojis as custom ones aren't supported!")

        else:


            sql = 'INSERT INTO reactionrole(msgid) VALUES (?)'

            try:
                async with self.bot.db.execute(sql, (msg.id,)) as cursor:
                    await self.bot.db.commit()

            except IntegrityError:
                return await ctx.send("Database mismatch. Please restart bot!")

            self.rr.append(msg.id)






#Setup
def setup(bot):
    bot.add_cog(ReactionRole(bot))
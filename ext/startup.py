import discord
import os
from discord.ext import commands
import aiosqlite


class Startup(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.bot.loop.create_task(self.initializeDB())



    async def initializeDB(self):

        self.bot.db = await aiosqlite.connect('bot.db')

        socialtable = '''CREATE TABLE IF NOT EXISTS social (
            
            twitch TEXT UNIQUE,
            youtube TEXT UNIQUE
            
        )
        
        '''


        rr = '''CREATE TABLE IF NOT EXISTS reactionrole (
            
            msgid INTEGER UNIQUE
            
        )
        
        '''


        levels = '''CREATE TABLE IF NOT EXISTS levels (
            
            user INTEGER UNIQUE PRIMARY KEY,
            xp BIGINT,
            level BIGINT
            
            
        )
        
        '''

        await self.bot.db.execute(socialtable)
        await self.bot.db.execute(rr)
        await self.bot.db.execute(levels)
        await self.bot.db.commit()



    @commands.Cog.listener()
    async def on_ready(self):
        print(f'Logged in as {self.bot.user.name} | {self.bot.user.id}')









#Setup
def setup(bot):
    bot.add_cog(Startup(bot))
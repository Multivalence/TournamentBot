import discord
import twitch
import os
import concurrent.futures
from discord.ext import commands, tasks
from utils._errors import SocialAlreadyImplemented, SocialNotFound, SocialDoesNotExist
from sqlite3 import IntegrityError
from datetime import datetime


class Twitch(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.clientID = os.environ["TWITCH_ID"]
        self.clientSecret = os.environ["TWITCH_SECRET"]
        self.announced = []
        self.bot.loop.create_task(self.updateStreamers())



    async def updateStreamers(self):

        await self.bot.wait_until_ready()

        async with self.bot.db.execute("SELECT twitch FROM social") as cursor:
            rows = await cursor.fetchall()

            try:
                self.streamers = [i[0] for i in rows if i[0] != None]

            except IndexError:
                self.streamers = list()

            print("Twitch Plugin:",self.streamers)
            self.check_if_live.start()


    async def cog_command_error(self, ctx, error):

        # Gets original attribute of error
        error = getattr(error, "original", error)

        if isinstance(error, SocialDoesNotExist):
            await ctx.send("That Streamer is not in the database!")

        elif isinstance(error, SocialNotFound):
            await ctx.send("Could not find streamer. Are you sure you typed the username correctly?")

        elif isinstance(error, SocialAlreadyImplemented):
            await ctx.send("That Streamer is already in the database!")



    @tasks.loop(seconds=600)
    async def check_if_live(self):

        streamers = self.streamers

        if len(streamers) == 0:
            return


        for username in streamers:
            with concurrent.futures.ThreadPoolExecutor() as pool:
                result = await self.bot.loop.run_in_executor(pool, self.isLive, username)


            # If Live Stream is finished for particular user
            if not result and username in self.announced:
                self.announced.remove(username)

            #If Live Stream is still going for particular user but has already been announced
            elif result and username in self.announced:
                continue

            #If Live Stream is going for particular user and has not been announced
            elif result and username not in self.announced:

                link = f"https://www.twitch.tv/{username}"

                channel = self.bot.get_channel(int(os.environ["ANNOUNCEMENT-CHANNEL-TWITCH"]))

                with open('./customize/announce_twitch.txt','r') as textFile:
                    text = textFile.read().format(user=result,url=link)

                await channel.send(text)
                self.announced.append(username)

            else:
                continue



    @check_if_live.before_loop
    async def before_live_check(self):
        await self.bot.wait_until_ready()



    def isLive(self, username : str):

        streamer = twitch.Helix(self.clientID, self.clientSecret).user(username)

        if streamer.is_live:
            return streamer.display_name

        else:
            return False


    def validate(self, username : str) -> bool:
        return twitch.Helix(self.clientID, self.clientSecret).user(username)


    @commands.guild_only()
    @commands.has_permissions(administrator=True)
    @commands.command(name="addtwitch", description="Command to add Streamer", aliases=['at'])
    async def addtwitch(self, ctx, user : str):

        await ctx.trigger_typing()

        username = user.lower()

        with concurrent.futures.ThreadPoolExecutor() as pool:
            result = await self.bot.loop.run_in_executor(pool, self.validate, username)

        if not result:
            raise SocialNotFound

        sql = 'INSERT INTO social(twitch) VALUES (?)'

        try:
            async with self.bot.db.execute(sql, (username,)) as cursor:
                await self.bot.db.commit()

        except IntegrityError:
            raise SocialAlreadyImplemented

        else:
            self.streamers.append(username)

            embed = discord.Embed(
                title="Action Successful",
                description=f"Streamer Added: **{user}**",
                colour=discord.Colour.dark_purple()
            )

            return await ctx.send(embed=embed)



    @commands.guild_only()
    @commands.has_permissions(administrator=True)
    @commands.command(name='removetwitch',description='Command to remove streamer',aliases=['rt'])
    async def removetwitch(self, ctx, user : str):


        username = user.lower()

        if username not in self.streamers:
            raise SocialDoesNotExist


        sql = 'DELETE FROM social WHERE twitch=?'

        async with self.bot.db.execute(sql, (username,)) as cursor:
            await self.bot.db.commit()

        self.streamers.remove(username)

        embed = discord.Embed(
            title="Action Successful",
            description=f"Streamer Removed: **{user}**",
            colour=discord.Colour.dark_purple()
        )

        await ctx.send(embed=embed)


    @commands.guild_only()
    @commands.has_permissions(administrator=True)
    @commands.command(name='listtwitch', description='Command that lists all Streamers being Monitored', aliases=['lt'])
    async def listtwitch(self, ctx):

        if len(self.streamers) == 0:
            return await ctx.send("There are currently no Streamers being monitored. Add them via the `addtwitch` command")

        mapped = '\n'.join(map(str,self.streamers))

        embed = discord.Embed(
            title="List of Streamers currently being Monitored",
            description=f"`{mapped}`",
            colour=discord.Colour.purple(),
            timestamp=datetime.utcnow()
        )

        embed.set_footer(text=f"{ctx.author.name}#{ctx.author.discriminator}", icon_url=ctx.author.avatar_url)

        return await ctx.send(embed=embed)





#Setup
def setup(bot):
    bot.add_cog(Twitch(bot))
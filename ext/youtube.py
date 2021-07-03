import discord
import os
import concurrent.futures
import urllib.request
import json
from discord.ext import commands, tasks
from utils._errors import SocialAlreadyImplemented, SocialNotFound, SocialDoesNotExist
from sqlite3 import IntegrityError
from datetime import datetime


class YouTube(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

        self.api_key = os.environ['YOUTUBE_API_KEY']
        self.base_video_url = 'https://www.youtube.com/watch?v='
        self.base_search_url = 'https://www.googleapis.com/youtube/v3/search?'

        self.announced = dict()

        self.bot.loop.create_task(self.updateChannels())



    async def updateChannels(self):

        await self.bot.wait_until_ready()

        async with self.bot.db.execute("SELECT youtube FROM social") as cursor:
            rows = await cursor.fetchall()

            try:
                self.channels = [i[0] for i in rows if i[0] != None]

            except IndexError:
                self.channels = list()

            print("YouTube Plugin:",self.channels)
            self.check_for_new_video.start()


    async def cog_command_error(self, ctx, error):

        # Gets original attribute of error
        error = getattr(error, "original", error)

        if isinstance(error, SocialDoesNotExist):
            await ctx.send("That Channel is not in the database!")

        elif isinstance(error, SocialNotFound):
            await ctx.send("Could not find Channel or Data API Rate Limit Reached. To convert username -> channel ID use this converter: https://socialnewsify.com/get-channel-id-by-username-youtube/")

        elif isinstance(error, SocialAlreadyImplemented):
            await ctx.send("That Channel is already in the database!")



    @tasks.loop(seconds=600)
    async def check_for_new_video(self):

        channels = self.channels

        if len(channels) == 0:
            return


        for channelID in channels:
            with concurrent.futures.ThreadPoolExecutor() as pool:
                result = await self.bot.loop.run_in_executor(pool, self.get_latest_video, channelID)

            #Youtube Data API rate limit reached
            if not result:
                return

            video_link, channel_title = result


            try:

                if video_link == self.announced[channel_title]:
                    print("Already Announced")
                    continue

            except KeyError:
                pass





            channel = self.bot.get_channel(int(os.environ["ANNOUNCEMENT-CHANNEL-YOUTUBE"]))

            with open('./customize/announce_youtube.txt','r') as textFile:
                text = textFile.read().format(user=channel_title,url=video_link)

            await channel.send(text)
            self.announced[channel_title] = video_link




    @check_for_new_video.before_loop
    async def before_check(self):
        await self.bot.wait_until_ready()



    def get_latest_video(self,channel_id):

        try:

            first_url = self.base_search_url+'key={}&channelId={}&part=snippet,id&order=date&maxResults=1'.format(self.api_key, channel_id)

            video_links = []
            url = first_url


            inp = urllib.request.urlopen(url)
            resp = json.load(inp)

            channelTitle = resp['items'][0]['snippet']['channelTitle']

            for i in resp['items']:
                if i['id']['kind'] == "youtube#video":
                    video_links.append(self.base_video_url + i['id']['videoId'])

            try:
                next_page_token = resp['nextPageToken']
                url = first_url + '&pageToken={}'.format(next_page_token)
            except:
                return (video_links[0], channelTitle)

            return (video_links[0], channelTitle)

        except Exception as e:
            return False


    def validate(self, channel_id : str) -> bool:

        try:

            first_url = self.base_search_url+'key={}&channelId={}&part=snippet,id&order=date&maxResults=1'.format(self.api_key, channel_id)
            url = first_url


            inp = urllib.request.urlopen(url)
            resp = json.load(inp)

            channelTitle = resp['items'][0]['snippet']['channelTitle']


        except Exception as e:
            print(e)
            return False


        else:
            return channelTitle if channelTitle else False


    @commands.guild_only()
    @commands.has_permissions(administrator=True)
    @commands.command(name="addyt", description="Command to add Channel", aliases=['addyoutube','ay'])
    async def addyt(self, ctx, channel_id : str):

        await ctx.trigger_typing()


        with concurrent.futures.ThreadPoolExecutor() as pool:
            result = await self.bot.loop.run_in_executor(pool, self.validate, channel_id)

        if not result:
            raise SocialNotFound

        sql = 'INSERT INTO social(youtube) VALUES (?)'

        try:
            async with self.bot.db.execute(sql, (channel_id,)) as cursor:
                await self.bot.db.commit()

        except IntegrityError:
            raise SocialAlreadyImplemented

        else:
            self.channels.append(channel_id)

            embed = discord.Embed(
                title="Action Successful",
                description=f"Channel Added: **{result}**",
                colour=discord.Colour.red()
            )

            return await ctx.send(embed=embed)



    @commands.guild_only()
    @commands.has_permissions(administrator=True)
    @commands.command(name='removeyt',description='Command to remove channel',aliases=['ry','removeyoutube'])
    async def removeyt(self, ctx, channel_id : str):


        if channel_id not in self.channels:
            raise SocialDoesNotExist


        sql = 'DELETE FROM social WHERE youtube=?'

        async with self.bot.db.execute(sql, (channel_id,)) as cursor:
            await self.bot.db.commit()

        self.channels.remove(channel_id)

        embed = discord.Embed(
            title="Action Successful",
            description=f"Channel Removed: **{channel_id}**",
            colour=discord.Colour.from_rgb(255,255,255)
        )

        await ctx.send(embed=embed)


    @commands.guild_only()
    @commands.has_permissions(administrator=True)
    @commands.command(name='listyt', description='Command that lists all channels being Monitored', aliases=['ly','listyoutube'])
    async def listyt(self, ctx):

        if len(self.channels) == 0:
            return await ctx.send("There are currently no Channels being monitored. Add them via the `addyt` command")

        mapped = '\n'.join(map(str,self.channels))

        embed = discord.Embed(
            title="List of Channels currently being Monitored",
            description=f"`{mapped}`",
            colour=discord.Colour.dark_red(),
            timestamp=datetime.utcnow()
        )

        embed.set_footer(text=f"{ctx.author.name}#{ctx.author.discriminator}", icon_url=ctx.author.avatar_url)

        return await ctx.send(embed=embed)





#Setup
def setup(bot):
    bot.add_cog(YouTube(bot))
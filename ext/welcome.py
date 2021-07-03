import discord
import os
from discord import Webhook, AsyncWebhookAdapter
from discord.ext import commands
import aiohttp


class Welcome(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.bot.loop.create_task(self.identifyWebhook())


    async def identifyWebhook(self):

        await self.bot.wait_until_ready()

        guild = self.bot.get_guild(int(os.environ["GUILD_ID"]))
        channel = guild.get_channel(int(os.environ["ANNOUNCEMENT-CHANNEL-WELCOME"]))
        whooks = await guild.webhooks()

        for i in whooks:
            if i.name == "Bad Omens":
                self.url = i.url
                return


        async with aiohttp.ClientSession() as cs:

            async with cs.get(str(self.bot.user.avatar_url)) as r:
                image_bytes = await r.read()


            web = await channel.create_webhook(name="Bad Omens", avatar=image_bytes, reason="Welcome Messages")

            self.url = web.url
            print(self.url)
            return



    @commands.Cog.listener()
    async def on_member_join(self,member):

        if not self.url:
            return

        embed = discord.Embed(
            title="",
            description="**WELCOME!**",
            color=discord.Color.green(),
            type="rich"
        )

        embed.add_field(name="User", value=member.mention, inline=True)
        embed.set_thumbnail(url=member.avatar_url)

        async with aiohttp.ClientSession() as session:
            webhook = Webhook.from_url(self.url, adapter=AsyncWebhookAdapter(session))
            await webhook.send(embed=embed)









#Setup
def setup(bot):
    bot.add_cog(Welcome(bot))
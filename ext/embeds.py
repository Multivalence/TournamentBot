import discord
from discord.ext import commands
import aiohttp
import json

class Embed(commands.Cog):

    def __init__(self,bot):
        self.bot = bot

    @commands.guild_only()
    @commands.has_permissions(administrator=True)
    @commands.command(name="embed", description="Create custom embeds")
    async def embed(self,ctx):

        await ctx.message.delete()

        if len(ctx.message.attachments) == 0:
            return await ctx.send("You haven't sent any JSON file to me. Here is the format you must follow: https://discord.com/developers/docs/resources/channel#embed-object")


        else:
            url = ctx.message.attachments[0].url

            async with aiohttp.ClientSession() as session:
                async with session.get(url) as resp:
                    x = await resp.read()


                    try:
                        data = json.loads(x)
                        embed = discord.Embed.from_dict(data)

                    except Exception as e:
                        print(e)
                        return await ctx.send("Something went wrong. Please make sure the file type is json and that the data inside the file is correct!")

                    await ctx.send(embed=embed)




#Setup
def setup(bot):
    bot.add_cog(Embed(bot))
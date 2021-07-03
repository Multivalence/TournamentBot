import discord
import os
from discord.ext import commands
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())


class MyHelp(commands.HelpCommand):
    def get_command_signature(self, command):
        return '%s%s %s' % (self.clean_prefix, command.qualified_name, command.signature)

    async def send_bot_help(self, mapping):
        embed = discord.Embed(title="Help")
        for cog, commands in mapping.items():
            filtered = await self.filter_commands(commands, sort=True)
            command_signatures = [self.get_command_signature(c) for c in filtered]
            if command_signatures:
                cog_name = getattr(cog, "qualified_name", "No Category")
                embed.add_field(name=cog_name, value="\n".join(command_signatures), inline=False)

        channel = self.get_destination()
        await channel.send(embed=embed)



bot = commands.Bot(command_prefix=os.environ["PREFIX"],
                   status=discord.Status.online,
                   activity=discord.Game(name="with my homies"),
                   intents=discord.Intents.all(),
                   help_command=MyHelp(),
                   case_insensitive=True)


extensions = [
    'ext.startup',
    'ext.music',
    'ext.errors',
    'ext._twitch',
    'ext.temprole',
    'ext.application',
    'ext.welcome',
    'ext.reaction',
    'ext.embeds',
    'ext.giveaway',
    'ext.youtube',
    'ext.levels',
    'ext.suggestions',
    'ext.tournament.tournament'
]

for ext in extensions:
    bot.load_extension(ext)


bot.run(os.environ["TOKEN"])








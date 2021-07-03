import discord
import os
from datetime import datetime
from discord.ext import commands, tasks
from utils.checks import is_register_channel, is_command_channel
from ext.tournament.tourn import Tourney
from ext.tournament.tourn import SizeError, MaxSizeReached, MaxTeamSizeReached, NoParticipants, NotInBracket
from ext.tournament.tourn import ParticipantNotFound, ParticipantAlreadyExists, BracketAlreadyGenerated





class Tournament(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.brackets_channel = int(os.environ["BRACKETS-CHANNEL"])
        self.results_channel = int(os.environ["RESULTS-CHANNEL"])
        self.score_channel = int(os.environ["SCORE-CHANNEL"])
        self.tournament = None
        self.started = False
        self.winner = None
        self.loser = None
        self.check_if_tournament_over.start()


    @tasks.loop(seconds=5)
    async def check_if_tournament_over(self):

        if self.winner and self.loser:

            channel = self.bot.get_channel(self.results_channel)

            winners = (self.winner, self.loser)
            p = 0
            third_team = None

            for team in self.tournament.team_data:
                wins = self.tournament.team_data[team]["wins"]
                loses = self.tournament.team_data[team]["loses"]

                if team not in winners:

                    print(team, f"{wins}/{loses}")

                    if wins / loses > p:
                        p = wins / loses
                        third_team = team




            embed = discord.Embed(
                title="Tournament Finished",
                colour=discord.Colour.gold(),
                timestamp=datetime.utcnow()
            )

            embed.add_field(name="Winner of Main Bracket",value=f"```{self.winner}```", inline=False)
            embed.add_field(name="Winner of Loser Bracket", value=f"```{self.loser}```",inline=False)
            embed.add_field(name="3rd Place Winner", value=f"```{third_team}```", inline=False)

            msg = await channel.send(embed=embed)
            ctx = await self.bot.get_context(msg)

            await ctx.invoke(self.info, team_name=self.winner)
            await ctx.invoke(self.info, team_name=self.loser)

            if third_team:
                await ctx.invoke(self.info, team_name=third_team)


            self.winner = None
            self.loser = None
            self.tournament = None
            self.started = False



    @check_if_tournament_over.before_loop
    async def before_check(self):
        await self.bot.wait_until_ready()




    @commands.guild_only()
    @commands.has_permissions(administrator=True)
    @commands.command(name='create', description="Create a tournament")
    async def create(self, ctx, size : int, team_size : int, prize1 : str, prize2 : str, prize3 : str, hosts : commands.Greedy[discord.Member]):

        if isinstance(self.tournament, Tourney):
            return await ctx.send("There is already an active Tournament. Please delete it before creating an new one!")

        try:
            self.tournament = Tourney(size, team_size, hosts)

        except SizeError:
            return await ctx.send("The size is required to be an even number!")

        else:

            await ctx.message.delete()

            embed = discord.Embed(
                title="Tournament",
                description="Register in the Registry channel!",
                colour=discord.Colour.dark_green(),
                timestamp=datetime.utcnow()
            )

            embed.add_field(name="Participant Size",value=str(size))
            embed.add_field(name="Team Size", value=str(team_size))
            embed.add_field(name="1st Place Prize", value="\u200b",inline=False)
            embed.set_image(url=prize1)




            secondplace = discord.Embed(title="2nd Place Prize", colour=discord.Colour.blue())
            secondplace.set_image(url=prize2)

            thirdplace = discord.Embed(title="3rd Place Prize",colour=discord.Colour.gold())
            thirdplace.set_image(url=prize3)

            await ctx.send(embed=embed)
            await ctx.send(embed=secondplace)
            await ctx.send(embed=thirdplace)



    @commands.guild_only()
    @commands.has_permissions(administrator=True)
    @commands.command(name='cancel', description="stop the tournament")
    async def cancel(self, ctx):

        channel = ctx.guild.get_channel(self.results_channel)

        if isinstance(self.tournament, Tourney):

            self.winner = None
            self.loser = None
            self.tournament = None
            self.started = False

            await ctx.send("Tournament Stopped", delete_after=10)


            embed = discord.Embed(
                title="Tournament Stopped by Administrator",
                colour=discord.Colour.dark_red(),
                timestamp=datetime.utcnow()
            )

            await channel.send(embed=embed)


        else:
            await ctx.send("There is no Tournament to stop!")


    @commands.guild_only()
    @commands.command(name='forcedisband', description="Forcefully disband a team")
    async def forcedisband(self, ctx, *, team_name : str):


        if not self.tournament:
            return await ctx.send("There is no active tournament at the moment")

        if not ctx.author in self.tournament.HOSTS:
            return await ctx.send("You do not have permission to do this command!")

        if self.started:
            return await ctx.send("You cannot disband a team after the tournament has started as brackets have already been generated!")

        try:
            self.tournament.remove_participant(team_name)

        except NoParticipants:
            return await ctx.send("There are no participants in the tournament")

        except ParticipantNotFound:
            return await ctx.send("Participant not found")

        else:
            return await ctx.send(f"Team {team_name} was disbanded")


    @commands.guild_only()
    @commands.command(name='start', description="start the tournament")
    async def start(self, ctx):

        if not self.tournament:
            return await ctx.send("No Tournament to start")

        if ctx.author not in self.tournament.HOSTS:
            return await ctx.send("You do not have permission to do this command!")

        if self.started:
            return await ctx.send("Tournament has already been started!")


        try:

            self.tournament.generate_bracket()

        except SizeError:
            return await ctx.send("Not enough participants to start")

        channel = ctx.guild.get_channel(self.brackets_channel)

        self.started = True


        return await self.brackets_embed(channel)




    async def brackets_embed(self, channel):

        embed = discord.Embed(
            title="Brackets"
        )

        if len(self.tournament.brackets) >= 1:

            x = "\n".join(map(str,[f"```{t1} vs {t2}```" for t1, t2 in self.tournament.brackets]))

            embed.add_field(name="Winners Bracket", value=x, inline=False)

        if len(self.tournament.loser_brackets) >= 1:
            y = "\n".join(map(str,[f"```{t1} vs {t2}```" for t1, t2 in self.tournament.loser_brackets]))
            embed.add_field(name="Losers Bracket", value=y, inline=False)

        if len(self.tournament.winners) >= 1:

            if self.winner:
                embed.add_field(name="Winner (Winners Bracket)", value=self.tournament.winners[0], inline=False)

            else:
                embed.add_field(name="Waiting for Opponent (Winners Bracket)", value=self.tournament.winners[0], inline=False)


        if len(self.tournament.losers) >= 1:

            if self.loser:
                embed.add_field(name="Winner (Losers Bracket)", value=self.tournament.losers[0], inline=False)

            else:
                embed.add_field(name="Waiting for Opponent (Losers Bracket)", value=self.tournament.losers[0], inline=False)


        return await channel.send(embed=embed)




    @commands.guild_only()
    @commands.command(name='winner', description="add a winner for the tournament")
    async def winner(self, ctx, *, team_name : str):

        if not self.tournament:
            return await ctx.send("There is currently no Tournament Active")

        if ctx.author not in self.tournament.HOSTS:
            return await ctx.send("You do not have permission to do this command!")

        if not self.started:
            return await ctx.send("Bracket must be generated before adding winners. Use the start command to do so!")

        if team_name not in self.tournament.participants:
            return await ctx.send("Could not find team with that name!")


        score_channel = self.bot.get_channel(self.score_channel)

        if len(self.tournament.participants) == 2:


            loser_brackets_winner = "".join(map(str,[i for i in self.tournament.participants if i != team_name]))

            self.winner = team_name
            self.loser = loser_brackets_winner

            await self.brackets_embed(ctx.guild.get_channel(self.brackets_channel))
            await score_channel.send(f"```[+ 1 win (Winners Bracket)] {self.winner}```")
            await score_channel.send(f"```[+ 1 win (Losers Bracket)] {self.loser}```")




        else:

            for i in self.tournament.brackets:
                if team_name in i:
                    x = self.tournament.winner(team_name)
                    await score_channel.send(f"```[+ 1 win (Winners Bracket)] {team_name}```")

                    if x:
                        print(f"Winners Bracket Won by {team_name}")
                        self.winner = team_name
                        return await self.brackets_embed(ctx.guild.get_channel(self.brackets_channel))



                    return await self.brackets_embed(ctx.guild.get_channel(self.brackets_channel))



            for i in self.tournament.loser_brackets:
                if team_name in i:
                    x = self.tournament.loser_bracket_winner(team_name)
                    await score_channel.send(f"```[+ 1 win (Losers Bracket)] {team_name}```")

                    if x:

                        print(f"Losers Bracket Won by {team_name}")
                        self.loser = team_name
                        return await self.brackets_embed(ctx.guild.get_channel(self.brackets_channel))



                    return await self.brackets_embed(ctx.guild.get_channel(self.brackets_channel))








    @commands.guild_only()
    @commands.check(is_register_channel)
    @commands.command(name='disband', description="Disband your team")
    async def disband(self, ctx):

        if not self.tournament:
            return await ctx.send("There is no active tournament at the moment")

        if self.started:
            return await ctx.send("Team cannot be disbanded after tournament has started!")

        for team in self.tournament.team_data:
            if ctx.author in self.tournament.team_data[team]['members']:

                try:
                    self.tournament.remove_participant(team)

                except NoParticipants:
                    return await ctx.send("There are no participants in the tournament")

                except ParticipantNotFound:
                    return await ctx.send("Participant not found")

                else:
                    return await ctx.send("Your team was disbanded!")


        return await ctx.send("Could not find your team!")



    #For Testing purposes only.

    # @commands.guild_only()
    # @commands.command()
    # async def test(self, ctx, *, team_name : str):
    #
    #     self.tournament.add_participant(team_name, (ctx.author,))



    @commands.guild_only()
    @commands.check(is_register_channel)
    @commands.command(name='register', description="Register your team for the tournament")
    async def register(self, ctx, team_members : commands.Greedy[discord.Member], *, team_name : str):

        if self.started:
            return await ctx.send("You may not register as the tournament has already started")

        if not self.tournament:
            return await ctx.send("There is no tournament to register for!")

        if len(team_members) > self.tournament.team_size - 1:
            return await ctx.send(f"You may only have a maximum of {self.tournament.team_size} members in your team! Please do not add yourself as a team member as you will automatically be included!")

        if team_name.lower() in [i.lower() for i in self.tournament.participants]:
            return await ctx.send(f"The team name: `{team_name}` is already taken!")

        if ctx.author in team_members:
            return await ctx.send("Please do not add yourself as a team member as you will automatically be included!")

        for team in self.tournament.team_data:
            if ctx.author in self.tournament.team_data[team]['members']:
                return await ctx.send(f"You are already part of a team: `{team}`. If you believe this is a mistake, please contact an administrator!")

            for i in team_members:
                if i in self.tournament.team_data[team]['members']:
                    return await ctx.send("The team member(s) you have provided are already in a team! If you believe this is a mistake, please contact an administrator!")

        team_members.append(ctx.author)

        try:

            self.tournament.add_participant(team_name, team_members)


        except MaxSizeReached:
            return await ctx.send("Tournament has reached maximum size capacity. No more teams are permitted to register!")

        except MaxTeamSizeReached:
            return await ctx.send("You may not have that many people in your team!")

        except ParticipantAlreadyExists:
            return await ctx.send("Team already exists. If you believe this is an error please contact an administrator!")

        else:

            return await ctx.send(embed=discord.Embed(title="Team Registered", description=team_name))



    @commands.guild_only()
    @commands.check(is_command_channel)
    @commands.command(name="info", description="get info about teams")
    async def info(self, ctx, *, team_name : str):

        if not self.tournament:
            return await ctx.send("There is no active tournament at the moment")

        if team_name in self.tournament.participants:

            embed = discord.Embed(
                title=team_name,
                color=discord.Colour.random()
            )

            data = self.tournament.team_data[team_name]


            embed.add_field(name="Team Members", value="\n".join(map(str,[i.mention for i in data["members"]])))
            embed.add_field(name="Wins", value=data["wins"])
            embed.add_field(name="Loses", value=data["loses"])

            return await ctx.send(embed=embed)


        else:
            return await ctx.send("Could not find team with that name! **Note:** Team names are case sensitive.")









#Setup
def setup(bot):
    bot.add_cog(Tournament(bot))
import random
from discord.ext.commands import CommandError

class SizeError(CommandError):
    pass


class MaxSizeReached(CommandError):
    pass


class NoParticipants(CommandError):
    pass


class ParticipantNotFound(CommandError):
    pass


class ParticipantAlreadyExists(CommandError):
    pass


class BracketAlreadyGenerated(CommandError):
    pass


class MaxTeamSizeReached(CommandError):
    pass


class StrictError(CommandError):
    pass


class NotInBracket(CommandError):
    pass


class Tourney:

    def __init__(self, size : int, team_size : int, hosts : tuple, strict : bool = False):


        self._checkSize(size)

        self.size = size
        self.HOSTS = hosts
        self.team_size = team_size
        self.strict = strict
        self.rounds_completed = 0
        self.loser_rounds_completed = 0

        self.participants = []

        self.winners = []
        self.brackets = []

        self.loser_brackets = []
        self.losers = []

        self.team_data = {}


    @property
    def rounds(self):
        return len(self.participants) // 2


    def _checkSize(self, size):

        if size % 2 != 0 or size <= 0:
            raise SizeError


    def generate_bracket(self):

        if len(self.brackets) > 0:
            raise BracketAlreadyGenerated

        self._checkSize(len(self.participants))

        random.shuffle(self.participants)

        self.brackets = [(self.participants[i], self.participants[i+1]) for i in range(0,len(self.participants)-1, 2)]

        #Stops more people from joining once bracket generated
        self.size = len(self.participants)



        return self.brackets



    def add_participant(self, name : str, team_members : tuple):

        if len(self.participants) == self.size:
            raise MaxSizeReached


        if len(team_members) > self.team_size:
            raise MaxTeamSizeReached

        if self.strict and (len(team_members) < self.team_size):
            raise StrictError



        if name in self.participants:
            raise ParticipantAlreadyExists


        self.participants.append(name)

        self.team_data[name] = {
            'members': team_members,
            'wins' : 0,
            'loses' : 0,
        }




    def remove_participant(self, name : str):

        if len(self.participants) == 0:
            raise NoParticipants


        if name not in self.participants:
            raise ParticipantNotFound

        self.participants.remove(name)

        self.team_data.pop(name, None)


    def winner(self, name : str):

        self.rounds_completed += 1


        if name in self.winners or name in self.losers:
            raise NotInBracket

        if name not in self.participants:
            raise ParticipantNotFound

        for i in self.brackets:

            t1, t2 = i

            if t1.lower() == name.lower():
                self.winners.append(t1)
                self.losers.append(t2)
                self.team_data[t1]['wins'] += 1
                self.team_data[t2]['loses'] += 1
                self.brackets.remove(i)
                break

            if t2.lower() == name.lower():
                self.winners.append(t2)
                self.losers.append(t1)
                self.team_data[t2]['wins'] += 1
                self.team_data[t1]['loses'] += 1
                self.brackets.remove(i)
                break


        if len(self.winners) >= 2:
            x = self.winners[0]
            y = self.winners[1]
            self.brackets.append((x, y))
            self.winners.remove(x)
            self.winners.remove(y)


        if len(self.losers) >= 2:
            x = self.losers[0]
            y = self.losers[1]
            self.loser_brackets.append((x, y))
            self.losers.remove(x)
            self.losers.remove(y)


        if self.rounds_completed == len(self.participants)-1:
            return self.winners[0]



    def loser_bracket_winner(self, name : str):

        if name in self.losers and len(self.participants)-2 == 0:
            return self.losers[0]

        if name in self.winners or name in self.losers:
            raise NotInBracket


        if name not in self.participants:
            raise ParticipantNotFound


        self.loser_rounds_completed += 1


        for i in self.loser_brackets:

            t1, t2 = i

            if t1.lower() == name.lower():
                self.losers.append(t1)
                self.team_data[t1]['wins'] += 1
                self.team_data[t2]['loses'] += 1
                self.loser_brackets.remove(i)
                break

            if t2.lower() == name.lower():
                self.losers.append(t2)
                self.team_data[t2]['wins'] += 1
                self.team_data[t1]['loses'] += 1
                self.loser_brackets.remove(i)
                break


        if len(self.losers) >= 2:
            x = self.losers[0]
            y = self.losers[1]
            self.loser_brackets.append((x, y))
            self.losers.remove(x)
            self.losers.remove(y)


        if self.loser_rounds_completed == len(self.participants)-2:
            return self.losers[0]



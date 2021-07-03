from discord.ext.commands import CommandError


# Twitch and Youtube Plugin

# Raised when inputted Social does not exist in database
class SocialDoesNotExist(CommandError):
    pass

#Raised when inputted Social is already in database
class SocialAlreadyImplemented(CommandError):
    pass

#Raised when Social cannot be located
class SocialNotFound(CommandError):
    pass



#Giveaway Plugin

class CannotFindColour(CommandError):
    pass

class URLNotValid(CommandError):
    pass


class NoReactionsFound(CommandError):
    pass


class NoEntryFound(CommandError):
    pass


class SomethingWentWrong(CommandError):
    pass
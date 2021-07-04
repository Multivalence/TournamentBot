# Tournament Bot


# Setup

1. Install Python 3.8. **Make sure to check mark the "Add to Path" option when installing**
2. Download the repository and CD to it using terminal or command prompt
3. Install the required packages by doing `pip install -r requirements.txt` in the terminal
4. Get a Youtube Data API Key by going here and following the Getting Started Guide [YouTube Data API Overview](https://developers.google.com/youtube/v3/getting-started)
5. Get Twitch API client ID and secret by creating an Application here [Twitch Developer Console](https://dev.twitch.tv/console)
6. Download OpenJDK 13.0.2 from here [OpenJDK](https://jdk.java.net/archive/)
7. Download lavalink from here [Fredboat](https://ci.fredboat.com/viewLog.html?buildId=lastSuccessful&buildTypeId=Lavalink_Build&tab=artifacts&guest=1)
8. Drag lavalink.jar into the bin folder of the JDK folder
9. Drag application.yml (in this repository) to bin folder in JDK folder
10. CD into the bin directory by using terminal or command prompt then run the following command `java -jar lavalink.jar`
11. Get a discord bot token by creating an application here [Discord Developer Console](https://discord.com/developers/applications)
12. Insert all neccessary data in the .env file (in this repository). Note that all channels must be given as IDS
13. CD to the Tournament Bot directory then run the command `python app.py`
14. txt files in the customize folder (in this repository) can be customized to your liking. However, there are default messages already in there.

***Note**: You must have the lavalink server open in parallel with the bot for the music plugin to function*

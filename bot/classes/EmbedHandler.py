import json
import discord
import config as cfg
import datetime
from classes.GuildHandler import GuildHandler

# Overarching handler
class EmbedHandler ( ):

    # Custom embed class
    class CustomEmbed( discord.Embed ):
        def __init__(self, *, guildHandler, channel_name, **kwargs):
            super().__init__(**kwargs)
            self.guildHandler = guildHandler
            self.channel_name = channel_name
            self.channel_obj = None
            self.guild = None

        def set_channel_obj( self, msg_channel:discord.channel):
        
            # check if embed can be sent anywhere
            if self.channel_name == "" and msg_channel != None:

                # set the channel obj
                self.channel_obj = msg_channel
            
            # A channel has been named
            else:
                self.channel_obj = self.guild.get_channel_obj( self.channel_name )

        def set_guild(self, guild):
            self.guild = self.guildHandler.new_guild( guild )

        async def send(self, guild, msg_channel:discord.channel=None):
            """Sends the embed to the assigned channel."""

            # Set embed parameters
            self.set_guild( guild )
            self.set_channel_obj( msg_channel )

            # send the embed
            if self.channel_obj is not None:

                # Send the embed
                async with self.channel_obj.typing():


                    await self.channel_obj.send(embed=self)
            else:
                raise ValueError(f"Embed '{self.title}' needs a channel in order to be sent!.")

    # init
    def __init__(self):

        self.guildHandler = GuildHandler()

        self._json_file = cfg.json_file

        self._color_map = {
            "DEFAULT":cfg.dft_color,
            "SUCCESS":cfg.success_color,
            "FAILURE":cfg.error_color
        }

        self.guild = None

        with open(self._json_file, 'r') as embed_file:
            self.messages = json.load(embed_file)

    async def get_embed(self, key, **kwargs):

        # get embed format
        data = self._get_embed_format( key )

        # retrieve channel name 
        channel_name = data.get("channel")

        # create embed with channel obj
        embed = EmbedHandler.CustomEmbed(
            title=data.get("title").format(**kwargs),             # format the title w args
            description=data.get("description").format(**kwargs), # format the body w args
            color=self._color_map[(data.get("color"))],           # Get the hex color
            channel_name = channel_name,                           # set destination channel
            timestamp=datetime.datetime.now(tz=datetime.timezone.utc),             
            guildHandler=self.guildHandler
        )

        # return the embed
        return embed
    
    def _get_embed_format( self, key ):

        data = self.messages.get(key)

        if not data:
            raise ValueError(f"Embed key '{key}' not found in configuration.")
        
        return data
    
    def set_guild(self, guild):
        self.guild = guild

def _example():

    guild = discord.guild
    embed_handler = EmbedHandler(guild)

    '''
    Assume regular bot stuff here
    '''

    # @bot.event
    async def on_member_join(member):
        """
        Handles the event when a member joins the server.
        Sends a welcome embed message to the configured channel.
        """
        guild = member.guild
        try:
            embed = await embed_handler.get_embed("welcome", mention=member.mention)
            destination_channel = embed.get_channel()
            if destination_channel:
                await destination_channel.send(embed=embed)
        except Exception as e:
            print(f"Error sending welcome message: {e}")


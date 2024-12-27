import discord
from discord.utils import get

# Overarching guild class
class GuildHandler():

   # Custom class to build on top of native guild
    class CustomGuild():
        def __init__(self, guild: discord.Guild, required_channels, required_roles):
            self.guild = guild
            self.required_roles = required_roles
            self.required_channels = required_channels

        def get_channel_obj(self, channel_name):
            """Get a channel object by name."""
            return get(self.guild.channels, name=channel_name)

        def get_role_obj(self, role_name):
            """Get a role object by name."""
            return get(self.guild.roles, name=role_name)

        def validate_channel(self, channel_name):
            """Check if a channel exists in the guild."""
            return self.get_channel_obj(channel_name) != None

        def validate_channels(self, channel_names=None, verbose=False):
            """Validate the existence of multiple channels."""
            all_valid = True
            desc = ""

            channel_names = channel_names or self.required_channels
            for channel_name in channel_names:
                if not self.validate_channel(channel_name):
                    all_valid = False
                    desc += f"- Channel Error: `#{channel_name}` not found.\n"

            if verbose and desc:
                print(desc)

            return all_valid

        def validate_role(self, role_name):
            """Check if a role exists in the guild."""
            return self.get_role_obj(role_name) != None

        def validate_roles(self, role_names=None, verbose=False):
            """Validate the existence of multiple roles."""
            all_valid = True
            desc = ""

            role_names = role_names or self.required_roles
            for role_name in role_names:
                if not self.validate_role(role_name):
                    all_valid = False
                    desc += f"- Role Error: '{role_name}' does not exist.\n"

            if verbose and desc:
                print(desc)

            return all_valid

        def validate_guild(self):
            """Validate the guild setup."""
            channels_valid = self.validate_channels(verbose=False)
            roles_valid = self.validate_roles(verbose=False)
            return channels_valid and roles_valid
        

    def __init__(self, required_channels=None, required_roles=None) -> None:
        self.custom_guilds = []
        self.required_channels = required_channels or []
        self.required_roles = required_roles or []


    def add_guild( self, guild:discord.Guild ):

        # create custom guild obj
        custom_guild = self.CustomGuild(guild, self.required_channels, self.required_roles)

        # Add in valid guild
        if custom_guild.validate_guild:
            self.custom_guilds.append( custom_guild )

    def get_custom_guild( self, guild:discord.Guild ):
        
        # loop through our guilds
        for custom_guild in self.custom_guilds:
            
            # see if the guild matches
            if guild.id == custom_guild.id:
                
                # return correct guild
                return custom_guild
            
        # No guild found 
        return None
            
    def initialize_guilds( self, client ):

         # initialize variables
        guilds = client.guilds

        # loop through guilds
        for guild in guilds:

            # add custom guild object
            self.add_guild( guild )

    def new_guild(self, guild:discord.Guild ):

        #print(guild)

        return self.CustomGuild( guild, self.required_channels, self.required_roles )
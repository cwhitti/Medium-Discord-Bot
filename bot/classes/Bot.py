import secret as sc
import config as cfg
from classes.EmbedHandler import EmbedHandler 
from classes.GuildHandler import GuildHandler
from classes.SQLHandler import SQLHandler, Course
from classes.DatabaseHandler import DatabaseHandler

class Bot( EmbedHandler, SQLHandler, GuildHandler, DatabaseHandler ):

    '''
    PUBLIC FUNCTIONS
    '''

    async def handle_command( self, msg ):

        # initialize variables
        author_id = msg.author.id

        # Get command 
        argv = msg.content.split()
        command = argv[0].lower()

        # check if command is valid
        if command in self.commands.keys():

            # Grab the command tuple
            selected_option = self.commands.get( command ) 

            # Ensure permissions, currently owner-only
            if author_id != self.owner and selected_option[2] == True:

                embed = await self.get_embed("unauthorized-user", 
                                            guild=msg.guild)

                return embed # return early

            # run the selected option
            embed = await selected_option[0]( msg )

        # Command not in the command dictionary
        else:  
            embed = await self.get_embed("invalid-command", 
                                            guild=msg.guild,
                                            prefix = self.prefix)

        return embed

    async def hello(self, msg):

        embed = await self.get_embed("hello",
                             guild=msg.guild,
                             prefix = self.prefix)

        return embed
        
    async def help(self, msg):

        # Help command, sorry this isnt more automatic. 
        # You'll have to write it out for now
        desc=f'''Hi, thanks for using {self.name}! 
        
        This bot was created by Claire Whittington. Try out the list of commands below:
        
        🤖💬
        
        '''

        # iterate through the commands
        for trigger, tuple in self.commands.items():
            
            # get desc
            text = tuple[1]
            admin_only = tuple[2]

            if self._is_admin( msg.author ) or not admin_only:

                desc += f"**{trigger}**: {text}\n"

        return await self.get_embed("help", 
                                    guild = msg.guild, 
                                    desc = desc)
    
    async def update_database(self, msg=None):

        # initialize variables
            # None

        # try to update the db
        try: 

            self.insert( Course(id=1001, name="CS126") )
            self.insert( Course(id=1002, name="CS126L", section="001") )
            self.insert( Course(id=1003, name="CS126L", section="002") )
            self.insert( Course(id=1004, name="CS126L", section="003") )
            self.insert( Course(id=5005, name="CS249", section="001") )
            self.insert( Course(id=5006, name="CS249", section="002") )

            # We wanna make some updates!
            updates={"name": "CS126 - Combo Class"}

            # Update a course's name
            if self.needs_update(Course, record_id=1001, updates=updates):
                self.update(Course, record_id=1001, updates=updates)

            self.ready = True
            
        # Error in updating database
        except Exception as e:
            
            # Bot is not ready :(
            self.ready = False

        # get the summary
        return self.ready

    '''
    PRIVATE FUNCTIONS
    '''
    def __init__(self, name, client, prefix, dft_color, TOKEN):

        # Define ready flag
        self.ready = False

        # initialize important stuff
        self.client     = client    # discord client o bject
        self.name       = name      # str
        self.dft_color  = dft_color # hex
        self.prefix     = prefix    # str
        self.token      = TOKEN     # str | TODO: make this environmental variable

        # initialize additional file variables
        self.invite_link = sc.invite_link # str
        self.admin_list = cfg.admin_list  # list of ints (discord IDs)
        self.owner      = cfg.owner       # int (discord ID)

        # validation stuff
        self.required_roles    = [ ] # list of string names for roles
        self.required_channels = [ "general" ] # list of string names for channels

        # initialize inherited classes
        DatabaseHandler.__init__( self )
        GuildHandler.__init__( self )
        EmbedHandler.__init__( self )
        SQLHandler.__init__( self, cfg.db_path, dbg=True )

        # initialize all available commands for users to call
        self.commands = {   
                            self.prefix + "hello": ( self.hello,
                                                    "Test me to say hello!",
                                                    False
                            ),
                            self.prefix + "help": ( self.help, # command to run
                                                    "List of commands", # help desc
                                                    False, # is admin-only command
                            ),
                            self.prefix + "update":(
                                                self.update_database,
                                                "Force-updates the database.",
                                                True
                            ),
                        }
    def _is_admin(self, author):
        return author.id in self.admin_list
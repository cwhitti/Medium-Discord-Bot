import discord
import secret as sc
import config as cfg
from classes.Bot import Bot
from discord.ext import tasks

def run_discord_bot():

    # Set up bot
    intents = discord.Intents.default()
    intents.message_content = True
    client = discord.Client( intents=intents )

    # initialize variables
    name      = cfg.name
    prefix    = cfg.prefix
    dft_color = cfg.dft_color
    token     = sc.TOKEN

    # initialize bot
    bot = Bot(name, client, prefix, dft_color, token)

    # Task loop to update data periodically
    @tasks.loop(hours=cfg.HOURS_UPDATE)  
    async def passive_update_database():
        await bot.update_database() 
        # await embed.send()

    @client.event
    async def on_guild_join(guild): # check if we need to update bot on a new join
        bot.add_guild( guild )
        pass

    # Show bot logged on successfully
    @client.event
    async def on_ready():

        # change bot's presence
        await client.change_presence(activity=discord.Game(name=f"Hi, I'm {bot.name}! Try {bot.prefix}help"))

        # initialize client guilds 
        bot.initialize_guilds( bot.client )

        # Start database updating coroutine
        print("Updating database...")
        passive_update_database.start()

        # Print bot is now running
        print(f"{bot.name} is now running!")

    # Message Handler
    @client.event
    async def on_message(msg):

        # Don't listen to self
        if msg.author == client.user or msg.attachments:
            return

        # Handle commands
        if msg.content.startswith( bot.prefix ):
            
            # Bot is not ready to handle messages yet as it hasn't synced yet
            if not bot.ready:

                embed = await bot.get_embed("bot-not-ready", 
                                        mention=msg.author.mention)
            
            # handle the command, grab the embed
            else:
                embed = await bot.handle_command( msg )

            await send_embed( embed, msg.guild, msg.channel )
            
            return

    # Run Bot with Token
        # Should be  the very last command inside of run_discord_bot 
    client.run( bot.token )

async def send_embed( embed, guild, channel ):
    # Send 
    if embed != None:
        await embed.send( guild, channel )

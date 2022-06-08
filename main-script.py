from json import load, dump
from validators import url
from datetime import datetime
from multiprocessing import Pool

# Banned words list
banned_words = open("bannedWords.txt", "r").read().split('\n')

# Automod bypass roles
bypass_roles = [980663462457909322, 980663462457909321, 980663462457909320]

### Link Bypass Channel
##links_allowed = 

# Mod Info Channel
mod_channel = 980663463028342818

# Guild ID
guild_id = 980663462457909318

# Discord integration module
import discord
from discord.ext import commands

TOKEN = open("token.txt", "r").read()

intents = discord.Intents.default()
intents.members = True

client = commands.Bot(command_prefix='!', intents=intents)

# Commands
@commands.command()
async def member_channel_update():
    member_count = 0
    for m in client.get_guild(980663462457909318).members:
        if any([r.id == 980663462457909319 for r in m.roles]):
            member_count = member_count + 1
    member_channel_name = "|| Member Count: "+str(member_count)+" ||"
    await client.get_channel(983071241143484436).edit(name=member_channel_name)

@commands.command()
async def online_channel_update():
    online_count = 0
    for m in client.get_guild(980663462457909318).members:
        if any([r.id == 980663462457909319 for r in m.roles]) and m.status != discord.Status.offline:
            online_count = online_count + 1
    online_channel_name = "|| Players Online: "+str(online_count)+" ||"
    await client.get_channel(983071451101933588).edit(name=online_channel_name)

@commands.command()
async def ghost_sudo(ctx):
    if not any([r.id in bypass_roles for r in ctx.author.roles]):
        return
    await ctx.delete()
    await ctx.channel.send(ctx.content[7:])

# Discord event listeners
@client.event
async def on_ready():
    print(f'{client.user} is running!')
    await member_channel_update()
    await online_channel_update()

@client.event
async def on_connect():
    print("Connected to Discord")

@client.event
async def on_disconnect():
    print("Disconnected; attempting to reconnect...")

@client.event
async def on_member_join(member):
    await member_channel_update()

@client.event
async def on_member_leave(member):
    await member_channel_update()

@client.event
async def on_message_delete(ctx):
    if ctx.content.startswith('d!sudo'):
        return
    now = datetime.now()
    footer = f"Author ID: {ctx.author.id} | Message ID: {ctx.id} • " + now.strftime("%H:%M ")
    embed=discord.Embed(title="", color=0xee00ff)
    embed.set_author(name=ctx.author, icon_url=ctx.author.avatar_url)
    embed.add_field(name=f"Message sent by @{ctx.author.name} deleted in #{ctx.channel.name}", value=ctx.content, inline=False)
    embed.set_footer(text=footer)
    await client.get_channel(mod_channel).send(embed=embed)

@client.event
async def on_message_edit(before, after):
    now = datetime.now()
    footer = f"Author ID: {after.author.id} | Message ID: {after.id} • " + now.strftime("%H:%M ")
    embed=discord.Embed(title=f"Message edited in #{after.channel.name}", color=0xee00ff)
    embed.set_author(name=after.author, icon_url=after.author.avatar_url)
    embed.add_field(name="Before", value=before.content, inline=False)
    embed.add_field(name="After", value=after.content, inline=False)
    embed.set_footer(text=footer)
    await client.get_channel(mod_channel).send(embed=embed)

@client.event
async def on_message(ctx):
    user_warnings = load(open("userWarnings.txt"))
    await member_channel_update()
    await online_channel_update()
    
    if not str(ctx.author) in user_warnings:
        user_warnings[str(ctx.author)] = 0
    
    if ctx.author == client.user:
        return
    
    if ctx.author.bot:
        return
    
    if ctx.content.startswith('d!sudo'):
        await ghost_sudo(ctx)
    
    # Admin escape
    if not any([x in [y.id for y in ctx.author.roles] for x in bypass_roles]):
        
##        # Link ban
##        if not ctx.channel.id in links_allowed:
##            if url(ctx.content):
##                await ctx.delete()
##                user_warnings[str(ctx.author)] = user_warnings[str(ctx.author)] + 0.5
##                print(f"Deleted message with link by user '{ctx.author}':\n\"{ctx.content}\"")
        
        # Word ban
        if any(check in banned_words for check in ctx.content.split()):
            await ctx.delete()
            user_warnings[str(ctx.author)] = user_warnings[str(ctx.author)] + 1
            print(f"Deleted message with banned word by user '{ctx.author}':\n\"{ctx.content}\"")
        
        # Moderator flag-down
        if user_warnings[str(ctx.author)] >= 3:
            await client.get_channel(mod_channel).send(f"User '{ctx.author}' has reached 3 moderation points.")
    
    # JSON dump
    dump(user_warnings, open("userWarnings.txt", "r+"))

client.run(TOKEN)

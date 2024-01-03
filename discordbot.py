import discord
from discord.commands import Option
from database import db

ADMIN_IDS = [None]

accountsCollection = db["accounts"]

bot = discord.Bot(intents=discord.Intents.all())

cmdgroup = bot.create_group("ip", "Control database IPs")

@bot.event
async def on_ready():
    await bot.change_presence(
        activity=discord.Activity(
            type=discord.ActivityType.listening, name="to arshan's commands!"
        )
    )
    print("Ready!")

@cmdgroup.command(pass_context=True, description="Add an IP to the database!", options=[Option(str, name="username", description="Username", required=True), Option(str, name="ip", description="IP Address", required=True)])
async def add(ctx, user, ip):
    if ctx.author.id not in ADMIN_IDS:
        await ctx.respond("You can't use this command!")
        return
    # Check if user exists
    if accountsCollection.find_one({"username": user}) == None:
        await ctx.respond("User does not exist!")
        return
    # Check if IP is valid
    if len(ip.split(".")) != 4:
        await ctx.respond("Invalid IP!")
        return
    # Check if IP is already in database
    if ip in accountsCollection.find_one({"username": user})["ip"]:
        await ctx.respond("IP already exists!")
        return
    # Add IP to database
    accountsCollection.update_one({"username": user}, {"$push": {"ip": ip}})
    await ctx.respond(accountsCollection.find_one({"username": user})["ip"])

@cmdgroup.command(pass_context=True, description="Remove an IP from the database!", options=[Option(str, name="username", description="Username", required=True), Option(str, name="ip", description="IP Address", required=True)])
async def remove(ctx, user, ip):
    if ctx.author.id not in ADMIN_IDS:
        await ctx.respond("You can't use this command!")
        return
    # Check if user exists
    if accountsCollection.find_one({"username": user}) == None:
        await ctx.respond("User does not exist!")
        return
    # Check if IP is valid
    if len(ip.split(".")) != 4:
        await ctx.respond("Invalid IP!")
        return
    # Check if IP is already in database
    if ip not in accountsCollection.find_one({"username": user})["ip"]:
        await ctx.respond("IP does not exist!")
        return
    # Remove IP from database
    accountsCollection.update_one({"username": user}, {"$pull": {"ip": ip}})
    await ctx.respond(accountsCollection.find_one({"username": user})["ip"])
    
@cmdgroup.command(pass_context=True, description="Get all IPs from the database!", options=[Option(str, name="username", description="Username", required=True)])
async def get(ctx, user):
    if ctx.author.id not in ADMIN_IDS:
        await ctx.respond("You can't use this command!")
        return
    # Check if user exists
    if accountsCollection.find_one({"username": user}) == None:
        await ctx.respond("User does not exist!")
        return
    # Get all IPs from database
    await ctx.respond(accountsCollection.find_one({"username": user})["ip"])


bot.run(None) # Token goes here

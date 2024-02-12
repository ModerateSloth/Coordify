## Author: Jaymin Jhaveri

# For env
from dotenv import load_dotenv
import os
# Discord import
import discord
from discord.ext import commands
# Datetime
import datetime
from datetime import datetime
# sqlite3
import sqlite3
# For pattern matching
import re
# Testing
import pytest

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

intent = (discord.Intents.all())
client = discord.Client(intents=intent)
bot = commands.Bot(command_prefix='::', intents=intent)

## DEBUG ##
debug = False

sqlcon = sqlite3.connect("coordify.db")
cursor = sqlcon.cursor()
cursor.execute("CREATE TABLE IF NOT EXISTS events(server, year, month, day, event, UNIQUE(server, year, month, day, event))")

options = (
    "Usage:\n"
+   "::commands        |   Brings up this menu any time\n"
+   "::add                      |   To add an event\n"
+   "::remove               |   To remove an event\n"
+   "::view                     |   To view this month"
)

incorrect_add = ("Usage: ::add [\"event\"] ['mm/dd/yyyy']\nUse quotes for events with multiple words\n*No brackets*")
incorrect_view = ("Usage: ::view *Optional*['mm/dd/yyyy']\n*No brackets*")
no_special = ("Special characters ': *' not allowed!")
incorrect_remove = ("Usage: ::remove [\"event\"]['mm/dd/yyyy']\nUse '*' to remove all for a given date\n*No brackets*")

@bot.event
async def on_ready():
    print(f'{bot.user} has connected to Discord!')
    for guild in bot.guilds:
        print(guild.name)
        print(guild.id)

@bot.command()
async def commands(ctx, *args):
    await ctx.send(options)

@bot.command()
async def test(ctx):
   global testnum
   testnum = 1

def check_err(month):
    return re.fullmatch("../../....", month) == None

def parse_month(mon) -> list:
    return (mon.split('/'))

def list_itr(results) -> str:
    out = ""
    i = 1
    for entry in results:
        out += str(i) + ")\n"
        out += "Date: " + entry[2] + "/" + entry[3] + "/" + entry[1] + "\n"
        out += "Event: " + entry[4] + "\n"
        out += "\n"
        i += 1
    return out

@bot.command()
async def view(ctx, *args):
    server = str(ctx.message.guild.id)
    if len(args) == 0:
        thismonth = str(datetime.now().month)
        thisyear = str(datetime.now().year)
        print(thismonth)
        print(thisyear)
        query = f"SELECT * FROM events WHERE server={server} AND year='{thisyear}' AND month='{thismonth}'"
        res = cursor.execute(query)
        out = cursor.fetchall()
        listing = list_itr(out)
        if len(listing) == 0:
            await ctx.send("NO EVENTS TO SHOW FOR THIS MONTH")
            return True
        msg = "ALL EVENTS FROM THIS MONTH:\n"
        msg += listing
        print(msg)
        if len(msg) == 0:
            await ctx.send("No events to show")
            return True
        else:
            await ctx.send(msg)
            return True
    elif len(args) == 1:
        if check_err(args[0]):
            await ctx.send(incorrect_view)
            return False
        else:
            date = parse_month(args[0])
            month = date[0]
            day = date[1]
            year = date[2]
            query = f"SELECT * FROM events WHERE server={server} AND year='{year}' AND month='{month}' AND day='{day}'"
            res = cursor.execute(query)
            out = cursor.fetchall()
            msg = list_itr(out)
            await ctx.send(msg)
            return True

@bot.command()
async def add(ctx, *args):
    server = str(ctx.message.guild.id)
    
    if len(args) == 0 or len(args) == 1:
        await ctx.send(incorrect_add)
        return False
    else:
        if check_err(args[1]):
            await ctx.send(incorrect_add)
            return False
        elif args[1] == ":" or args[1] == "*":
            await ctx.send(no_special)
            return False
        else:
            event = args[0]
            date = args[1]
            seperate = parse_month(date)
            month = seperate[0]
            day = seperate[1]
            year = seperate[2]
            thismonth = str(datetime.now().month)
            thisyear = str(datetime.now().year)
            thisday = str(datetime.now().day)
            if int(year) < int(thisyear):
                await ctx.send("Cannot add an event in the past!")
                return False
            elif int(month) < int(thismonth):
                await ctx.send("Cannot add an event in the past!")
                return False
            elif int(day) < int(thisday):
                await ctx.send("Cannot add an event in the past!")
                return False
            else:
                query_add = f"INSERT OR IGNORE INTO events (server, year, month, day, event) VALUES ({server}, '{year}', '{month}', '{day}', '{event}')"
                res = cursor.execute(query_add)
                cursor.connection.commit()
                st = f"Added/Attempted to add: \"{event}\"" + " on " + date + "."
                await ctx.send(st)
                return True

@bot.command()
async def remove(ctx, *args):
    if len(args) == 0:
        await ctx.send(incorrect_remove)
        return False
    elif len(args) == 1:
        event = args[0]
        if event == "!ALL":
            query_rem = f"DELETE FROM events WHERE server='{str(ctx.message.guild.id)}'"
            res = cursor.execute(query_rem)
            cursor.connection.commit()
            st = "REMOVED ALL EVENTS"
            await ctx.send(st)
            return True
        else:
            await ctx.send(incorrect_remove)
            return True
    else:
        event = args[0]
        date = args[1]
        seperate = parse_month(date)
        month = seperate[0]
        day = seperate[1]
        year = seperate[2]
        # If *
        if event == "*":
            query_rem = f"DELETE FROM events WHERE year='{year}' AND month='{month}' AND day='{day}'"
            res = cursor.execute(query_rem)
            cursor.connection.commit()
            st = f"Removed/Attempted to remove: ALL EVENTS on {month}/{day}/{year}"
            await ctx.send(st)
            return True
        else:
            query_rem = f"DELETE FROM events WHERE year='{year}' AND month='{month}' AND day='{day}' AND event='{event}'"
            res = cursor.execute(query_rem)
            cursor.connection.commit()
            st = f"Removed/Attempted to remove: \"{event}\" on {month}/{day}/{year}"
            await ctx.send(st)
            return True

@bot.command()
async def debug(ctx, *args):
    global debug
    if len(args) != 1:
        return
    elif args[0] == "-t":
        debug = True
        await ctx.send("Debugging on")
    elif args[0] == "-f":
        debug = False
        await ctx.send("Debugging off")

@bot.listen('on_message')
async def send(message):
    if message.author == bot.user:
        return
    
    if message.content == ('::'):
        await message.channel.send(options)

bot.run(TOKEN)
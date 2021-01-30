import os
import sqlite3
import random
import uuid
import datetime

import discord
from discord.ext import commands

TOKEN = "INSERT TOKEN HERE"
GUILD = "INSERT DISCORD SERVER ID HERE"

bot = commands.Bot(command_prefix=';')
encryption_log = "INSERT CHANNELID TO PRINT ENCRYPTED MESSAGES TO HERE"
bot_actions = "INSERT CHANNELID TO PRINT ALL BOT ACTIONS TO HERE"



@bot.event
async def on_ready():
    print("on_ready just happened!")
    activity = discord.Activity(name='over the Kapteyn system.', type=discord.ActivityType.watching)
    await bot.change_presence(activity=activity)
    channel_ba = bot.get_channel(bot_actions)
    await channel_ba.send("Repulsion Bot is now live!")


@bot.command(name='encrypt', help='Can be used to send encrypted messages to another player. '
                                  'Format messages as ;encrypt recipient_ID "message goes here, including the quotes".')
async def encrypt(ctx, sendee, sent_text):
    message = ctx.message
    sender = message.author
    sendeeLower = sendee.lower()
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute("""SELECT * FROM playerIDs WHERE identifier = ?""", (sendeeLower,))
    nickname = c.fetchone()

    if nickname != None:
        user = bot.get_user(int(nickname[1]))
    else:
        await ctx.send("Oops! Can't find recipient. Make sure they're in the database, or contact a ref for help.")
        return
    encryptID = str(uuid.uuid1())
    sendee_channel = await user.create_dm()
    sender_channel = await sender.create_dm()
    channel_el = bot.get_channel(encryption_log)
    await sendee_channel.send("You have received an encrypted message on channel " + encryptID + ":" + "\n" +
                              sent_text)
    await sender_channel.send("You have successfully sent a message on encrypted channel " + encryptID + ":" + "\n" +
                              sent_text)
    # print(channel_el)
    await channel_el.send(str(sender) + " sent a message to " + str(user) + ":" + "\n" + sent_text)
    print(sender, "sent a message to", user, ":", sent_text)
    # await bot.send_message(sent_text)

@bot.command(name='add_nick', help='Adds nicknames for players to be used in ;encrypt instead of their Discord IDs.')
async def add_nick(ctx, nickname, userID):
    print("add_nick just happened!")
    nickLower = nickname.lower()
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute("""SELECT * FROM playerIDs WHERE identifier = ?""", (nickLower,))
    row = c.fetchone()
    print(row)
    if row != None:
        await ctx.send('Nickname already in table!')
    else:
        c.execute("""INSERT INTO playerIDs VALUES (?, ?)""", (nickLower, userID,))
        conn.commit()
        conn.close()
        await ctx.send('Successfully added player to players database!')
        channel_ba = bot.get_channel(bot_actions)
        await channel_ba.send("A player nickname has been added to the database. Player " + userID +
                              " may now be referred to as " + nickLower + ".")

@bot.command(name='remove_nick', help='Removes nicknames for players to be used in ;encrypt instead of their Discord IDs.')
async def remove_nick(ctx, nickname, userID):
    print("remove_nick just happened!")
    nickLower = nickname.lower()
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute("""SELECT * FROM playerIDs WHERE identifier = ?""", (nickLower,))
    row = c.fetchone()
    # print(c.fetchone())
    if row == None:
        await ctx.send('Nickname not in table!')
    else:
        c.execute("""DELETE FROM playerIDs WHERE identifier = ?""", (nickLower,))
        conn.commit()
        conn.close()
        await ctx.send('Successfully removed nickname from players database!')
        channel_ba = bot.get_channel(bot_actions)
        await channel_ba.send("A player nickname has been removed from the database. Player " + userID +
                              " may no longer be referred to as " + nickLower + ".")


@bot.command(name='nick_all', help='Displays all nicknames and their respective player IDs.')
async def nick_all(ctx):
    print("nick_all just happened!")
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute("""SELECT * FROM playerIDs""")
    rows = c.fetchall()
    text = "Here are all of the currently implemented nicknames:\n"
    for row in rows:
        text += row[0] + ' = ' + row[1] + '\n'
    await ctx.send(text)
    conn.close()

@bot.command(name='nick_player', help='Displays all nicknames for a specific user ID.')
async def nick_player(ctx, user_ID):
    print("nick_player just happened!")
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute("""SELECT * FROM playerIDs WHERE userID = ?""", (user_ID,))
    rows = c.fetchall()
    text = "Here are all of the currently implemented nicknames for this user (case insensitive):\n"
    for row in rows:
        text += row[0] + ', '
    await ctx.send(text)
    conn.close()

print("Starting bot")
bot.run(TOKEN)
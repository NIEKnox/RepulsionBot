import sqlite3
import uuid

import discord
from discord.ext import commands

TOKEN = "INSERT TOKEN HERE"
GUILD = "INSERT DISCORD SERVER ID HERE"

bot = commands.Bot(command_prefix=';')
encryption_log = "INSERT CHANNELID TO PRINT ENCRYPTED MESSAGES TO HERE"
bot_actions = "INSERT CHANNELID TO PRINT ALL BOT ACTIONS TO HERE"

ref1 = "INSERT USER ID OF REF 1 IN HERE" # Comment as to who this number corresponds to
ref2 = "INSERT USER ID OF REF 2 IN HERE" # Comment as to who this number corresponds to

refs = [ref1, ref2] # Refs can be added to this list indefinitely

@bot.event
async def on_ready():
    print("on_ready just happened!")
    activity = discord.Activity(name='over the Kapteyn system.', type=discord.ActivityType.watching)
    await bot.change_presence(activity=activity)
    channel_ba = bot.get_channel(bot_actions)
    await channel_ba.send("Repulsion Bot is now live!")


@bot.command(name='encrypt', help='Can be used to send encrypted messages to another player. '
                                  'Format messages as ;encrypt recipient_nickname "message goes here, not necessarily the quotes".')
async def encrypt(ctx, *sent_text):
    if len(sent_text) == 0:
        await ctx.send("Not enough data sent!")
        return
    if len(sent_text) == 1:
        await ctx.send("You must send something to this user!")
        return
    sendee = sent_text[0]
    encrypted_message = ' '.join(sent_text[1::])
    sender = ctx.author
    sendeeLower = sendee.lower()
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute("""SELECT * FROM playerIDs WHERE identifier = ?""", (sendeeLower,))
    nickname = c.fetchone()
    if nickname != None:
        user_id = int(nickname[1])
        user = await bot.fetch_user(user_id)
    else:
        await ctx.send("Oops! Can't find recipient. Make sure they're in the database, or contact a ref for help.")
        return
    encryptID = str(uuid.uuid1())
    sendee_channel = await user.create_dm()
    channel_el = bot.get_channel(encryption_log)
    await sendee_channel.send("You have received an encrypted message on channel " + encryptID + ":" + "\n" +
                              encrypted_message)
    await ctx.send("You have successfully sent a message on encrypted channel " + encryptID + ":" + "\n" +
                              encrypted_message)
    # print(channel_el)
    await channel_el.send(str(sender) + " sent a message to " + str(user) + ":" + "\n" + encrypted_message)
    print(sender, "sent a message to", user, ":", encrypted_message)

    c.execute("""SELECT * FROM bugs WHERE target = ?""", (str(sender.id),))
    sender_rows = c.fetchall()
    if sender_rows != []:
        for row in sender_rows:
            bug_id = row[0]
            placer_id = int(row[2])
            activations = int(row[3])
            new_activations = activations-1
            placer = await bot.fetch_user(placer_id)
            await placer.send("A bug you placed on " + str(sender) + " has picked up a message:\n" + encrypted_message + "\nYour bug has "
                              + str(new_activations) + " uses left!")
            if new_activations <= 0:
                c.execute("""DELETE FROM bugs WHERE bugID = ?""", (bug_id,))

            else:
                c.execute('''UPDATE bugs SET activations = ? WHERE bugID = ?''', (new_activations, bug_id,))

    c.execute("""SELECT * FROM bugs WHERE target = ?""", (str(user_id),))
    receiver_rows = c.fetchall()
    # print(receiver_rows)
    if receiver_rows != []:
        for row in receiver_rows:
            bug_id = row[0]
            placer_id = int(row[2])
            activations = int(row[3])
            new_activations = activations-1
            placer = await bot.fetch_user(placer_id)
            await placer.send("A bug you placed on " + str(user) + "has picked up a message:\n" + encrypted_message + "\nYour bug has "
                              + str(new_activations) + " uses left!")
            if new_activations <= 0:
                c.execute("""DELETE FROM bugs WHERE bugID = ?""", (bug_id,))

            else:
                c.execute('''UPDATE bugs SET activations = ? WHERE bugID = ?''', (str(new_activations), bug_id,))

    conn.commit()
    conn.close()

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

@bot.command(name='place_bug', help='Places a bug on another player. Format using ;place_bug target, where target can be the nickname of a target.')
async def place_bug(ctx, nickname):
    setter = ctx.author
    setter_id = setter.id
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute("""SELECT userID FROM playerIDs WHERE identifier = ?""", (nickname,))
    existing_bug = c.fetchone()
    target_id = existing_bug[0]
    c.execute("""SELECT * FROM bugs WHERE target = ? AND setter = ?""", (str(target_id),str(setter_id),))
    row = c.fetchone()
    print(row)
    if row != None:
        await ctx.send("You have already placed a bug on this player! It has sent " + str((3 - int(row[3]))) + " messages!")
    else:
        bugID = str(uuid.uuid1())
        print(str(target_id), str(setter_id))
        c.execute("""INSERT INTO bugs VALUES (?, ?, ?, ?)""", (str(bugID), str(target_id), str(setter_id), 3,))
        conn.commit()
        await ctx.send("You have successfully placed a bug on " + nickname + "!")
    conn.close()

@bot.command(name='bugs', help='Lists all placed bugs. FOR REF USE ONLY!')
async def bugs(ctx):
    user = ctx.author
    user_id = user.id
    channel_ba = bot.get_channel(bot_actions)
    if user_id not in refs:
        await ctx.send("You are not authorised to execute this command!")
        await channel_ba.send("Player " + str(user_id) + " just tried to access bugs!")
        return
    print("Bugs just happened!")
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute("""SELECT * FROM bugs""")
    rows = c.fetchall()
    text = "Here are all of the currently active bugs:\n"
    for row in rows:
        text += 'Bug ' + row[0] + ': ' + row[2] + ' has placed a bug on ' + row[1] + '. It has ' + str(row[3]) + ' uses left!\n'
    await ctx.send(text)
    conn.close()

@bot.command(name='purge_bugs', help='Removes all placed bugs. FOR REF USE ONLY!')
async def purge_bugs(ctx):
    user = ctx.author
    user_id = user.id
    channel_ba = bot.get_channel(bot_actions)
    if user_id not in refs:
        await ctx.send("You are not authorised to execute this command!")
        await channel_ba.send("Player " + str(user_id) + " just tried to purge all bugs!")
        return
    print("Purge bugs just happened!")
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute("""DELETE FROM bugs""")
    await ctx.send("All bugs have been purged. Long live the debuggers.")
    conn.commit()
    conn.close()

@bot.command(name='place_bug_ref', help='Allows the manual setting of bugs. Format ;place_bug_ref target setter number of uses. FOR REF USE ONLY!')
async def place_bug_ref(ctx, target, setter, uses):
    user = ctx.author
    user_id = user.id
    channel_ba = bot.get_channel(bot_actions)
    if user_id not in refs:
        await ctx.send("You are not authorised to execute this command!")
        await channel_ba.send("Player " + str(user_id) + " just tried to purge all bugs!")
        return
    print("Place bug ref just happened!")
    bugID = str(uuid.uuid1())
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute("""SELECT userID FROM playerIDs WHERE identifier = ?""", (target.lower(),))
    target_row = c.fetchone()
    target_id = target_row[0]
    c.execute("""SELECT userID FROM playerIDs WHERE identifier = ?""", (setter.lower(),))
    setter_row = c.fetchone()
    setter_id = setter_row[0]
    c.execute("""INSERT INTO bugs VALUES (?, ?, ?, ?)""", (str(bugID), str(target_id), str(setter_id), str(uses),))
    await ctx.send("A bug has been manually placed on " + str(target) + ", and will now send messages " + str(uses)
                          + " times to " + str(setter) + ". Thank you for your service, Ref!")
    await channel_ba.send("A bug has been manually placed on " + str(target) + ", and will now send messages " + str(uses)
                          + " times to " + str(setter) + ".")
    conn.commit()
    conn.close()

@bot.command(name='remove_bug', help='Removes a specific placed bug. FOR REF USE ONLY!')
async def remove_bug(ctx, bug_id):
    user = ctx.author
    user_id = user.id
    channel_ba = bot.get_channel(bot_actions)
    if user_id not in refs:
        await ctx.send("You are not authorised to execute this command!")
        await channel_ba.send("Player " + str(user_id) + " just tried to remove a bug!")
        return
    print("Remove bug just happened!")
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute("""DELETE FROM bugs WHERE bugID=?""", (str(bug_id),))
    await ctx.send("A bug has been purged. Please press F.")
    conn.commit()
    conn.close()

print("Starting bot")
bot.run(TOKEN)
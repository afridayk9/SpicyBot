import discord
import random
import os
import json
import requests
import asyncio
from discord.ext import commands, tasks
from discord.utils import get
from twitchAPI.twitch import Twitch


client = commands.Bot(command_prefix='!', intents=discord.Intents.all())



@client.event
async def on_ready():
    print("Spicy bot is ready for use")
    print("--------------------------")

#Anthony Friday
@client.command()
async def hello(ctx):
    await ctx.send("Hello, I am Spicy Bot!")

@client.command()
async def joke(ctx):
    with open("jokes.txt", "r", encoding="utf-8") as file:
        jokes = file.readlines()
    random_joke = random.choice(jokes).strip()
    await ctx.send(random_joke)

@client.command()
async def insult(ctx):
        with open("yomomma.txt", "r", encoding="utf-8") as file:
             insults = file.readlines()
        random_insult = random.choice(insults).strip()
        await ctx.send(random_insult)

#https://www.youtube.com/watch?v=AHdb8K6BHLY&list=PLShlsXPw8HheSzjp6avwGdMFVQxsJOK2P&index=1&t=105s
#The following command was created using the above video

#Twitch API authentication
client_id = "uhxflhcvb06gqws8hb8yczuowmi0fb"
client_secret = "34z8bvrk2efe5uvp5w395x2f1lc0c7"
twitch = Twitch(client_id, client_secret)
twitch.authenticate_app([])
TWITCH_STREAM_API_ENDPOINT_V5 = "https://api.twitch.tv/kraken/streams/{}"
API_HEADERS = {
    'Client-ID': client_id,
    'Accept': 'application/vnd.twitchtv.v5+json',
}

# Returns true if online, false if not.
async def checkuser(user):
    try:
        async for user_data in twitch.get_users(logins=[user]):
            userid = user_data['id']
            url = TWITCH_STREAM_API_ENDPOINT_V5.format(userid)
            try:
                req = await requests.Session().get(url, headers=API_HEADERS)
                jsondata = req.json()
                if 'stream' in jsondata:
                    if jsondata['stream'] is not None:
                        return True
                    else:
                        return False
            except Exception as e:
                print("Error checking user: ", e)
                return False
    except IndexError:
        return False
    
# Executes when bot is started
@client.event
async def on_ready():
    # Defines a loop that will run every 10 seconds (checks for live users every 10 seconds).
    @tasks.loop(seconds=10)
    async def live_notifs_loop():
        # Opens and reads the json file
        with open('streamers.json', 'r') as file:
            streamers = json.loads(file.read())
        # Makes sure the json isn't empty before continuing.
        if streamers is not None:
            # Gets the guild, 'twitch streams' channel, and streaming role.
            guild = client.get_guild(1212108998963232798)
            channel = client.get_channel(1212108999663558688)
            role = get(guild.roles, id=1213179914669400104)
            # Loops through the json and gets the key,value which in this case is the user_id and twitch_name of
            # every item in the json.
            for user_id, twitch_name in streamers.items():
                # Takes the given twitch_name and checks it using the checkuser function to see if they're live.
                # Returns either true or false.
                status = checkuser(twitch_name)
                # Gets the user using the collected user_id in the json
                user = client.get_user(int(user_id))
                # Makes sure they're live
                if status is True:
                    # Checks to see if the live message has already been sent.
                    async for message in channel.history(limit=200):
                        # If it has, break the loop (do nothing).
                        if str(user.mention) in message.content and "is now streaming" in message.content:
                            break
                        # If it hasn't, assign them the streaming role and send the message.
                        else:
                            # Gets all the members in your guild.
                            async for member in guild.fetch_members(limit=None):
                                # If one of the id's of the members in your guild matches the one from the json and
                                # they're live, give them the streaming role.
                                if member.id == int(user_id):
                                    await member.add_roles(role)
                            # Sends the live notification to the 'twitch streams' channel then breaks the loop.
                            await channel.send(
                                f":red_circle: **LIVE**\n{user.mention} is now streaming on Twitch!"
                                f"\nhttps://www.twitch.tv/{twitch_name}")
                            print(f"{user} started streaming. Sending a notification.")
                            break
                # If they aren't live do this:
                else:
                    # Gets all the members in your guild.
                    async for member in guild.fetch_members(limit=None):
                        # If one of the id's of the members in your guild matches the one from the json and they're not
                        # live, remove the streaming role.
                        if member.id == int(user_id):
                            await member.remove_roles(role)
                    # Checks to see if the live notification was sent.
                    async for message in channel.history(limit=200):
                        # If it was, delete it.
                        if str(user.mention) in message.content and "is now streaming" in message.content:
                            await message.delete()
    # Start your loop.
    live_notifs_loop.start()


# Command to add Twitch usernames to the json.
@client.command(name='addtwitch', help='Adds your Twitch to the live notifs.', pass_context=True)
async def add_twitch(ctx, twitch_name):
    # Opens and reads the json file.
    with open('streamers.json', 'r') as file:
        streamers = json.loads(file.read())
    
    # Gets the users id that called the command.
    user_id = ctx.author.id
    # Assigns their given twitch_name to their discord id and adds it to the streamers.json.
    streamers[user_id] = twitch_name
    
    # Adds the changes we made to the json file.
    with open('streamers.json', 'w') as file:
        file.write(json.dumps(streamers))
    # Tells the user it worked.
    await ctx.send(f"Added {twitch_name} for {ctx.author} to the notifications list.")

#Bailey Wilson
@client.command(name='blackjack', help='Play Blackjack with the bot. Use !blackjack <bet> to place your bet.')
async def blackjack(ctx, bet: int):

    if bet <= 0:
        await ctx.send("Please enter a valid bet greater than 0.")
        return

    player_hand = [draw_card(), draw_card()]
    dealer_hand = [draw_card(), draw_card()]

    await ctx.send(f'Your hand: {", ".join(map(str, player_hand))}\nDealer\'s hand: {dealer_hand[0]}, ?')

    while sum(player_hand) < 21:
        response = await get_player_response(ctx, "Do you want to hit or stand? Type `hit` or `stand`.")
        if response == 'timeout':
            await ctx.send("Time's up! You didn't make a decision in time.")
            return
        elif response == 'hit':
            player_hand.append(draw_card())
            await ctx.send(f'Your hand: {", ".join(map(str, player_hand))}\nDealer\'s hand: {dealer_hand[0]}, ?')
        elif response == 'stand':
            break
        else:
            await ctx.send("Invalid input. Please type `hit` or `stand`.")

    while sum(dealer_hand) < 17:
        dealer_hand.append(draw_card())

    winner = determine_winner(player_hand, dealer_hand)

    await ctx.send(f'Your hand: {", ".join(map(str, player_hand))}\nDealer\'s hand: {", ".join(map(str, dealer_hand))}')
    await ctx.send(f'Winner: {winner.capitalize()}! {ctx.author.mention} {"won" if winner == "player" else "lost"} {bet} credits.')

def draw_card():
    return random.randint(1, 11)

async def get_player_response(ctx, message):
    def check(m):
        return m.author == ctx.author and m.channel == ctx.channel and m.content.lower() in ['hit', 'stand']

    await ctx.send(message)
    try:
        response = await client.wait_for('message', timeout=10.0, check=check)
        return response.content.lower()
    except asyncio.TimeoutError:
        return 'timeout'
    

def determine_winner(player_hand, dealer_hand):
    player_total = sum(player_hand)
    dealer_total = sum(dealer_hand)

    if player_total > 21:
        return 'dealer'
    elif dealer_total > 21:
        return 'player'
    elif player_total == dealer_total:
        return 'draw'
    elif player_total > dealer_total:
        return 'player'
    else:
        return 'dealer'
    
#Douglas Perry

async def scramble(word):
    return ''.join(random.sample(word, len(word)))

@client.command()
async def scramblegame(ctx):
    with open("randomwords.txt", "r", encoding="utf-8") as file:
       word = file.readlines()
    
    random_word = random.choice(word).strip()
    scrambled_word = await scramble(random_word)
    embed = discord.Embed(title="Guess the Word!", description = f"Scrambled word: {scrambled_word}")
    embed.set_footer(text="Time Limit: 10 Seconds")
    await ctx.send (embed=embed)

    try:
        def check(msg):
            return msg.author == ctx.author and msg.channel == ctx.channel

        guess = await client.wait_for("message", timeout=10.0, check=check)
        guess = guess.content.lower()

        if guess == random_word.lower():
            await ctx.send("Correct! You guessed the word in time.")
        else:
            await ctx.send("Wrong Guess! The word was: " + random_word)

    except asyncio.TimeoutError:
        await ctx.send("Time's up! You didn't guess the word in time. The word was: " + random_word)

with open("token.txt") as file:
    token = file.read()

client.run(token)



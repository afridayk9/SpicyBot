import discord
import random
import asyncio
import requests
import aiohttp
import pytz
import datetime
from discord.ext import commands
from igdb.wrapper import IGDBWrapper
from requests import post



client = commands.Bot(command_prefix='!', intents=discord.Intents.all())
client_id = "uhxflhcvb06gqws8hb8yczuowmi0fb"
client_secret = "ozt8nao0bsr3rujvkl2ke6tvp8x0ce"
base_url = "https://api.igdb.com/v4"

@client.event
async def on_ready():
    print("Spicy bot is ready for use")
    print("--------------------------")



#Anthony Friday
async def get_access_token():
    access_token_url = post (f"https://id.twitch.tv/oauth2/token?client_id={client_id}&client_secret={client_secret}&grant_type=client_credentials")
    #print ("access token: %s" % str(access_token_url.json()))
    access_token = access_token_url.json().get('access_token')
    return access_token

async def fetch_todays_releases():    
    access_token = await get_access_token()      
    headers = {
        'Client-ID': client_id,
        'Authorization': f'Bearer {access_token}',
    }
    # Get today's date in the format required by IGDB
    current_date = datetime.datetime.now(datetime.timezone.utc).date()
    day_start = int(datetime.datetime.combine(current_date, datetime.time.min).timestamp())
    print("Day Start: ", day_start)
    day_end = int(datetime.datetime.combine(current_date, datetime.time.max).timestamp())
    print("Day End: ", day_end)       
    
    async with aiohttp.ClientSession() as session:
        print("fetch releases client session")
        async with session.post(f'{base_url}/release_dates', **{'headers': headers, 'data': 'fields date,game;'}) as response:
            #print("fetch response :", response)
            if response.status == 200:
                todays_releases = await response.json()
                print("today's releases:", todays_releases)
                return todays_releases
            else:
                raise Exception(f"Failed to fetch release dates: {response.status} - {response.reason}")

async def fetch_games():
    print("made it inside fetch_games")    
    access_token = await get_access_token()    
    headers = {
        "Client-ID": client_id,
        "Authorization": f"Bearer {access_token}",
    }

    todays_releases = await fetch_todays_releases()
    todays_games = []

    for games in todays_releases:
        game_id = games.get('game')
        todays_games.append(game_id)
    
    print("todays game list:", todays_games)

    for game_info in todays_games:
        
        async with aiohttp.ClientSession() as session:
            print("fetch game aiohttp client session")
            async with session.post(f"{base_url}/games", **{'headers' : headers, 'data': f'fields name, genres, platforms; where id={game_info}'}) as response:

                if response.status == 200:
                    games = await response.json()
                    print("games: ", games)
                    return games
                else:
                    raise Exception(f"Failed to fetch games:  {response.status} - {response.reason} ")
    else:
        print("No Releases for today.")


@client.command()
async def releases(ctx):
    try:        
        access_token = await get_access_token()
        # Fetch game IDs released today
        game_ids = await fetch_todays_releases()
        #await ctx.send(await fetch_todays_releases()) #for debug purposes
        if game_ids:
            # Fetch detailed information about the games based on the IDs
            games_info = await fetch_games()
            game_info = []            
            for game in games_info:
                # Extract the desired fields from each game
                name = game.get('name')
                genres = ', '.join(game.get('genres', []))
                platforms = ', '.join(game.get('platforms', []))
                game_info.append(f"Name: {name}\nGenres: {genres}\nPlatforms: {platforms}\n")
            # Send the formatted game information to the Discord channel
            await ctx.send("\n".join(game_info))
        else:
            await ctx.send("No games released today.")
    except Exception as e:
        await ctx.send(f"Error occurred: {e}")

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
    
@client.command(name='8ball', help='Ask the magic 8-ball a question.')
async def magic_8_ball(ctx, *, question):
    responses = [
        "Yes, because the universe revolves around you.",
        "No, and you should've seen that coming.",
        "Ask again later, or don't.",
        "Cannot predict now, but I predict your confusion will continue.",
        "Don't count on it, but feel free to blame the 8-ball for your problems.",
        "Maybe",
        "Definitely! Just kidding, I have no idea.",
        "No chance."
    ]

    response = random.choice(responses)
    await ctx.send(f'Magic 8-ball says: {response}')

    try:
        def check(m):
            return m.author == ctx.author and m.channel == ctx.channel

        await client.wait_for('message', timeout=10.0, check=check)
    except asyncio.TimeoutError:
        await ctx.send("Time's up! You didn't ask another question in time.")



#Douglas Perry

async def scramble(word):
    return ''.join(random.sample(word, len(word)))

@client.command()
async def scramble(ctx):
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



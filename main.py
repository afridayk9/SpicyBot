import discord
import random
import asyncio
import datetime
import json
from discord.ext import commands
from igdb.wrapper import IGDBWrapper
from requests import post



client = commands.Bot(command_prefix='!', intents=discord.Intents.all())
base_url = "https://api.igdb.com/v4"

with open("client_id.txt") as file:
    client_id = file.read()

with open("client_secret.txt") as file:
    client_secret = file.read()

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
    print("inside fetch_todays_releases")    
    access_token= await get_access_token()
    wrapper = IGDBWrapper(client_id, access_token)

    current_date = datetime.datetime.now(datetime.timezone.utc).date()
    day_start = int(datetime.datetime.combine(current_date, datetime.time(hour=0,minute=0,second=0)).timestamp())
    tomorrow = current_date + datetime.timedelta(days=1)
    day_end = int(datetime.datetime.combine(tomorrow, datetime.time.max).timestamp())
    print("day_start:", day_start)
    print("day_end:", day_end)


    todays_releases = wrapper.api_request(
        'release_dates',
        f'fields game; where date >= {day_start} & date < {day_end};'
    )

    response_str = todays_releases.decode('utf-8')
    response_json = json.loads(response_str)
    #print("return from fetch_release_dates: ", response_json)
    return response_json

async def fetch_genres(id):
    #print("inside fetch_genres")
    access_token = await get_access_token()
    wrapper = IGDBWrapper(client_id, access_token)

    genres = wrapper.api_request(
        'genres',
        f'fields name; where id={id}'
    )

    response_str = genres.decode('utf-8')
    response_json = json.loads(response_str)
    print("return from fetch_genres: ", response_json)
    return response_json

#use the id of the platform retrieved from fetch_games to determine the platform name
async def fetch_platforms(id):
    print("inside fetch_platforms")
    access_token = await get_access_token()
    wrapper = IGDBWrapper(client_id, access_token)

    platforms = wrapper.api_request(
        'platforms',
        f'fields name; where id={id}'
    )

    response_str = platforms.decode('utf-8')
    response_json = json.loads(response_str)
    print("return from fetch_platforms: ", response_json)
    return response_json



async def fetch_games():
    print("inside fetch_games")
    access_token = await get_access_token()
    wrapper = IGDBWrapper(client_id, access_token)

    todays_releases = await fetch_todays_releases()
    todays_games = []
    print("todays releases", todays_releases)
    
    
    for release in todays_releases:
        game_id = release.get('game')
        todays_games.append(game_id)
    print("todays games:", todays_games)
    
    
    games_info = []
    for game_id in todays_games:
        byte_array = wrapper.api_request(
            'games',
            f'fields name, genres, platforms; where id={game_id};'
        )
        # Decode the byte array response into a string
        response_str = byte_array.decode('utf-8')
        # Parse the string into JSON
        response_json = json.loads(response_str)

        for game in response_json:
            for i, genre_id in enumerate(game['genres']):
                genre_array = wrapper.api_request(
                    'genres',
                    f'fields name; where id={genre_id};'
                )
                genre_str = genre_array.decode('utf-8')
                genre_json = json.loads(genre_str)
                game['genres'][i] = genre_json[0]['name']

        for game in response_json:
            for i, platform_id in enumerate(game['platforms']):
                platform_array = wrapper.api_request(
                    'platforms',
                    f'fields name; where id={platform_id};'
                )
                platform_str = platform_array.decode('utf-8')
                platform_json = json.loads(platform_str)
                game['platforms'][i] = platform_json[0]['name']

        games_info.append(response_json)

    return games_info

#https://api-docs.igdb.com/#getting-started
#https://github.com/twitchtv/igdb-api-python

@client.command()
async def releases(ctx):
    games_info = await fetch_games()
    for game in games_info:
        game_dict = game[0] 
        await ctx.send(f"Title: {game_dict['name']}\n Genres: {game_dict['genres']}\n Platforms: {game_dict['platforms']}\n *******************************\n")
    

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

user_points = {}

async def scrambler(word):
    return ''.join(random.sample(word, len(word)))

@client.command()
async def scramble(ctx):
    with open("randomwords.txt", "r", encoding="utf-8") as file:
       word = file.readlines()

    user_id = ctx.author.id
    if user_id not in user_points:
        user_points[user_id] = 0

    random_word = random.choice(word).strip()
    scrambled_word = await scrambler(random_word)
    embed = discord.Embed(title="Guess the Word!", description = f"Scrambled word: {scrambled_word}")
    embed.set_footer(text="Time Limit: 10 Seconds")
    await ctx.send (embed=embed)


    try:
        def check(msg):
            return msg.author == ctx.author and msg.channel == ctx.channel

        guess = await client.wait_for("message", timeout=10.0, check=check)
        guess = guess.content.lower()

        if guess == random_word.lower():
            user_points[user_id] += 1
            await ctx.send(f"Correct! You guessed the word in time. You have {user_points[user_id]} point(s)")
        else:
            if user_points[user_id] > 0:
                user_points[user_id] -= 1
            await ctx.send(f"Wrong Guess! The word was: {random_word}. You have {user_points[user_id]} point(s)")

    except asyncio.TimeoutError:
        if user_points[user_id] > 0:
            user_points[user_id] -= 1
        await ctx.send(f"Time's up! You didn't guess the word in time, the word was: {random_word}. You have {user_points[user_id]} point(s)")

@client.command()
async def points(ctx, member: discord.Member = None):
    if member is None:
            member = ctx.author
    if member.id not in user_points:
        user_points[member.id] = 0
    await ctx.send(f"{member.name} has {user_points[member.id]} point(s)")

with open("token.txt") as file:
    token = file.read()
    
client.run(token)

import discord
import random
import asyncio
import requests
import aiohttp
import pytz
from discord.ext import commands
from datetime import datetime

client = commands.Bot(command_prefix='!', intents=discord.Intents.all())
client_id = "uhxflhcvb06gqws8hb8yczuowmi0fb"
client_secret = "ozt8nao0bsr3rujvkl2ke6tvp8x0ce"

@client.event
async def on_ready():
    print("Spicy bot is ready for use")
    print("--------------------------")


#Anthony Friday
async def get_access_token():
    token_url = "https://id.twitch.tv/oauth2/token"
    params = {
        "client_id": client_id,
        "client_secret": client_secret,
        "grant_type": "client_credentials"
    }
    async with aiohttp.ClientSession() as session:
        async with session.post(token_url, params=params) as response:
            data = await response.json()
            return data.get("access_token")

async def fetch_release_dates(access_token):
    base_url = "https://api.igdb.com/v4"
    endpoint = "/games"
    fields = "name,genre,platforms,first_release_date,;"
    headers = {
        "Client-ID": client_id,
        "Authorization": f"Bearer {access_token}"
    }
    url = base_url + endpoint
    today = datetime.utcnow().strftime('%Y-%m-%d')
    data = {"fields": fields, "where": f"date = '{today}'"}
    async with aiohttp.ClientSession() as session:
        async with session.post(url, json=data, headers=headers) as response:
            return await response.json()

@client.command()
async def releases(ctx):
    try:
        access_token = await get_access_token()
        release_data = await fetch_release_dates(access_token)
        await ctx.send(release_data)
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



import discord
from discord.ext import commands
from dotenv import load_dotenv
import aiohttp
import sqlite3
import os
import random

# setup for auto-running the script when a new commit is available
with open('/root/WatchBuddies/pidfile', 'w') as f:
    f.write(str(os.getpid()))

load_dotenv()  # take environment variables from .env.

# setup for Discord
TOKEN = os.getenv('TOKEN')

#setup for TMDB
TMDB_API_KEY = os.getenv('TMDB_API_KEY')

intents = discord.Intents.all()
bot = commands.Bot(command_prefix='!', intents=intents)

# Connect to the SQLite database
conn = sqlite3.connect('movies.db')

# Create the default watchlist
c = conn.cursor()
c.execute('''
    CREATE TABLE IF NOT EXISTS movies (
        id INTEGER PRIMARY KEY,
        title TEXT NOT NULL,
        release_date TEXT NOT NULL
    )
''')
conn.commit()

# Create the watched list
c.execute('''
    CREATE TABLE IF NOT EXISTS watched_movies (
        id INTEGER PRIMARY KEY,
        title TEXT NOT NULL
    )
''')
conn.commit()

@bot.event
async def on_ready():
    print(f'We have logged in as {bot.user}')

@bot.command()
async def addmovie(ctx, *, movie_name):
    # Check if the movie already exists in the database
    c.execute("SELECT * FROM movies WHERE title = ?", (movie_name,))
    movie_exists = c.fetchone()
    
    if movie_exists:
        await ctx.send(f"{movie_name} is already in the watchlist.")
    else:
        async with aiohttp.ClientSession() as session:
            async with session.get(f'https://api.themoviedb.org/3/search/movie?api_key={TMDB_API_KEY}&query={movie_name}') as r:
                if r.status == 200:
                    js = await r.json()
                    if js['results']:
                        movie = js['results'][0]  # Get the first result
                        c.execute("INSERT INTO movies (title, release_date) VALUES (?, ?)", (movie['title'], movie['release_date']))
                        conn.commit()
                        await ctx.send(f"Added {movie['title']} to the watchlist!")
                    else:
                        await ctx.send(f"No movie found with the name '{movie_name}'.")
                else:
                    response = await r.text()
                    await ctx.send(f"API request failed with status {r.status} and response {response}.")

@bot.command()
async def removemovie(ctx, *, movie_name):
    # Remove the quotes around the movie name if present
    if movie_name.startswith('"') and movie_name.endswith('"'):
        movie_name = movie_name[1:-1]

    # Remove the movie from the database
    c.execute("DELETE FROM movies WHERE LOWER(title) = LOWER(?)", (movie_name,))
    rows_deleted = conn.total_changes
    if rows_deleted > 0:
        conn.commit()
        await ctx.send(f'Removed "{movie_name}" from the watchlist!')
    else:
        await ctx.send(f'Movie "{movie_name}" not found in the watchlist.')

@bot.command()
async def watchedmovie(ctx, *, movie_name):
    # Check if the movie exists in the watchlist
    c.execute("SELECT * FROM movies WHERE title = ?", (movie_name,))
    movie = c.fetchone()

    if movie:
        # Move the movie to the watched movies list
        c.execute("INSERT INTO watched_movies (title) VALUES (?)", (movie_name,))
        c.execute("DELETE FROM movies WHERE title = ?", (movie_name,))
        conn.commit()
        await ctx.send(f'Moved "{movie_name}" to the watched list.')
    else:
        await ctx.send(f'Movie "{movie_name}" not found in the watchlist.')

@bot.command()
async def viewlist(ctx):
    # Get all movies from the database
    c.execute("SELECT id, title FROM movies")
    movies = c.fetchall()
    if movies:
        movie_list = "\n".join(f"{movie[0]} - {movie[1]}" for movie in movies)
        await ctx.send(movie_list)
    else:
        await ctx.send("No movies in the watchlist.")

@bot.command()
async def viewwatchedlist(ctx):
    # Get all watched movies from the database
    c.execute("SELECT title FROM watched_movies")
    watched_movies = c.fetchall()

    if watched_movies:
        watched_movie_list = "\n".join(movie[0] for movie in watched_movies)
        await ctx.send(f"Watched movies:\n{watched_movie_list}")
    else:
        await ctx.send("No watched movies.")

@bot.command()
async def pickrandom(ctx, number: int):
    # Get all movies from the database
    c.execute("SELECT title FROM movies")
    all_movies = c.fetchall()

    if all_movies:
        # If there are fewer movies than the requested number, notify the user
        if len(all_movies) < number:
            await ctx.send(f"Only {len(all_movies)} movies in the watchlist. Unable to select {number} movies.")
        else:
            # Randomly select 'number' movies from the list
            selected_movies = random.sample(all_movies, number)
            movie_list = "\n".join(movie[0] for movie in selected_movies)
            await ctx.send(f"Randomly selected movies:\n{movie_list}")
    else:
        await ctx.send("No movies in the watchlist.")

@bot.command()
async def changelog(ctx):
    # Set GitHub repo details
    owner = "melissarios94"
    repo = "WatchBuddies"

    # GitHub API URL to fetch the latest commit
    url = f'https://api.github.com/repos/{owner}/{repo}/commits'

    # Make an HTTP request to the GitHub API
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            if response.status == 200:
                commits = await response.json()
                latest_commit = commits[0]['commit']['message']
                await ctx.send(f"Latest changelog: {latest_commit}")
            else:
                await ctx.send("Failed to fetch the changelog.")

@bot.command()
async def test(ctx):
    await ctx.send('Test successful!')


bot.run(TOKEN)

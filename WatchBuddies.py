import discord
from discord.ext import commands
from dotenv import load_dotenv
import aiohttp
import sqlite3
import os

load_dotenv()  # take environment variables from .env.

# setup for Discord
TOKEN = os.getenv('TOKEN')

#setup for TMDB
TMDB_API_KEY = os.getenv('TMDB_API_KEY')

intents = discord.Intents.all()
bot = commands.Bot(command_prefix='!', intents=intents)

# Connect to the SQLite database
conn = sqlite3.connect('movies.db')
c = conn.cursor()
c.execute('''
    CREATE TABLE IF NOT EXISTS movies (
        id INTEGER PRIMARY KEY,
        title TEXT NOT NULL,
        release_date TEXT NOT NULL
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
async def changelog(ctx):
    # Get the current directory
    current_dir = os.getcwd()
    
    # Construct the file path to the changelog
    changelog_path = os.path.join(current_dir, 'changelog.txt')
    
    # Print the absolute file path for debugging
    print(changelog_path)
    
    # Read the changelog
    with open(changelog_path, 'r') as file:
        lines = file.readlines()
        print(lines)
        
    if lines:
        # Get the first line of the changelog
        first_line = lines[0].strip()

        # Send the first line as a message
        await ctx.send(f"Changelog: {first_line}")
    else:
        await ctx.send("No changelog available.")

@bot.command()
async def test(ctx):
    await ctx.send('Test successful!')


bot.run(TOKEN)

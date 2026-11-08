
import discord
from discord.ext import commands
import os
import json

TOKEN = os.getenv("DISCORD_TOKEN")

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

BOT_ON = True

@bot.event
async def on_ready():
    print(f"Phantom-Mart is online as {bot.user}")

@bot.command()
@commands.has_permissions(administrator=True)
async def on(ctx):
    global BOT_ON
    BOT_ON = True
    await ctx.send("✅ Phantom-Mart listings are ON!")

@bot.command()
@commands.has_permissions(administrator=True)
async def off(ctx):
    global BOT_ON
    BOT_ON = False
    await ctx.send("⛔ Phantom-Mart listings are OFF!")

@bot.command()
@commands.has_permissions(administrator=True)
async def listing(ctx, channel: discord.TextChannel, *, details):
    if not BOT_ON:
        await ctx.send("Listings are currently OFF.")
        return

    embed = discord.Embed(
        title="🛒 PHANTOM-MART LISTING",
        description=details,
        color=discord.Color.blue()
    )
    embed.set_footer(text="Phantom-Mart | Official Store")

    await channel.send(embed=embed)
    await ctx.send("✅ Listing posted!")

bot.run(TOKEN)

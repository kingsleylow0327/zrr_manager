# bot.py
import discord
from discord.ext import commands
from modal.api_modal import APIModal
from modal.activate_modal import ActivateModal
from view.trader_view import TraderSelectView
from config import Config
from sql_con import ZonixDB
from bingx import BINGX

# Client setup
intents = discord.Intents.all()
intents.message_content = True
bot = commands.Bot(command_prefix="!",intents=intents)

# Bot setup
config = Config()

# DB Setup
dbcon = ZonixDB(config)

GUILD_ID = int(config.GUILD_ID)

@bot.event
async def on_ready():
    await bot.tree.sync()
    print("Manager Ready")

@bot.tree.command(name="api", description="Register API")
async def register(interaction: discord.Interaction):
    await interaction.response.send_modal(APIModal(dbcon))

@bot.tree.command(name="activate", description="Activate User")
async def activate(interaction: discord.Interaction):
    if not dbcon.is_admin(str(interaction.user.id)):
        await interaction.response.send_message("This function only limit to Admin", ephemeral=True)
        return
    await interaction.response.send_modal(ActivateModal(dbcon))

@bot.command()
async def trader(ctx: commands.Context):
    await ctx.send("Select Your Trader", view=TraderSelectView(dbcon), ephemeral=True)

@bot.command()
async def status(ctx: commands.Context):
    min_wallet = 200
    max_wallet = 1000
    player_id = str(ctx.author.id)
    if not dbcon.check_user_exist(player_id):
        message = """
        You have not registered to the system
        Please Contact ZRR Admin to register
        """
        await ctx.send(message, ephemeral=True)
        return
    trader_api = dbcon.get_player_status(player_id)[0]

    bingx = BINGX(trader_api.get("api_key"), trader_api.get("api_secret"))
    response = bingx.get_wallet()
    
    msg_api = "❌"
    msg_wallet_min = "❌"
    msg_wallet_max = "❌"
    msg_trader = ""
    if trader_api.get("trader_id"):
        msg_trader = "✅"

    if response.get("code") == 0 or response.get("code") == 200:
        msg_api = "✅"
        balance = float(response.get("data").get("balance").get("availableMargin"))
        if balance > float(min_wallet):
            msg_wallet_min = "✅"
        if balance < float(max_wallet):
            msg_wallet_max = "✅"

    embed = discord.Embed(title="Your ZRR status", description="")
    embed.add_field(name=f"API Setup: {msg_api} \n", value="", inline=False)
    embed.add_field(name=f"Wallet > {min_wallet}: {msg_wallet_min} \n", value="", inline=False)
    embed.add_field(name=f"Wallet < {max_wallet}: {msg_wallet_max} \n", value="", inline=False)
    embed.add_field(name=f"Following Traders: {msg_trader}", value="", inline=False)
    await ctx.send(embed=embed, ephemeral=True)

bot.run(config.TOKEN)
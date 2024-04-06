# bot.py
import discord
import message as ms
from discord.ext import commands
from datetime import datetime
from modal.api_modal import APIModal
from modal.activate_modal import ActivateModal
from modal.extend_modal import ExtendModal
from view.trader_view import TraderSelectView
from view.damage_view import DamageSelectView
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

def within_valid_period(date_time):
    current_date = datetime.now()
    if current_date.day in range(1, 31):
        return (date_time.month <= current_date.month and date_time.year <= current_date.year)
    return False

@bot.event
async def on_ready():
    await bot.tree.sync()
    print("Manager Ready")

@bot.tree.command(name="api", description="Register API")
async def register(interaction: discord.Interaction):
    if interaction.channel.id != int(config.COMMAND_CHANNEL_ID):
        return True
    await interaction.response.send_modal(APIModal(dbcon))

@bot.tree.command(name="activate", description="Activate User")
async def activate(interaction: discord.Interaction):
    if interaction.channel.id != int(config.COMMAND_CHANNEL_ID):
        return True
    if not dbcon.is_admin(str(interaction.user.id)):
        await interaction.response.send_message("This function only limit to Admin", ephemeral=True)
        return
    await interaction.response.send_modal(ActivateModal(dbcon))

@bot.tree.command(name="extend", description="Extend Users Expiry")
async def extend(interaction: discord.Interaction):
    if interaction.channel.id != int(config.COMMAND_CHANNEL_ID):
        return True
    if not dbcon.is_admin(str(interaction.user.id)):
        await interaction.response.send_message("This function only limit to Admin", ephemeral=True)
        return
    await interaction.response.send_modal(ExtendModal(dbcon))

@bot.tree.command(name="trader", description="Select Trader")
async def trader(interaction: discord.Interaction, user_account_name: str):
    user_account_name = user_account_name.lower()
    if interaction.channel.id != int(config.COMMAND_CHANNEL_ID):
        return True
    player_id = str(interaction.user.id)
    if not user_account_name:
        await interaction.response.send_message(ms.MISSING_ACCOUNT_NAME, ephemeral=True)
        return
    if not dbcon.check_user_exist_with_ref(player_id, user_account_name):
        await interaction.response.send_message(ms.NON_REGISTERED, ephemeral=True)
        return
    player_status = dbcon.get_player_status(player_id, user_account_name)
    if player_status.get("following_time") and not within_valid_period(player_status.get("following_time")):
        await interaction.response.send_message(ms.SELECTED_TRADER, ephemeral=True)
        return
    following_trader_id = player_status.get("trader_id")
    player = BINGX(player_status.get("api_key"), player_status.get("api_secret"))

    await interaction.response.send_message(content="Please Select a Trader", view=TraderSelectView(dbcon, user_account_name, player, following_trader_id), ephemeral=True)

@bot.tree.command(name="damage", description="Amend Damage Cost")
async def damage(interaction: discord.Interaction, user_account_name: str):
    user_account_name = user_account_name.lower()
    if interaction.channel.id != int(config.COMMAND_CHANNEL_ID):
        return True
    player_id = str(interaction.user.id)
    if not user_account_name:
        await interaction.response.send_message(ms.MISSING_ACCOUNT_NAME, ephemeral=True)
        return
    if not dbcon.check_user_exist_with_ref(player_id, user_account_name):
        await interaction.response.send_message(ms.NON_REGISTERED, ephemeral=True)
        return
    await interaction.response.send_message("Select Your Damage Cost", view=DamageSelectView(dbcon, user_account_name), ephemeral=True)   

@bot.tree.command(name="status", description="Check Status")
async def status(interaction: discord.Interaction, id:str=None):
    if interaction.channel.id != int(config.COMMAND_CHANNEL_ID):
        return True
    min_wallet = 300
    max_wallet = 3000
    player_id = str(interaction.user.id)
    is_admin_flag = False
    if dbcon.is_admin(player_id):
        is_admin_flag = True
        if id is not None and id.strip() != "":
            player_id = id

    trader_api_list = dbcon.get_all_player_status(player_id)
    if not trader_api_list:
        await interaction.response.send_message(ms.NON_REGISTERED, ephemeral=True)
        return
    
    embed_list = []
    count = 1
    for trader_api in trader_api_list:
        embed = discord.Embed(title=f"# Your AutoTrade Account {count} Status", description="")
        bingx = BINGX(trader_api.get("api_key"), trader_api.get("api_secret"))
        response = bingx.get_wallet()
        
        uid = "❌"
        msg_api = "❌"
        msg_wallet_min = "❌"
        msg_wallet_max = "❌"
        msg_trader = "❌"
        balance = "❌"
        expiry = "None"
        if trader_api.get('expiry_date'):
            expiry = trader_api.get('expiry_date')

        if trader_api.get("trader_id"):
            msg_trader = f" `{trader_api.get('trader_id')}`"

        if response.get("code") == 0 or response.get("code") == 200:
            msg_api = "✅"
            uid = str(response.get("data").get("balance").get("userId"))
            balance = float(response.get("data").get("balance").get("availableMargin"))
            if balance > float(min_wallet):
                msg_wallet_min = "✅"
            if balance < float(max_wallet):
                msg_wallet_max = "✅"

        if is_admin_flag:
            embed.add_field(name=f"BingX UserId: {uid}", value="", inline=False)
        embed.add_field(name=f"Account Name: {trader_api.get('player_id')} \n", value="", inline=False)
        embed.add_field(name=f"\n", value="", inline=False)
        embed.add_field(name=f"API Setup: {msg_api} \n", value="", inline=False)
        embed.add_field(name=f"Future Wallet > {min_wallet}: {msg_wallet_min} \n", value="", inline=False)
        embed.add_field(name=f"Future Wallet < {max_wallet}: {msg_wallet_max} \n", value="", inline=False)
        embed.add_field(name=f"Wallet Amount: `{balance}`", value="", inline=False)
        embed.add_field(name=f"\n", value="", inline=False)
        embed.add_field(name=f"Following Traders: {msg_trader}", value="", inline=False)
        embed.add_field(name=f"Damage Cost: `{trader_api.get('damage_cost')}%`", value="", inline=False)
        embed.add_field(name=f"Expiry Date: `{expiry}`", value="", inline=False)
        embed_list.append(embed)
        count += 1
    
    await interaction.response.send_message(embeds=embed_list, ephemeral=True)

bot.run(config.TOKEN)
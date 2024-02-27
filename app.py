# bot.py
import discord
import message as ms
from discord.ext import commands
from datetime import datetime
from modal.api_modal import APIModal
from modal.activate_modal import ActivateModal
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
    await interaction.response.send_modal(APIModal(dbcon))

@bot.tree.command(name="activate", description="Activate User")
async def activate(interaction: discord.Interaction):
    if not dbcon.is_admin(str(interaction.user.id)):
        await interaction.response.send_message("This function only limit to Admin", ephemeral=True)
        return
    await interaction.response.send_modal(ActivateModal(dbcon))

@bot.command()
async def trader(ctx: commands.Context, arg=None):
    player_id = str(ctx.author.id)
    if not arg:
        await ctx.send(ms.MISSING_REF_NAME, ephemeral=True)
        return
    if not dbcon.check_user_exist_with_ref(player_id, arg):
        await ctx.send(ms.NON_REGISTERED, ephemeral=True)
        return
    player_status = dbcon.get_player_status(player_id, arg)
    if player_status.get("following_time") and not within_valid_period(player_status.get("following_time")):
        await ctx.send(ms.SELECTED_TRADER, ephemeral=True)
        return
    following_trader_id = player_status.get("trader_id")
    await ctx.send("Select Your Trader", view=TraderSelectView(dbcon, arg, following_trader_id), ephemeral=True)
    player = BINGX(player_status.get("api_key"), player_status.get("api_secret"))
    pos_ret = player.close_all_pos()
    order_ret = player.close_all_order()
    if pos_ret.get("code") == 0:
        await ctx.send(ms.CLOSED_POS, ephemeral=True)
    else:
        await ctx.send(ms.ERROR_CLOSED_POS, ephemeral=True)
    if order_ret.get("code") == 0:
        await ctx.send(ms.CLOSED_ORDER, ephemeral=True)
    else:
        await ctx.send(ms.ERROR_CLOSED_ORDER, ephemeral=True)

@bot.command()
async def damage(ctx: commands.Context, arg=None):
    player_id = str(ctx.author.id)
    if not arg:
        await ctx.send(ms.MISSING_REF_NAME, ephemeral=True)
        return
    if not dbcon.check_user_exist_with_ref(player_id, arg):
        await ctx.send(ms.NON_REGISTERED, ephemeral=True)
        return
    await ctx.send("Select Your Damage Cost", view=DamageSelectView(dbcon, arg), ephemeral=True)   

@bot.command()
async def status(ctx: commands.Context, id=None):
    min_wallet = 200
    max_wallet = 1000
    player_id = str(ctx.author.id)
    is_admin_flag = False
    if dbcon.is_admin(player_id):
        is_admin_flag = True
        if id is not None and id.strip() != "":
            player_id = id

    trader_api_list = dbcon.get_all_player_status(player_id)
    if not trader_api_list:
        await ctx.send(ms.NON_REGISTERED, ephemeral=True)
        return
    
    embed = discord.Embed(title="Your ZRR status", description="")
    for trader_api in trader_api_list:
        bingx = BINGX(trader_api.get("api_key"), trader_api.get("api_secret"))
        response = bingx.get_wallet()
        
        msg_api = "❌"
        msg_wallet_min = "❌"
        msg_wallet_max = "❌"
        msg_trader = ""
        if trader_api.get("trader_id"):
            msg_trader = f" ***{trader_api.get('trader_id')}***"

        if response.get("code") == 0 or response.get("code") == 200:
            msg_api = "✅"
            uid = str(response.get("data").get("balance").get("userId"))
            balance = float(response.get("data").get("balance").get("availableMargin"))
            if balance > float(min_wallet):
                msg_wallet_min = "✅"
            if balance < float(max_wallet):
                msg_wallet_max = "✅"

        if is_admin_flag and (response.get("code") == 0 or response.get("code") == 200):
            embed.add_field(name=f"BingX UserId: {uid}", value="", inline=False)
        embed.add_field(name=f"Ref Id: {trader_api.get('player_id')} \n", value="", inline=False)
        embed.add_field(name=f"API Setup: {msg_api} \n", value="", inline=False)
        embed.add_field(name=f"Wallet > {min_wallet}: {msg_wallet_min} \n", value="", inline=False)
        embed.add_field(name=f"Wallet < {max_wallet}: {msg_wallet_max} \n", value="", inline=False)
        embed.add_field(name=f"Following Traders: {msg_trader}", value="", inline=False)
        embed.add_field(name=f"Damage Cost: {trader_api.get('damage_cost')}%", value="", inline=False)
        if is_admin_flag and (response.get("code") == 0 or response.get("code") == 200):
            embed.add_field(name=f"Wallet Amount: {balance}", value="", inline=False)
        embed.add_field(name=f"=====\n", value="", inline=False)
    await ctx.send(embed=embed, ephemeral=True)

bot.run(config.TOKEN)
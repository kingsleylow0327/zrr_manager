# bot.py
import asyncio
import discord
import message as ms
import schedule
import json
from dto.license_dto import LicenseDTO
from discord.ext import commands
from datetime import datetime
from logger import Logger
from modal.activate_modal import ActivateModal
from modal.extend_modal import ExtendModal
from service.new_account import create_new_account
from service.resubscribe import resubscribe
from service.cancel_subscribe import cancel_subscribe
from view.master_view import MasterView
from view.status_view import StatusView
from config import Config
from sql_con import ZonixDB
from bingx import BINGX

# Logger setup
logger_mod = Logger("Manager")
logger = logger_mod.get_logger()

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
    if current_date.day in range(1, 8):
        return (date_time.month <= current_date.month and date_time.year <= current_date.year)
    return False

@bot.event
async def on_ready():
    await bot.tree.sync()
    logger.info("Manager Ready")
    await run_scheduler()

# License command
@bot.event
async def on_message(message):
    if message.author == int(config.ZONIX_ID):  # Ignore messages from the bot itself
        return
    if message.channel.id == int(config.LICENCE_CHANNEL_ID) and message.author == int(config.PAYMENT_BOT_ID):
        try:
            json_msg = json.loads(message.content)
            license_dto = LicenseDTO.from_json(json_msg)
            guild = bot.get_guild(GUILD_ID)
            # New Account
            if license_dto.type == "create":
                logger.info(f"Created!")
                await create_new_account(dbcon, license_dto, guild)
            # Renew Subs
            elif license_dto.type == "renew":
                await resubscribe(dbcon, license_dto, guild)
            elif license_dto.type == "cancel":
                await cancel_subscribe(dbcon, license_dto, guild)
        except Exception as e:
            logger.error(e)
    await bot.process_commands(message)

@bot.tree.command(name="zrrdev_clearex", description="AutoTrade Manager Command")
async def clearex(interaction: discord.Interaction):
    if interaction.channel.id != int(config.COMMAND_CHANNEL_ID):
        return True
    if interaction.channel.id != int(config.COMMAND_CHANNEL_ID):
        return True
    if not dbcon.is_admin(str(interaction.user.id)):
        await interaction.response.edit_message("This function only limit to Admin", view=None)
        return True
    await interaction.response.send_message("Clearing Start", ephemeral=True)
    await clear_expired()
    return True

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

@bot.tree.command(name="atm", description="AutoTrade Manager")
async def atm(interaction: discord.Interaction):
    await interaction.response.defer(ephemeral=True)
    if interaction.channel.id != int(config.COMMAND_CHANNEL_ID):
        return True
    player_id = str(interaction.user.id)
    user_account_list = dbcon.get_all_player_status(player_id)
    license_list = dbcon.get_license(player_id)
    if not user_account_list and not license_list:
        await interaction.followup.send(content=ms.NO_ACCOUNT, ephemeral=True)
        return
    status_view = StatusView(dbcon, interaction, user_account_list)
    embeded_status_list = status_view.compute()
    await interaction.followup.send(content="Welcome to AutoTrade Manager", embeds=embeded_status_list, view=MasterView(dbcon, user_account_list, license_list), ephemeral=True)

@bot.tree.command(name="api", description="API setup")
async def register(interaction: discord.Interaction, account_name: str, key: str, secret: str):
    if interaction.channel.id != int(config.COMMAND_CHANNEL_ID):
        return True
    await interaction.response.defer(ephemeral=True)
    player_id = str(interaction.user.id)
    if not dbcon.check_user_exist_with_ref(player_id, account_name):
        await interaction.followup.send(content=ms.NON_REGISTERED, ephemeral=True)
        return
    dbcon.set_player_api(player_id, key, secret, account_name)
    await interaction.followup.send(content="API Set", ephemeral=True)

@bot.tree.command(name="status", description="Check Status")
async def status(interaction: discord.Interaction, id:str):
    await interaction.response.defer(ephemeral=True)
    if interaction.channel.id != int(config.COMMAND_CHANNEL_ID):
        return True

    player_id = str(interaction.user.id)
    if not dbcon.is_admin(player_id):
        return True

    min_wallet = 300
    max_wallet = 3000

    trader_api_list = dbcon.get_all_player_status(id)
    if not trader_api_list:
        await interaction.followup.send(ms.NON_REGISTERED, ephemeral=True)
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

        if trader_api.get("trader_name"):
            msg_trader = f" `{trader_api.get('trader_name')}`"

        if response.get("code") == 0 or response.get("code") == 200:
            msg_api = "✅"
            uid = str(response.get("data").get("balance").get("userId"))
            balance = float(response.get("data").get("balance").get("availableMargin"))
            if balance > float(min_wallet):
                msg_wallet_min = "✅"
            if balance < float(max_wallet):
                msg_wallet_max = "✅"

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
    
    await interaction.followup.send(embeds=embed_list, ephemeral=True)

async def clear_expired():
    logger.info("Cron Job:Clearing Start")
    expired_player_list = dbcon.get_expired_user()
    player_name_list = []
    logger.info(f"Cron Job:{len(player_name_list)} user to be cleared")
    if not expired_player_list:
        logger.info("Cron Job:Clearing Expired User Done")
        return True
    guild = bot.get_channel(int(config.COMMAND_CHANNEL_ID)).guild
    for player_info in expired_player_list:
        user = guild.get_member(int(player_info.get("discord_id")))
        if not user:
            continue
        original_role = discord.utils.get(guild.roles, name=player_info.get("trader_name"))
        await user.remove_roles(original_role)
        player_name_list.append(f"""\'{player_info.get("player_id")}\'""")
    player_name_list = f"({','.join(player_name_list)})"
    dbcon.unfollow_trader(player_name_list)
    logger.info("Cron Job:Clearing Expired User Done")

# Main Program Run here
schedule.every().day.at('00:00').do(lambda: asyncio.create_task(clear_expired()))

async def run_scheduler():
    while True:
        schedule.run_pending()
        await asyncio.sleep(1)

bot.run(config.TOKEN)
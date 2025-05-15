# bot.py
import asyncio
import discord
import message as ms
import schedule
import json
from dto.license_dto import LicenseDTO
from discord.ext import commands
from datetime import datetime, timedelta
from logger import Logger
from modal.activate_modal import ActivateModal
from modal.extend_modal import ExtendModal
from service.role_manager import RoleManager
from service.new_account import create_new_account
from service.resubscribe import resubscribe
from service.cancel_subscribe import cancel_subscribe
from service.gsheet import GSheet
from view.atm_view import AutoTradeManagerView
from view.redeem_vip_view import RedeemVIPView, RedeemVIPViewCH
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
    bot.add_view(RedeemVIPView(dbcon, config.SUPPORT_CHANNEL_ID, config.SUPPORT_CHANNEL_CH_ID))
    await run_vip()
    # await run_atm()
    await run_scheduler()


# License command
@bot.event
async def on_message(message):
    if message.author.id == int(config.ZONIX_ID):  # Ignore messages from the bot itself
        return
    if message.channel.id == int(config.LICENCE_CHANNEL_ID) and message.author.id == int(config.PAYMENT_BOT_ID):
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


@bot.tree.command(name="clearex", description="AutoTrade Manager Command")
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


@bot.tree.command(name="redeemvip", description="Redeem Vip")
async def vip(interaction: discord.Interaction):
    await interaction.response.defer()
    if str(interaction.channel.id) not in config.ON_BOARDING_CHANNEL_ID:
        return True
    player_id = str(interaction.user.id)
    if not dbcon.is_vip_admin(player_id):
        return True
    support_channel_id = config.SUPPORT_CHANNEL_ID
    embed = discord.Embed(
        title=ms.VIP_TITTLE,
        description=ms.VIP_DESCRIPTION.format(config.VIP_ROLE_ID, config.SUPPORT_CHANNEL_ID, config.SUPPORT_CHANNEL_CH_ID),
        color=0xE733FF  # Purple color
    )
    await interaction.followup.send(content="", embed=embed, view=RedeemVIPView(dbcon, support_channel_id))


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


@bot.tree.command(name="givevip", description="Give VIP")
async def give_vip(interaction: discord.Interaction, id:str, day:str):
    await interaction.response.defer(ephemeral=True)
    if str(interaction.channel.id) not in config.ON_BOARDING_CHANNEL_ID:
        return True
    player_id = str(interaction.user.id)
    if not dbcon.is_vip_admin(player_id):
        return True
    vip_detail = dbcon.get_trade_volume_by_id(id)
    if not vip_detail:
        await interaction.followup.send(content="This User have not pair with a UID yet", ephemeral=True)
    else:
        current_date = datetime.now()
        new_exipry_date = (current_date + timedelta(days=int(day))).strftime("%Y-%m-%d")
        dbcon.update_expiry_date_by_discord_id(player_id, new_exipry_date)

        # Give Role
        guild = bot.get_guild(GUILD_ID)
        member = guild.get_member(int(id))
        role = discord.utils.get(interaction.guild.roles, name="VIP")
        await member.add_roles(role)
        await interaction.followup.send(content=f"User {id} have become VIP until {new_exipry_date}", ephemeral=True)


@bot.tree.command(name="adduid", description="Add UID")
async def give_vip(interaction: discord.Interaction, uid: str):
    await interaction.response.defer(ephemeral=True)
    player_id = str(interaction.user.id)
    if not dbcon.is_vip_admin(player_id):
        return True
    uid_detail = dbcon.check_uid_exist_from_trade_volume_table(uid)
    if uid_detail:
        await interaction.followup.send(content="This BingX UID already existed")
    else:
        dbcon.insert_solely_uid(uid)
        await interaction.followup.send(content=f"New UID {uid} added")


@bot.tree.command(name="updatepropw", description="Update PropW table")
async def update_propw(interaction: discord.Interaction):
    await interaction.response.defer(ephemeral=True)
    player_id = str(interaction.user.id)
    if not dbcon.is_vip_admin(player_id):
        return True
    await update_propw_routine()
    await interaction.followup.send(content="PropW table Updated")

@bot.tree.command(name="updatebingx", description="Update BingX table")
async def update_bingx(interaction: discord.Interaction):
    await interaction.response.defer(ephemeral=True)
    player_id = str(interaction.user.id)
    if not dbcon.is_vip_admin(player_id):
        return True
    await update_bingx_routine()
    guild = bot.get_guild(GUILD_ID)
    give_role_service = RoleManager(dbcon, guild, interaction)
    give_role_service.get_bingx_user()
    await give_role_service.give_role("VIP")
    await interaction.followup.send(content="Bingx table Updated")

async def update_propw_routine():
    gsheet_service = GSheet(dbcon, config)
    gsheet_service.store_to_propw_db()

async def update_bingx_routine():
    gsheet_service = GSheet(dbcon, config)
    gsheet_service.store_to_bingx_db()

async def clear_expired():
    logger.info("Cron Job: Autotrade Clearing Start")
    expired_player_list = dbcon.get_expired_user()
    player_name_list = []
    logger.info(f"Cron Job:{len(player_name_list)} user to be cleared")
    if not expired_player_list:
        logger.info("Cron Job: Autotrade Clearing Expired User Done")
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
    logger.info("Cron Job: Autotrade Clearing Expired User Done")

@bot.tree.command(name="clear_vip", description="clear vip")
async def clear_vip_expired(interaction: discord.Interaction, role: str):
    role = role.upper()
    await interaction.response.defer(ephemeral=True)
    await clear_expired_user_by_role(role)
    await interaction.followup.send(content=f"Expired user with role: {role} cleared")

async def clear_expired_user_by_role(role:str):
    logger.info(f"Cron Job: Clearing {role} Start")
    expired_player_list = dbcon.get_expired_vip_user(role)
    logger.info(f"Cron Job: {len(expired_player_list)} user to be cleared")
    if not expired_player_list:
        logger.info(f"Cron Job: Clearing {role} Expired User Done")
        return True
    guild = bot.get_channel(int(config.COMMAND_CHANNEL_ID)).guild
    for player_info in expired_player_list:
        user = guild.get_member(int(player_info.get("discord_id")))
        if not user:
            continue
        target_role = discord.utils.get(guild.roles, name=role)
        if target_role in user.roles:
            try:
                await user.send(f"Your {role} experience is Expired.")
            except Exception as e:
                logger.info(f"Unable to send message to user: {int(player_info.get('discord_id'))}")
            await user.remove_roles(target_role)
    logger.info(f"Cron Job: Clearing Expired {role} User Done")

async def clear_vip_routine():
    await clear_expired_user_by_role("VIP")
    await clear_expired_user_by_role("VIP30")

async def notify_expiring_expired_vips():
    logger.info("Cron Job: Notifying expiry and expiry soon VIPs")

    guild = bot.get_guild(GUILD_ID)

    # Notify users whose VIP has expired today
    # expired_user_ids = dbcon.fetch_vips_by_expiry()

    # for expired_user_id in expired_user_ids:
    #     member = guild.get_member(int(expired_user_id))
    #     if member:
    #         try:
    #             await member.send("Your VIP experience has expired.")
    #             logger.info(f"Sent VIP expired notice to {expired_user_id}")
    #         except Exception as e:
    #             logger.error(f"Failed to send expired message to {expired_user_id}: {e}")

    # Notify users whose VIP is expiring in 7 days
    notification_day = 3
    expiring_user_ids = dbcon.fetch_vips_by_expiry(days=notification_day)

    for expiring_user_id in expiring_user_ids:
        member = guild.get_member(int(expiring_user_id))
        if member:
            try:
                await member.send(f"Your VIP experience will expire in {notification_day} days.")
                logger.info(f"Sent VIP expiration notice to {expiring_user_id}")
            except Exception as e:
                logger.error(f"Failed to send expiration message to {expiring_user_id}: {e}")


# Main Program Run here
# schedule.every().day.at('00:00').do(lambda: asyncio.create_task(clear_expired()))
# schedule.every().day.at('00:00').do(lambda: asyncio.create_task(notify_expiring_expired_vips()))
# schedule.every().day.at('00:00').do(lambda: asyncio.create_task(clear_vip_routine()))
# schedule.every().day.at('00:00').do(lambda: asyncio.create_task(update_propw_routine()))

async def run_vip():
    channel_en = bot.get_channel(int(config.ON_BOARDING_CHANNEL_ID[0]))
    embed = discord.Embed(
        title=ms.VIP_TITTLE,
        description=ms.VIP_DESCRIPTION,
        color=0xE733FF  # Purple color
    )
    view = RedeemVIPView(dbcon, config.SUPPORT_CHANNEL_ID, config.SUPPORT_CHANNEL_CH_ID)
    await channel_en.send(embed=embed, view=view)

    channel_ch = bot.get_channel(int(config.ON_BOARDING_CHANNEL_ID[1]))
    embed = discord.Embed(
        title=ms.VIP_TITTLE_CH,
        description=ms.VIP_DESCRIPTION_CH,
        color=0xE733FF  # Purple color
    )
    view = RedeemVIPViewCH(dbcon, config.SUPPORT_CHANNEL_ID, config.SUPPORT_CHANNEL_CH_ID)
    await channel_ch.send(embed=embed, view=view)


async def run_atm():
    channel_en = bot.get_channel(int(config.COMMAND_CHANNEL_ID))
    embed = discord.Embed(
        title=ms.ATM_TITLE,
        description=ms.ATM_DESCRIPTION.format(config.VIP_ROLE_ID, config.SUPPORT_CHANNEL_ID),
        color=0xE733FF  # Purple color
    )
    view = AutoTradeManagerView(dbcon)
    await channel_en.send(embed=embed, view=view)


# async def run_scheduler():
#     while True:
#         schedule.run_pending()
#         await asyncio.sleep(1)

bot.run(config.TOKEN)
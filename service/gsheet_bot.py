import gspread
import pandas as pd
from google.oauth2.service_account import Credentials
import os
from config import Config
from discord.utils import get
from logger import Logger

config = Config()

# Google Sheet Configurations
CREDENTIALS_FILE = os.getenv('GBOT_GOOGLE_SERVICE_ACCOUNT', 'config/services_account.json')

# System Configurations
GBOT_MINIMUM_VOLUME_THRESHOLD = int(os.getenv('GBOT_MINIMUM_VOLUME_THRESHOLD', 30000))

logger_mod = Logger("GSheet Bot")
logger = logger_mod.get_logger()

# Global variable for expected headers
expected_headers = ['uuid', 'discord_id', 'volume']

free_vip_role = 'FREE_VIP'


def get_worksheet(sheet_id):
    client = init_gspread_client()
    sheet = client.open_by_key(sheet_id)
    return sheet.get_worksheet(0)


def init_gspread_client():
    scope = [
        'https://www.googleapis.com/auth/spreadsheets',
        'https://www.googleapis.com/auth/drive'
    ]
    credentials = Credentials.from_service_account_file(CREDENTIALS_FILE, scopes=scope)
    return gspread.authorize(credentials)


def get_all_user(worksheet):
    records = worksheet.get_all_records(expected_headers=expected_headers, head=2)
    df = pd.DataFrame(records)

    # Ensure all volume values are floats
    df['volume'] = df['volume'].astype(float)

    # Summarize volumes by UUID
    grouped_df = df.groupby('uuid', as_index=False).agg({
        'discord_id': 'first',
        'volume': 'sum'
    })

    grouped_df['status'] = grouped_df['volume'].apply(lambda x: 'pass' if x >= GBOT_MINIMUM_VOLUME_THRESHOLD else 'fail')

    return grouped_df


async def batch_assign_free_vip(dbcon, guild):
    worksheet = get_worksheet(config.GBOT_GSHEET_ID)
    df = get_all_user(worksheet)

    if df.empty:
        logger.info("No data found. Skipping update.")
        return True

    df_pass = df[df['status'] == 'pass']

    if df_pass.empty:
        logger.info("No pass user to be updated.")
        return True

    trade_volumes = dbcon.fetch_all_user_trade_volumes()
    if trade_volumes is None:
        trade_volumes = []

    trade_volumes_dict = {str(record['discord_id']).strip(): record['volume'] for record in trade_volumes}

    update_scripts = []
    insert_scripts = []
    free_vip_discord_ids = []

    for _, row in df_pass.iterrows():
        uuid = row['uuid']
        discord_id = str(row['discord_id']).strip()
        volume = row['volume']
        status = row['status']

        if not pd.notna(uuid) or not pd.notna(discord_id):
            logger.info("Empty UUID or Discord ID found. Skipping entry.")
            continue

        free_vip_discord_ids.append(discord_id)

        # Group all insert/update trade volume table
        if discord_id in trade_volumes_dict:
            update_scripts.append((discord_id, volume))
        else:
            insert_scripts.append((uuid, discord_id, volume))

    execute_updates_and_inserts(dbcon, update_scripts, insert_scripts)
    await assign_free_vip(guild, free_vip_discord_ids)
    return True


async def batch_revoke_free_vip(dbcon, guild):
    worksheet = get_worksheet(config.GBOT_GSHEET_ID)
    df = get_all_user(worksheet)

    if df.empty:
        logger.info("No data found. Skipping update.")
        return True

    df_fail = df[df['status'] == 'fail']

    if df_fail.empty:
        logger.info("No fail user to be updated.")
        return True

    trade_volumes = dbcon.fetch_all_user_trade_volumes()
    if trade_volumes is None:
        trade_volumes = []

    trade_volumes_dict = {str(record['discord_id']).strip(): record['volume'] for record in trade_volumes}

    update_scripts = []
    insert_scripts = []
    revoke_free_vip_discord_ids = []

    for _, row in df_fail.iterrows():
        uuid = row['uuid']
        discord_id = str(row['discord_id']).strip()
        volume = row['volume']
        status = row['status']

        if not pd.notna(uuid) or not pd.notna(discord_id):
            logger.info("Empty UUID or Discord ID found. Skipping entry.")
            continue

        revoke_free_vip_discord_ids.append(discord_id)

        # Group all insert/update trade volume table
        if discord_id in trade_volumes_dict:
            update_scripts.append((discord_id, volume))
        else:
            insert_scripts.append((uuid, discord_id, volume))

    execute_updates_and_inserts(dbcon, update_scripts, insert_scripts)
    await revoke_free_vip_role(guild, revoke_free_vip_discord_ids)
    return True


def execute_updates_and_inserts(dbcon, update_scripts, insert_scripts):
    if update_scripts:
        update_cases_volume = " ".join(
            f"WHEN '{discord_id}' THEN '{volume}'"
            for discord_id, volume in update_scripts
        )
        update_discord_ids = ", ".join(f"'{discord_id}'" for discord_id, _ in update_scripts)

        try:
            dbcon.update_trade_volume_table_by_discord_id(update_cases_volume, update_discord_ids)
            logger.info(f"{len(update_scripts)} records updated at trade_volume_table.")
        except Exception as e:
            logger.error(f"Update failed - {e}")

    if insert_scripts:
        insert_values = ", ".join(
            f"('{uuid}', '{discord_id}', '{volume}')"
            for uuid, discord_id, volume in insert_scripts
        )
        try:
            dbcon.insert_trade_volume_table(insert_values)
            logger.info(f"{len(insert_scripts)} records inserted into trade_volume_table.")
        except Exception as e:
            logger.error(f"Insert failed - {e}")


async def assign_free_vip(guild, free_vip_discord_ids):
    role = fetch_role_by_guild(guild)
    if role is None:
        return

    for discord_id in free_vip_discord_ids:
        member = fetch_member_info_by_guild_and_discord_id(guild, discord_id)

        if role not in member.roles:
            await member.add_roles(role)
            logger.info(f"Assigned role {role} to {member.name}.")


async def revoke_free_vip_role(guild, revoke_free_vip_discord_ids):
    role = fetch_role_by_guild(guild)
    if role is None:
        return

    for discord_id in revoke_free_vip_discord_ids:
        member = fetch_member_info_by_guild_and_discord_id(guild, discord_id)

        if role in member.roles:
            await member.remove_roles(role)
            logger.info(f"Revoke role {free_vip_role} from {member.name}.")


def fetch_role_by_guild(guild):
    role = get(guild.roles, name=free_vip_role)
    if role is None:
        logger.info(f"Role {free_vip_role} not found in server.")
        return None
    return role


def fetch_member_info_by_guild_and_discord_id(guild, discord_id):
    try:
        member = guild.get_member(int(discord_id))
    except ValueError:
        logger.info(f"Invalid Discord ID: {discord_id}")
        return None

    if member is None:
        logger.info(f"Member with Discord ID {discord_id} not found in server.")
        return None

    return member

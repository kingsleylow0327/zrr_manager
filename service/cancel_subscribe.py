import discord
from bingx import BINGX
from dto.license_dto import LicenseDTO
from util.date_dictionary import expriy_date_parse as ed

async def cancel_subscribe(dbcon, dto:LicenseDTO, guild):
    # expiry_date = ed(dto.validity)
    # user_account_list = dbcon.get_all_player_status(dto.userId)
    member = guild.get_member(int(dto.userId))
    license_info = dbcon.get_license_by_license_key(dto.licenseKey)
    account_name = license_info.get("account_used")
    # Close order
    user_api_info = dbcon.get_api_secret_by_account_name(dto.userId, license_info.get("account_used"))
    user_bingx_session = BINGX(user_api_info.get("api_key"), user_api_info.get("api_secret"))
    user_bingx_session.close_all_pos()
    user_bingx_session.close_all_order()
    # Cancel trader
    dbcon.cancel_trader(account_name)
    # Cancel role
    role = discord.utils.get(guild.roles, name=dto.trader)
    await member.remove_roles(role)
    dbcon.register_license(dto, account_name)

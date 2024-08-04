import discord
from dto.license_dto import LicenseDTO
from util.date_dictionary import expriy_date_parse as ed


async def create_new_account(dbcon, dto:LicenseDTO, guild):
    expiry_date = ed(dto.validity)
    user_account_list = dbcon.get_all_player_status(dto.userId)
    member = guild.get_member(int(dto.userId))
    new_name = member.display_name.lower()
    if user_account_list is not None:
        new_name = get_new_name(user_account_list)
    dbcon.activate_user(dto.userId, new_name, expiry_date)
    # Set trader
    dbcon.update_trader_by_trader_name(dto.trader, new_name)
    # Give role
    role = discord.utils.get(guild.roles, name=dto.trader)
    await member.add_roles(role)
    dbcon.register_license(dto, new_name)


def get_new_name(account_list):
        original_name = account_list[0].get("player_id")
        current_num = 2
        for account in account_list:
            account_num = account.get("player_id").split("_")[-1]
            if account_num.isdigit() and int(account_num) >= current_num:
                current_num = int(account_num) + 1
        new_name = f"{original_name}_{str(current_num)}"
        return new_name

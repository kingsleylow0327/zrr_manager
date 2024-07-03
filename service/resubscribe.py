import discord
from dto.license_dto import LicenseDTO
from util.date_dictionary import expriy_date_parse as ed

def resubscribe(dbcon, dto:LicenseDTO, guild):
    expiry_date = ed(dto.validity)
    license_info = dbcon.get_license_by_license_key(dto.licenseKey)
    account_used = license_info.get("account_used")
    dbcon.extend_user(account_used, expiry_date)
    dbcon.register_license(dto, account_used)
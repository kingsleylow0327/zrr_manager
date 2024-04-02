import discord
from discord.interactions import Interaction

TITLE = "Extend User"
class ExtendModal(discord.ui.Modal, title=TITLE):

    def __init__(self, dbcon):
        self.dbcon = dbcon
        super().__init__(title=TITLE, timeout=30)

    player_account_name = discord.ui.TextInput(label="Account Name",placeholder="user account name",style=discord.TextStyle.short)
    expiry_date = discord.ui.TextInput(label="Package",placeholder="2w(Default), 3m, 6m, 1y",style=discord.TextStyle.short, required=False)

    async def on_submit(self, interaction: Interaction):
        user_account_name = str(interaction.data.get("components")[0].get("components")[0].get("value"))
        user_account_name = user_account_name.lower()
        expiry_date = str(interaction.data.get("components")[1].get("components")[0].get("value")).strip()

        if expiry_date.lower() == "3m":
            expiry_date = "3 month"
        elif expiry_date.lower() == "6m":
            expiry_date = "6 month"
        elif expiry_date.lower() == "1y":
            expiry_date = "1 year"
        else:
            expiry_date = "2 week"

        self.dbcon.extend_user(user_account_name, expiry_date)
        await interaction.response.send_message(f"{user_account_name} has extended {expiry_date}!", ephemeral=True)
        return

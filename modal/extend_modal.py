import discord
from discord.interactions import Interaction
from util.date_dictionary import expriy_date_parse as ed

TITLE = "Extend User"
class ExtendModal(discord.ui.Modal, title=TITLE):

    def __init__(self, dbcon):
        self.dbcon = dbcon
        super().__init__(title=TITLE, timeout=30)

    player_account_name = discord.ui.TextInput(label="Account Name",placeholder="user account name",style=discord.TextStyle.short)
    expiry_date = discord.ui.TextInput(label="Package",placeholder="2w(Default), 1m, 3m, 6m",style=discord.TextStyle.short, required=False)

    async def on_submit(self, interaction: Interaction):
        user_account_name = str(interaction.data.get("components")[0].get("components")[0].get("value"))
        user_account_name = user_account_name.lower()
        expiry_date = str(interaction.data.get("components")[1].get("components")[0].get("value")).strip()
        expiry_date = ed(expiry_date.lower())

        self.dbcon.extend_user(user_account_name, expiry_date)
        await interaction.response.send_message(f"{user_account_name} has extended {expiry_date}!", ephemeral=True)
        return

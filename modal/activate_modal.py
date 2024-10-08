import discord
from discord.interactions import Interaction
from util.date_dictionary import expriy_date_parse as ed

TITLE = "Activate User"
class ActivateModal(discord.ui.Modal, title=TITLE):

    def __init__(self, dbcon):
        self.dbcon = dbcon
        super().__init__(title=TITLE, timeout=30)

    player_id = discord.ui.TextInput(label="User Id",placeholder="user id",style=discord.TextStyle.short)
    player_account_name = discord.ui.TextInput(label="Account Name",placeholder="user account name",style=discord.TextStyle.short)
    product_type = discord.ui.TextInput(label="Product Type",placeholder="user product type, atm/strategy",style=discord.TextStyle.short, required=False)
    expiry_date = discord.ui.TextInput(label="Package",placeholder="2w(Default), 1m, 3m, 6m",style=discord.TextStyle.short, required=False)

    async def on_submit(self, interaction: Interaction):
        player_id = str(interaction.data.get("components")[0].get("components")[0].get("value"))
        user_account_name = str(interaction.data.get("components")[1].get("components")[0].get("value"))
        user_account_name = user_account_name.lower()
        product_type = str(interaction.data.get("components")[2].get("components")[0].get("value")).lower()
        expiry_date = str(interaction.data.get("components")[3].get("components")[0].get("value")).strip()
        expiry_date = ed(expiry_date.lower())

        if not self.dbcon.check_user_exist_with_ref(player_id, user_account_name):
            self.dbcon.activate_user(player_id, user_account_name, expiry_date, product_type)
            await interaction.response.send_message(f"User Activated for {expiry_date}", ephemeral=True)
            return
        await interaction.response.send_message(f"User Id {player_id} has been activated before", ephemeral=True)

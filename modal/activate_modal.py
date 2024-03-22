import discord
from discord.interactions import Interaction

TITLE = "Activate User"
class ActivateModal(discord.ui.Modal, title=TITLE):

    def __init__(self, dbcon):
        self.dbcon = dbcon
        super().__init__(title=TITLE, timeout=30)

    player_id = discord.ui.TextInput(label="User Id",placeholder="user id",style=discord.TextStyle.short)
    player_account_name = discord.ui.TextInput(label="Account Name",placeholder="user account name",style=discord.TextStyle.short)
    expiry_date = discord.ui.TextInput(label="Package",placeholder="2w(Default), 3m, 6m, 1y",style=discord.TextStyle.short, required=False)

    async def on_submit(self, interaction: Interaction):
        player_id = str(interaction.data.get("components")[0].get("components")[0].get("value"))
        user_account_name = str(interaction.data.get("components")[1].get("components")[0].get("value"))
        user_account_name = user_account_name.lower()
        expiry_date = str(interaction.data.get("components")[2].get("components")[0].get("value"))

        if expiry_date.lower() == "3m":
            expiry_date = "3 month"
        elif expiry_date.lower() == "6m":
            expiry_date = "6 month"
        elif expiry_date.lower() == "1y":
            expiry_date = "1 year"
        else:
            expiry_date = "2 week"

        if not self.dbcon.check_user_exist_with_ref(player_id, user_account_name):
            self.dbcon.activate_user(player_id, user_account_name, expiry_date)
            await interaction.response.send_message(f"User Activated for {expiry_date}", ephemeral=True)
            return
        await interaction.response.send_message(f"User Id {player_id} has been activated before", ephemeral=True)

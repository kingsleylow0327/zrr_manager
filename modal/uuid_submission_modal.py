import discord
import message as ms
from discord.interactions import Interaction

TITLE = "Submit Your Account Details"


class UUIDSubmissionModal(discord.ui.Modal, title=TITLE):

    def __init__(self, dbcon, selected_account):
        self.dbcon = dbcon
        self.user_account_name = selected_account
        super().__init__(title=TITLE, timeout=120)

    uuid = discord.ui.TextInput(label="Bing X UUID", placeholder="Bing X UUID", style=discord.TextStyle.short)

    async def on_submit(self, interaction: Interaction):
        uuid = self.uuid.value
        discord_id = interaction.user.id
        if self.dbcon.check_discord_id_exist_from_trade_volume_table(discord_id):
            self.dbcon.update_user_from_trade_volume_table(uuid, discord_id)
            await interaction.response.send_message(ms.UUID_UPDATED, ephemeral=True)
        else:
            self.dbcon.insert_user_into_trade_volume_table(uuid, discord_id)
            await interaction.response.send_message(ms.UUID_CREATED, ephemeral=True)

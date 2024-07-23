import discord
import message as ms
from discord.interactions import Interaction

TITLE = "Submit Your UID"


class UUIDSubmissionModal(discord.ui.Modal, title=TITLE):

    def __init__(self, dbcon, support_channel_id):
        self.dbcon = dbcon
        self.support_channel_id = support_channel_id
        super().__init__(title=TITLE, timeout=120)

    uuid = discord.ui.TextInput(label="Bing X UUID", placeholder="Bing X UUID", style=discord.TextStyle.short)

    async def on_submit(self, interaction: Interaction):
        uuid = self.uuid.value
        discord_id = interaction.user.id
        trade_detail = self.dbcon.get_trade_volume_by_id(discord_id)
        if trade_detail == None:
            self.dbcon.insert_user_into_trade_volume_table(uuid, discord_id)
            await interaction.response.send_message(ms.UUID_CREATED, ephemeral=True)
        elif trade_detail.get("uuid") == uuid:
            await interaction.response.send_message(ms.USED_UUID.format(self.support_channel_id), ephemeral=True)
        else:
            self.dbcon.update_user_from_trade_volume_table(uuid, discord_id)
            await interaction.response.send_message(ms.UUID_UPDATED, ephemeral=True)

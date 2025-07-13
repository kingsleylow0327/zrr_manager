import discord
import message as ms
from discord.interactions import Interaction

TITLE = "Edit Your UID"
TITLE_CH = "修改你的 UID"
class UUIDSubmissionModal(discord.ui.Modal, title=TITLE):

    def __init__(self, dbcon, support_channel_id, support_channel_ch_id):
        self.dbcon = dbcon
        self.support_channel_id = support_channel_id
        self.support_channel_ch_id = support_channel_ch_id
        super().__init__(title=TITLE, timeout=120)

    uuid = discord.ui.TextInput(label="Bing X UUID", placeholder="Bing X UUID", style=discord.TextStyle.short)

    async def on_submit(self, interaction: Interaction):
        uuid = self.uuid.value
        discord_id = interaction.user.id

        if not self.dbcon.get_trade_volume_table_by_uuid(uuid):
            await interaction.response.send_message(ms.NO_UUID.format(self.support_channel_id, self.support_channel_ch_id), ephemeral=True)
            return
        else:
            self.dbcon.update_user_from_trade_volume_table(uuid, discord_id)
            await interaction.response.send_message(ms.UUID_UPDATED, ephemeral=True)

class UUIDSubmissionModalCH(discord.ui.Modal, title=TITLE_CH):

    def __init__(self, dbcon, support_channel_id, support_channel_ch_id):
        self.dbcon = dbcon
        self.support_channel_id = support_channel_id
        self.support_channel_ch_id = support_channel_ch_id
        super().__init__(title=TITLE, timeout=120)

    uuid = discord.ui.TextInput(label="BingX 主账户 UID", placeholder="BingX 主账户 UID", style=discord.TextStyle.short)

    async def on_submit(self, interaction: Interaction):
        uuid = self.uuid.value
        discord_id = interaction.user.id

        if not self.dbcon.get_trade_volume_table_by_uuid(uuid):
            await interaction.response.send_message(ms.NO_UUID_CH.format(self.support_channel_id, self.support_channel_ch_id), ephemeral=True)
            return
        else:
            self.dbcon.update_user_from_trade_volume_table(uuid, discord_id)
            await interaction.response.send_message(ms.UUID_UPDATED_CH, ephemeral=True)
import discord
import message as ms
from datetime import date, timedelta
from discord.interactions import Interaction

TITLE = "Get 30 Days VIP Access"
TITLE_CH = "领取 30 天免费VIP体验"
class PropWVIPRedeemtionModal(discord.ui.Modal, title=TITLE):

    def __init__(self, dbcon, support_channel_id, support_channel_ch_id):
        self.dbcon = dbcon
        self.support_channel_id = support_channel_id
        self.support_channel_ch_id = support_channel_ch_id
        super().__init__(title=TITLE, timeout=120)

    uuid = discord.ui.TextInput(label="PropW Account UID", placeholder="PropW Account UID", style=discord.TextStyle.short)

    async def on_submit(self, interaction: Interaction):
        uuid = self.uuid.value
        discord_id = interaction.user.id
        if not self.dbcon.check_uuid_exist_from_propw_table(uuid):
            await interaction.response.send_message(ms.NO_UUID.format(self.support_channel_id, self.support_channel_ch_id), ephemeral=True)
        else:
            today = (date.today() + timedelta(days=30)).strftime("%Y-%m-%d")
            self.dbcon.update_user_from_propw_table_with_date(uuid, discord_id, today)

            # Give Role
            user = interaction.user
            role = discord.utils.get(interaction.guild.roles, name="VIP30")
            await user.add_roles(role)
            await interaction.response.send_message(ms.PROPW_SUCCESS, ephemeral=True)


class PropWVIPRedeemtionModalCH(discord.ui.Modal, title=TITLE_CH):

    def __init__(self, dbcon, support_channel_id, support_channel_ch_id):
        self.dbcon = dbcon
        self.support_channel_id = support_channel_id
        self.support_channel_ch_id = support_channel_ch_id
        super().__init__(title=TITLE, timeout=120)

    uuid = discord.ui.TextInput(label="PropW 账户 UID", placeholder="PropW 账户 UID", style=discord.TextStyle.short)

    async def on_submit(self, interaction: Interaction):
        uuid = self.uuid.value
        discord_id = interaction.user.id
        if not self.dbcon.check_uuid_exist_from_propw_table(uuid):
            await interaction.response.send_message(ms.NO_UUID_CH.format(self.support_channel_id, self.support_channel_ch_id), ephemeral=True)
        else:
            today = (date.today() + timedelta(days=30)).strftime("%Y-%m-%d")
            self.dbcon.update_user_from_propw_table_with_date(uuid, discord_id, today)

            # Give Role
            user = interaction.user
            role = discord.utils.get(interaction.guild.roles, name="VIP30")
            await user.add_roles(role)
            await interaction.response.send_message(ms.PROPW_SUCCESS_CH, ephemeral=True)

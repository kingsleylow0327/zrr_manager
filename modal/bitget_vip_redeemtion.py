import discord
import message as ms
from datetime import date, timedelta
from discord.interactions import Interaction

TITLE = "Get 30 Days VIP Access"
TITLE_CH = "领取 30 天免费VIP体验"
class BitGetVIPRedeemtionModal(discord.ui.Modal, title=TITLE):

    def __init__(self, dbcon, support_channel_id, support_channel_ch_id):
        self.dbcon = dbcon
        self.support_channel_id = support_channel_id
        self.support_channel_ch_id = support_channel_ch_id
        self.table_name = dbcon.config.BITGET_TABLE
        self.no_uuid_message = ms.NO_UUID.format(self.support_channel_id, self.support_channel_ch_id)
        self.role_name = "VIPB"
        super().__init__(title=TITLE, timeout=120)

    uuid = discord.ui.TextInput(label="BitGet Account UID", placeholder="BitGet Account UID", style=discord.TextStyle.short)

    async def on_submit(self, interaction: Interaction):
        await interaction.response.defer(ephemeral=True)
        await vip_redeem(interaction, self.uuid.value, self.dbcon, self.no_uuid_message, self.table_name, self.role_name)

class BitGetVIPRedeemtionModalCH(discord.ui.Modal, title=TITLE_CH):

    def __init__(self, dbcon, support_channel_id, support_channel_ch_id):
        self.dbcon = dbcon
        self.support_channel_id = support_channel_id
        self.support_channel_ch_id = support_channel_ch_id
        self.table_name = dbcon.config.BITGET_TABLE
        self.no_uuid_message = ms.NO_UUID_CH.format(self.support_channel_id, self.support_channel_ch_id)
        self.role_name = "VIPB"
        super().__init__(title=TITLE, timeout=120)

    uuid = discord.ui.TextInput(label="BitGet 账户 UID", placeholder="BitGet 账户 UID", style=discord.TextStyle.short)

    async def on_submit(self, interaction: Interaction):
        await interaction.response.defer(ephemeral=True)
        await vip_redeem(interaction, self.uuid.value, self.dbcon, self.no_uuid_message, self.table_name, self.role_name)


async def vip_redeem(interaction, uuid, dbcon, no_uuid_message, table_name, role_name):
    discord_id = interaction.user.id
    user_info = dbcon.get_bitget_table_by_uuid(uuid)

    if user_info == None:
        await interaction.followup.send(no_uuid_message, ephemeral=True)

    else:
        expiry_date = (date.today() + timedelta(days=30)).strftime("%Y-%m-%d")
        dbcon.update_user_from_vip_tables_with_date(table_name, uuid, discord_id, expiry_date)
        # Give Role
        user = interaction.user
        role = discord.utils.get(interaction.guild.roles, name=role_name)
        await user.add_roles(role)
        await interaction.followup.send(ms.VIP_SUCCESS, ephemeral=True)

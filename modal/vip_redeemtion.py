import discord
import message as ms
from datetime import date, timedelta
from discord.interactions import Interaction

TITLE = "Redeem Your VIP!"
class VIPRedeemtionModal(discord.ui.Modal, title=TITLE):

    def __init__(self, dbcon, support_channel_id):
        self.dbcon = dbcon
        self.support_channel_id = support_channel_id
        super().__init__(title=TITLE, timeout=120)

    uuid = discord.ui.TextInput(label="Bing X UUID", placeholder="Bing X UUID", style=discord.TextStyle.short)

    async def on_submit(self, interaction: Interaction):
        uuid = self.uuid.value
        discord_id = interaction.user.id
        if self.dbcon.check_uuid_exist_from_trade_volume_table(uuid):
            await interaction.response.send_message(ms.USED_UUID.format(self.support_channel_id), ephemeral=True)
        else:
            today = (date.today() + timedelta(days=7)).strftime("%Y-%m-%d")
            self.dbcon.insert_user_into_trade_volume_table(uuid, discord_id, today)

            # Give Role
            user = interaction.user
            role = discord.utils.get(interaction.guild.roles, name="FREE_VIP")
            await user.add_roles(role)
            await interaction.response.send_message(ms.VIP_SUCCESS, ephemeral=True)

import discord
import message as ms
from datetime import date, timedelta
from modal.uuid_submission_modal import UUIDSubmissionModal


class RedeemVIPView(discord.ui.View):

    def __init__(self, dbcon, support_channel_id):
        super().__init__(timeout=180)
        self.dbcon = dbcon
        self.support_channel_id = support_channel_id

    @discord.ui.button(label="UID Submission", style=discord.ButtonStyle.blurple)
    async def uuidSubmissionButton(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(UUIDSubmissionModal(self.dbcon, self.support_channel_id))

    @discord.ui.button(label="Redeem VIP", style=discord.ButtonStyle.green)
    async def damageButton(self, interaction: discord.Interaction, button: discord.ui.Button):
        discord_id = interaction.user.id
        trade_detail = self.dbcon.get_trade_volume_by_id(discord_id)
        # No UUID
        if not trade_detail:
            await interaction.response.send_message(ms.NO_UUID.format(self.support_channel_id), ephemeral=True)
            return
        
        # Expired
        if trade_detail.get("vip_expired_date") and trade_detail.get("vip_expired_date") < date.today():
            await interaction.response.send_message(ms.EXPIRED_VIP.format(self.support_channel_id), ephemeral=True)
            return

        # Already registered
        if trade_detail.get("vip_expired_date") != None:
            await interaction.response.send_message(ms.REDEEMED_VIP.format(self.support_channel_id), ephemeral=True)
            return
        
        today = (date.today() + timedelta(days=7)).strftime("%Y-%m-%d")
        self.dbcon.update_exipry_date_from_trade_volume_table(discord_id, today)
        # Give Role
        user = interaction.user
        role = discord.utils.get(interaction.guild.roles, name="FREE_VIP")
        await user.add_roles(role)
        await interaction.response.send_message(ms.VIP_SUCCESS, ephemeral=True)
    
    @discord.ui.button(label="Done!", style=discord.ButtonStyle.gray)
    async def reportA(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.edit_message(content="", view=None, delete_after=1)
    
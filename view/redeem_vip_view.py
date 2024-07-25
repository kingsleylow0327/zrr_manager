import discord
import message as ms
from datetime import date
from modal.vip_redeemtion import VIPRedeemtionModal
from modal.uuid_submission_modal import UUIDSubmissionModal


class RedeemVIPView(discord.ui.View):

    def __init__(self, dbcon, support_channel_id):
        super().__init__(timeout=None)
        self.dbcon = dbcon
        self.support_channel_id = support_channel_id

    @discord.ui.button(label="Redeem VIP", style=discord.ButtonStyle.blurple, custom_id="redeem_button")
    async def RedeemButton(self, interaction: discord.Interaction, button: discord.ui.Button):
        discord_id = interaction.user.id
        trade_detail = self.dbcon.get_trade_volume_by_id(discord_id)
        
        # Expired
        if trade_detail and trade_detail.get("vip_expired_date") and trade_detail.get("vip_expired_date") < date.today():
            await interaction.response.send_message(ms.EXPIRED_VIP.format(self.support_channel_id), ephemeral=True)
            return

        # Already registered
        if trade_detail and trade_detail.get("vip_expired_date") != None:
            await interaction.response.send_message(ms.REDEEMED_VIP.format(self.support_channel_id), ephemeral=True)
            return
        
        await interaction.response.send_modal(VIPRedeemtionModal(self.dbcon, self.support_channel_id))
    
    @discord.ui.button(label="Edit UID", style=discord.ButtonStyle.green, custom_id="edit_uid_button")
    async def uuidSubmissionButton(self, interaction: discord.Interaction, button: discord.ui.Button):
        discord_id = interaction.user.id
        trade_detail = self.dbcon.get_trade_volume_by_id(discord_id)
        if not trade_detail:
            await interaction.response.send_message(ms.NO_UUID.format(self.support_channel_id), ephemeral=True)
            return
        await interaction.response.send_modal(UUIDSubmissionModal(self.dbcon, self.support_channel_id))
    
    # @discord.ui.button(label="Check Volume", style=discord.ButtonStyle.red, custom_id="volume_button")
    # async def check_volume(self, interaction: discord.Interaction, button: discord.ui.Button):
    #     player_id = str(interaction.user.id)
    #     volume_detail = self.dbcon.fetch_user_trade_volume_by_discord_id(player_id)
    #     final_volume = volume_detail.get('volume') if volume_detail and volume_detail.get('volume') else "--"
    #     embeded_volume = discord.Embed(title=f"Your Open Trade Volume for this Month: {final_volume} USDT \n")
    #     await interaction.response.send_message(embed=embeded_volume, ephemeral=True)

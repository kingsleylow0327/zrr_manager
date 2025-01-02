import discord
import message as ms
from datetime import date
from modal.vip_redeemtion import VIPRedeemtionModal, VIPRedeemtionModalCH
from modal.propw_vip_redeemtion import PropWVIPRedeemtionModal, PropWVIPRedeemtionModalCH
from modal.uuid_submission_modal import UUIDSubmissionModal, UUIDSubmissionModalCH


class RedeemVIPView(discord.ui.View):

    def __init__(self, dbcon, support_channel_id, support_channel_ch_id):
        super().__init__(timeout=None)
        self.dbcon = dbcon
        self.support_channel_id = support_channel_id
        self.support_channel_ch_id = support_channel_ch_id

    @discord.ui.button(label="Get My 7 Days VIP Access", style=discord.ButtonStyle.blurple, custom_id="redeem_button")
    async def RedeemButton(self, interaction: discord.Interaction, button: discord.ui.Button):
        discord_id = interaction.user.id
        trade_detail = self.dbcon.get_trade_volume_by_id(discord_id)
        
        # Expired
        if trade_detail and trade_detail.get("vip_expired_date") and trade_detail.get("vip_expired_date") < date.today():
            await interaction.response.send_message(ms.EXPIRED_VIP.format(self.support_channel_id, self.support_channel_ch_id), ephemeral=True)
            return

        # Already registered
        if trade_detail and trade_detail.get("vip_expired_date") != None:
            await interaction.response.send_message(ms.REDEEMED_VIP.format(self.support_channel_id, self.support_channel_ch_id), ephemeral=True)
            return
        
        await interaction.response.send_modal(VIPRedeemtionModal(self.dbcon, self.support_channel_id, self.support_channel_ch_id))
    
    @discord.ui.button(label="Edit UID", style=discord.ButtonStyle.green, custom_id="edit_uid_button")
    async def uuidSubmissionButton(self, interaction: discord.Interaction, button: discord.ui.Button):
        discord_id = interaction.user.id
        trade_detail = self.dbcon.get_trade_volume_by_id(discord_id)
        if not trade_detail:
            await interaction.response.send_message(ms.NO_UUID.format(self.support_channel_id, self.support_channel_ch_id), ephemeral=True)
            return
        await interaction.response.send_modal(UUIDSubmissionModal(self.dbcon, self.support_channel_id, self.support_channel_ch_id))
    
    # @discord.ui.button(label="PropW 30 Days Free VIP", style=discord.ButtonStyle.blurple, custom_id="propw_button")
    # async def propWRedeemButton(self, interaction: discord.Interaction, button: discord.ui.Button):
    #     discord_id = interaction.user.id
    #     trade_detail = self.dbcon.get_propw_by_id(discord_id)
        
    #     # Expired
    #     if trade_detail and trade_detail.get("expired_date") and trade_detail.get("expired_date") < date.today():
    #         await interaction.response.send_message(ms.PROPW_EXPIRED_VIP.format(self.support_channel_id, self.support_channel_ch_id), ephemeral=True)
    #         return

    #     # Already registered
    #     if trade_detail and trade_detail.get("expired_date") != None:
    #         await interaction.response.send_message(ms.PROPW_REDEEMED_VIP.format(self.support_channel_id, self.support_channel_ch_id), ephemeral=True)
    #         return
        
    #     await interaction.response.send_modal(PropWVIPRedeemtionModal(self.dbcon, self.support_channel_id, self.support_channel_ch_id))
  
    # @discord.ui.button(label="Check Volume", style=discord.ButtonStyle.red, custom_id="volume_button")
    # async def check_volume(self, interaction: discord.Interaction, button: discord.ui.Button):
    #     player_id = str(interaction.user.id)
    #     volume_detail = self.dbcon.fetch_user_trade_volume_by_discord_id(player_id)
    #     final_volume = volume_detail.get('volume') if volume_detail and volume_detail.get('volume') else "--"
    #     embeded_volume = discord.Embed(title=f"Your Open Trade Volume for this Month: {final_volume} USDT \n")
    #     await interaction.response.send_message(embed=embeded_volume, ephemeral=True)

class RedeemVIPViewCH(discord.ui.View):

    def __init__(self, dbcon, support_channel_id, support_channel_ch_id):
        super().__init__(timeout=None)
        self.dbcon = dbcon
        self.support_channel_id = support_channel_id
        self.support_channel_ch_id = support_channel_ch_id

    @discord.ui.button(label="领取 7 天免费VIP体验", style=discord.ButtonStyle.blurple, custom_id="redeem_button")
    async def RedeemButton(self, interaction: discord.Interaction, button: discord.ui.Button):
        discord_id = interaction.user.id
        trade_detail = self.dbcon.get_trade_volume_by_id(discord_id)
        
        # Expired
        if trade_detail and trade_detail.get("vip_expired_date") and trade_detail.get("vip_expired_date") < date.today():
            await interaction.response.send_message(ms.EXPIRED_VIP_CH.format(self.support_channel_id, self.support_channel_ch_id), ephemeral=True)
            return

        # Already registered
        if trade_detail and trade_detail.get("vip_expired_date") != None:
            await interaction.response.send_message(ms.REDEEMED_VIP_CH.format(self.support_channel_id, self.support_channel_ch_id), ephemeral=True)
            return
        
        await interaction.response.send_modal(VIPRedeemtionModalCH(self.dbcon, self.support_channel_id, self.support_channel_ch_id))
    
    @discord.ui.button(label="更改UID", style=discord.ButtonStyle.green, custom_id="edit_uid_button")
    async def uuidSubmissionButton(self, interaction: discord.Interaction, button: discord.ui.Button):
        discord_id = interaction.user.id
        trade_detail = self.dbcon.get_trade_volume_by_id(discord_id)
        if not trade_detail:
            await interaction.response.send_message(ms.NO_UUID_CH.format(self.support_channel_id, self.support_channel_ch_id), ephemeral=True)
            return
        await interaction.response.send_modal(UUIDSubmissionModalCH(self.dbcon, self.support_channel_id, self.support_channel_ch_id))
    
    # @discord.ui.button(label="PropW 30 天免费VIP体验", style=discord.ButtonStyle.blurple, custom_id="propw_button") 
    # async def propWRedeemButton(self, interaction: discord.Interaction, button: discord.ui.Button):
    #     discord_id = interaction.user.id
    #     trade_detail = self.dbcon.get_propw_by_id(discord_id)
        
    #     # Expired
    #     if trade_detail and trade_detail.get("expired_date") and trade_detail.get("expired_date") < date.today():
    #         await interaction.response.send_message(ms.PROPW_EXPIRED_VIP_CH.format(self.support_channel_id, self.support_channel_ch_id), ephemeral=True)
    #         return

    #     # Already registered
    #     if trade_detail and trade_detail.get("expired_date") != None:
    #         await interaction.response.send_message(ms.PROPW_REDEEMED_VIP_CH.format(self.support_channel_id, self.support_channel_ch_id), ephemeral=True)
    #         return
        
    #     await interaction.response.send_modal(PropWVIPRedeemtionModalCH(self.dbcon, self.support_channel_id, self.support_channel_ch_id))
  
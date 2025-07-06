import discord
import message as ms
from datetime import date
from modal.vip_redeemtion import VIPRedeemtionModal, VIPRedeemtionModalCH
from modal.uuid_submission_modal import UUIDSubmissionModal, UUIDSubmissionModalCH
from modal.bitget_vip_redeemtion import BitGetVIPRedeemtionModal, BitGetVIPRedeemtionModalCH
from modal.pionex_vip_redeemtion import PionexVIPRedeemtionModal, PionexVIPRedeemtionModalCH


class RedeemVIPView(discord.ui.View):

    def __init__(self, dbcon, support_channel_id, support_channel_ch_id):
        super().__init__(timeout=None)
        self.dbcon = dbcon
        self.support_channel_id = support_channel_id
        self.support_channel_ch_id = support_channel_ch_id

    @discord.ui.button(label="Claim VIP via BingX UID", style=discord.ButtonStyle.blurple, custom_id="redeem_button")
    async def RedeemButton(self, interaction: discord.Interaction, button: discord.ui.Button):
        discord_id = interaction.user.id
        trade_detail = self.dbcon.get_trade_volume_by_id(discord_id)
        
        # Expired
        if trade_detail and trade_detail.get("expired_date") and trade_detail.get("expired_date") < date.today():
            await interaction.response.send_message(ms.EXPIRED_VIP.format(self.support_channel_id, self.support_channel_ch_id), ephemeral=True)
            return

        # Already registered
        if trade_detail and trade_detail.get("expired_date") != None:
            await interaction.response.send_message(ms.REDEEMED_VIP.format(self.support_channel_id, self.support_channel_ch_id), ephemeral=True)
            return
        
        await interaction.response.send_modal(VIPRedeemtionModal(self.dbcon, self.support_channel_id, self.support_channel_ch_id))
    
    # @discord.ui.button(label="Edit UID", style=discord.ButtonStyle.green, custom_id="edit_uid_button")
    # async def uuidSubmissionButton(self, interaction: discord.Interaction, button: discord.ui.Button):
    #     discord_id = interaction.user.id
    #     trade_detail = self.dbcon.get_trade_volume_by_id(discord_id)
    #     if not trade_detail:
    #         await interaction.response.send_message(ms.NO_UUID.format(self.support_channel_id, self.support_channel_ch_id), ephemeral=True)
    #         return
    #     await interaction.response.send_modal(UUIDSubmissionModal(self.dbcon, self.support_channel_id, self.support_channel_ch_id))
    
    @discord.ui.button(label="Claim VIP via Bitget UID", style=discord.ButtonStyle.blurple, custom_id="bitget_button")
    async def bitgetRedeemButton(self, interaction: discord.Interaction, button: discord.ui.Button):
        discord_id = interaction.user.id
        trade_detail = self.dbcon.get_bitget_by_id(discord_id)
        
        # Expired
        if trade_detail and trade_detail.get("expired_date") and trade_detail.get("expired_date") < date.today():
            await interaction.response.send_message(ms.PROPW_EXPIRED_VIP.format(self.support_channel_id, self.support_channel_ch_id), ephemeral=True)
            return

        # Already registered
        if trade_detail and trade_detail.get("expired_date") != None:
            await interaction.response.send_message(ms.PROPW_REDEEMED_VIP.format(self.support_channel_id, self.support_channel_ch_id), ephemeral=True)
            return
        
        await interaction.response.send_modal(BitGetVIPRedeemtionModal(self.dbcon, self.support_channel_id, self.support_channel_ch_id))


class RedeemVIPViewCH(discord.ui.View):

    def __init__(self, dbcon, support_channel_id, support_channel_ch_id):
        super().__init__(timeout=None)
        self.dbcon = dbcon
        self.support_channel_id = support_channel_id
        self.support_channel_ch_id = support_channel_ch_id

    @discord.ui.button(label="通过BingX领取VIP体验", style=discord.ButtonStyle.blurple, custom_id="redeem_button")
    async def RedeemButton(self, interaction: discord.Interaction, button: discord.ui.Button):
        discord_id = interaction.user.id
        trade_detail = self.dbcon.get_trade_volume_by_id(discord_id)
        
        # Expired
        if trade_detail and trade_detail.get("expired_date") and trade_detail.get("expired_date") < date.today():
            await interaction.response.send_message(ms.EXPIRED_VIP_CH.format(self.support_channel_id, self.support_channel_ch_id), ephemeral=True)
            return

        # Already registered
        if trade_detail and trade_detail.get("expired_date") != None:
            await interaction.response.send_message(ms.REDEEMED_VIP_CH.format(self.support_channel_id, self.support_channel_ch_id), ephemeral=True)
            return
        
        await interaction.response.send_modal(VIPRedeemtionModalCH(self.dbcon, self.support_channel_id, self.support_channel_ch_id))
    
    # @discord.ui.button(label="更改UID", style=discord.ButtonStyle.green, custom_id="edit_uid_button")
    # async def uuidSubmissionButton(self, interaction: discord.Interaction, button: discord.ui.Button):
    #     discord_id = interaction.user.id
    #     trade_detail = self.dbcon.get_trade_volume_by_id(discord_id)
    #     if not trade_detail:
    #         await interaction.response.send_message(ms.NO_UUID_CH.format(self.support_channel_id, self.support_channel_ch_id), ephemeral=True)
    #         return
    #     await interaction.response.send_modal(UUIDSubmissionModalCH(self.dbcon, self.support_channel_id, self.support_channel_ch_id))
    
    @discord.ui.button(label="通过Bitget领取VIP体验", style=discord.ButtonStyle.blurple, custom_id="bitget_button") 
    async def bitgetRedeemButton(self, interaction: discord.Interaction, button: discord.ui.Button):
        discord_id = interaction.user.id
        trade_detail = self.dbcon.get_bitget_by_id(discord_id)
        
        # Expired
        if trade_detail and trade_detail.get("expired_date") and trade_detail.get("expired_date") < date.today():
            await interaction.response.send_message(ms.PROPW_EXPIRED_VIP_CH.format(self.support_channel_id, self.support_channel_ch_id), ephemeral=True)
            return

        # Already registered
        if trade_detail and trade_detail.get("expired_date") != None:
            await interaction.response.send_message(ms.PROPW_REDEEMED_VIP_CH.format(self.support_channel_id, self.support_channel_ch_id), ephemeral=True)
            return
        
        await interaction.response.send_modal(BitGetVIPRedeemtionModalCH(self.dbcon, self.support_channel_id, self.support_channel_ch_id))

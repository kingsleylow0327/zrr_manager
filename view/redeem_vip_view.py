import discord
import message as ms
from datetime import date
from modal.vip_redeemtion import VIPRedeemtionModal, VIPRedeemtionModalCH
from modal.bitget_vip_redeemtion import BitGetVIPRedeemtionModal, BitGetVIPRedeemtionModalCH


class RedeemVIPView(discord.ui.View):

    def __init__(self, dbcon, support_channel_id, support_channel_ch_id):
        super().__init__(timeout=None)
        self.dbcon = dbcon
        self.support_channel_id = support_channel_id
        self.support_channel_ch_id = support_channel_ch_id

        button = discord.ui.Button(
            label="Unity Fund Challenge",
            url="https://ufc.unitycrypto.com/landing?=potato&referral=B270FF",
            style=discord.ButtonStyle.success
        )
        self.add_item(button)


class RedeemVIPViewCH(discord.ui.View):

    def __init__(self, dbcon, support_channel_id, support_channel_ch_id):
        super().__init__(timeout=None)
        self.dbcon = dbcon
        self.support_channel_id = support_channel_id
        self.support_channel_ch_id = support_channel_ch_id

        button = discord.ui.Button(
            label="Unity Fund Challenge",
            url="https://ufc.unitycrypto.com/landing?=potato&referral=B270FF",
            style=discord.ButtonStyle.link
        )
        self.add_item(button)

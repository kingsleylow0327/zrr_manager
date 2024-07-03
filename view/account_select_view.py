import discord
import message as ms
from bingx import BINGX
from datetime import datetime
from discord.interactions import Interaction
from modal.api_modal import APIModal
from view.trader_view import TraderSelectView
from view.damage_view import DamageSelectView
from view.license_select_view import LicenseSelectView

class AccountSelectView(discord.ui.View):
    def __init__(self, dbcon, user_account_list, stage, license_list=None):
        super().__init__()
        self.add_item(UserDropDown(dbcon, user_account_list, stage, license_list))

class UserDropDown(discord.ui.Select):
    def __init__(self, dbcon, user_account_list, stage, license_list=None):
        self.dbcon = dbcon
        self.stage = stage
        self.player_dict = {}
        self.license_list = license_list

        account_options = []
        for account in user_account_list:
            account_options.append(discord.SelectOption(label=f"{account.get('player_id')}",
                                                        value=f"{account.get('player_id')}"))
            self.player_dict[account.get('player_id')] = {"discord_id": account.get('trader_discord_id'),
                                                          "expiry_date": account.get('expiry_date'),
                                                          "bingx": BINGX(account.get("api_key"), account.get("api_secret"))}

        super().__init__(placeholder="Please select an User Account", options=account_options, min_values=1, max_values=1)

    async def callback(self, interaction: Interaction):
        selected_account = self.values[0]
        following_trader_id = self.player_dict.get(selected_account).get("discord_id")
        player = self.player_dict.get(selected_account).get("bingx")
        expiry_date = self.player_dict.get(selected_account).get("expiry_date")
        if expiry_date != None and expiry_date < datetime.today().date() and self.stage != "extend":
            await interaction.response.edit_message(content=ms.EXPIRED_ACCOUNT,
                                                    embed=None,
                                                    view=None)
            return

        if self.stage == "trader":
            await interaction.response.edit_message(content=ms.SELECTED_ACCOUNT.format(selected_account),
                                                    embed=None,
                                                    view=TraderSelectView(self.dbcon,
                                                                          selected_account,
                                                                          player,
                                                                          following_trader_id))
        elif self.stage == "damage":
            await interaction.response.edit_message(content=ms.SELECTED_ACCOUNT.format(selected_account),
                                                    embed=None,
                                                    view=DamageSelectView(self.dbcon,
                                                                          selected_account))
        elif self.stage == "api":
            await interaction.response.send_modal(APIModal(self.dbcon, selected_account))
        
        elif self.stage == "extend":
            if self.license_list == None:
                await interaction.response.edit_message(content=ms.NO_LICENSE, embed=None, view=None)
                return
            await interaction.response.edit_message(content=ms.SELECTED_ACCOUNT.format(selected_account),
                                                    embed=None,
                                                    view=LicenseSelectView(self.dbcon,
                                                                          selected_account,
                                                                          self.license_list))
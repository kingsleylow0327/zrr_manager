import discord
from discord.interactions import Interaction
from util.date_dictionary import expriy_date_parse as ed

class LicenseSelectView(discord.ui.View):
    def __init__(self, dbcon, selected_account, license_list, account_list=None, is_new_account=False):
        super().__init__()
        self.add_item(LicensDropDown(dbcon, selected_account, license_list, account_list))

class LicensDropDown(discord.ui.Select):
    def __init__(self, dbcon, selected_account, license_list, account_list):
        self.dbcon = dbcon
        self.selected_account = selected_account
        # self.is_new_account = is_new_account
        self.discord_id = None
        self.account_list = None
        if account_list:
            self.account_list = [a.get("player_id") for a in account_list]
            self.account_list.sort()
            new_name = self.get_new_name(self.account_list)
        license_options = []
        for license in license_list:
            license_options.append(discord.SelectOption(label=f"{license.get('trader_name')}, {license.get('validity')}",
                                                        value=f"{license.get('license_key')},{license.get('validity')},{license.get('trader_name')}"))

        super().__init__(placeholder="Please select a License Key", options=license_options, min_values=1, max_values=1)

    async def callback(self, interaction: Interaction):
        license_info = self.values[0].split(",")
        license = license_info[0]
        validity = license_info[1].lower()
        trader_name = license_info[2]
        discord_id = interaction.user.id
        expiry_date = ed(validity)
        
        #self.dbcon.use_license(license)
        # if not self.is_new_account:
        self.dbcon.extend_user(self.selected_account, expiry_date)
        await interaction.response.edit_message(content=f"{self.selected_account} have extended {expiry_date} successfully", view=None)
        # else:
        #     if new_name == "empty":
        #         new_name = interaction.user.name.replace(" ", "_").lower()
        #     self.dbcon.activate_user(discord_id, new_name, expiry_date)
        #     await interaction.response.edit_message(content=f"New Account: *{new_name}* have created with {expiry_date} long!", embed=None, view=None)
        self.dbcon.use_license(license)
    
    def get_new_name(self, account_list):
        original_name = account_list[0]
        current_num = 2
        for account in account_list:
            account_num = account.split("_")[-1]
            if account_num.isdigit() and int(account_num) >= current_num:
                current_num = int(account_num) + 1
        new_name = f"{original_name}_{str(current_num)}"
        return new_name

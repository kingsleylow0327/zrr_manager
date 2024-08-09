import discord
from view.account_select_view import AccountSelectView


class MasterView(discord.ui.View):

    def __init__(self, dbcon, user_account_list, license_list=None):
        super().__init__(timeout=180)
        self.dbcon = dbcon
        self.user_account_list = user_account_list
        self.license_list = license_list

    # @discord.ui.button(label="Select Trader", style=discord.ButtonStyle.blurple)
    # async def traderButton(self, interaction: discord.Interaction, button: discord.ui.Button):
    #     await interaction.response.edit_message(content=f"Account Selection",
    #                                             view=AccountSelectView(self.dbcon,
    #                                                                    self.user_account_list,
    #                                                                    "trader"))

    # @discord.ui.button(label="UUID Submission", style=discord.ButtonStyle.blurple)
    # async def uuidSubmissionButton(self, interaction: discord.Interaction, button: discord.ui.Button):
    #     await interaction.response.send_modal(UUIDSubmissionModal(self.dbcon, "createAccount"))

    @discord.ui.button(label="Set Damage", style=discord.ButtonStyle.green)
    async def damage_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.edit_message(content=f"Account Selection",
                                                view=AccountSelectView(self.dbcon,
                                                                       self.user_account_list,
                                                                       "damage"))

    @discord.ui.button(label="Set/Reset API", style=discord.ButtonStyle.red)
    async def api_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.edit_message(content=f"Account Selection",
                                                view=AccountSelectView(self.dbcon,
                                                                       self.user_account_list,
                                                                       "api"))
    
    # @discord.ui.button(label="New Account", style=discord.ButtonStyle.red)
    # async def activateButton(self, interaction: discord.Interaction, button: discord.ui.Button):
    #     if self.license_list == None:
    #         await interaction.response.edit_message(content=ms.NO_LICENSE, embed=None, view=None)
    #         return
    #     await interaction.response.edit_message(content=f"License Selection",
    #                                             view=LicenseSelectView(self.dbcon,
    #                                                                    None,
    #                                                                    self.license_list,
    #                                                                    self.user_account_list,
    #                                                                    is_new_account=True))
    
    # @discord.ui.button(label="Extend Validity", style=discord.ButtonStyle.red)
    # async def extendButton(self, interaction: discord.Interaction, button: discord.ui.Button):
    #     if self.license_list == None:
    #         await interaction.response.edit_message(content=ms.NO_LICENSE, embed=None, view=None)
    #         return
    #     await interaction.response.edit_message(content=f"Account Selection",
    #                                             view=AccountSelectView(self.dbcon,
    #                                                                    self.user_account_list,
    #                                                                    "extend",
    #                                                                    self.license_list))

    @discord.ui.button(label="Done!", style=discord.ButtonStyle.gray)
    async def done_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.edit_message(content="", view=None, delete_after=1)
    
import discord
from view.account_select_view import AccountSelectView

class MasterView(discord.ui.View):

    def __init__(self, dbcon, user_account_list):
        super().__init__(timeout=180)
        self.dbcon = dbcon
        self.user_account_list = user_account_list

    @discord.ui.button(label="Select Trader", style=discord.ButtonStyle.blurple)
    async def traderButton(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.edit_message(content=f"Account Selection",
                                                view=AccountSelectView(self.dbcon,
                                                                       self.user_account_list,
                                                                       "trader"))

    @discord.ui.button(label="Set Damage", style=discord.ButtonStyle.green)
    async def damageButton(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.edit_message(content=f"Account Selection",
                                                view=AccountSelectView(self.dbcon,
                                                                       self.user_account_list,
                                                                       "damage"))

    @discord.ui.button(label="Set/Reset API", style=discord.ButtonStyle.red)
    async def apiButton(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.edit_message(content=f"Account Selection",
                                                view=AccountSelectView(self.dbcon,
                                                                       self.user_account_list,
                                                                       "api"))

    @discord.ui.button(label="Done!", style=discord.ButtonStyle.gray)
    async def reportA(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.edit_message(content="", view=None, delete_after=1)
    
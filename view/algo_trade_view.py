import discord
import message as ms
from view.account_select_view import AccountSelectView

class AlgoTradeView(discord.ui.View):

    def __init__(self, dbcon, user_account_list):
        super().__init__(timeout=None)
        self.dbcon = dbcon
        self.user_account_list = user_account_list

    @discord.ui.button(label="Algo Strategies", style=discord.ButtonStyle.green)
    async def algo_strategies_button(self, interaction: discord.Interaction, button: discord.ui.Button):

        # Fetch active strategies
        strategies = self.dbcon.get_all_active_strategies()

        if not strategies:
            await interaction.followup.send(content=ms.NO_ALGO_STRATEGY, ephemeral=True)
            return
        await interaction.response.edit_message(content=f"Account Selection", view=AccountSelectView(self.dbcon, self.user_account_list, "strategy", strategies=strategies))

    @discord.ui.button(label="Set/Reset API", style=discord.ButtonStyle.red)
    async def set_reset_api_button(self, interaction: discord.Interaction, button: discord.ui.Button):

        await interaction.response.edit_message(content=f"Account Selection", view=AccountSelectView(self.dbcon, self.user_account_list, "api"))

    @discord.ui.button(label="Done!", style=discord.ButtonStyle.gray)
    async def done_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.edit_message(view=None, delete_after=1)
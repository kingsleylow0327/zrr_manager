import discord
import message as ms
from view.algo_trade_view import AlgoTradeView

from view.master_view import MasterView
from view.status_view import StatusView


class AutoTradeManagerView(discord.ui.View):

    def __init__(self, dbcon):
        super().__init__(timeout=None)
        self.dbcon = dbcon

    @discord.ui.button(label="AutoTrade", style=discord.ButtonStyle.blurple, custom_id="auto_trade_button")
    async def auto_trade_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer(ephemeral=True)

        player_id = str(interaction.user.id)
        user_account_list = self.dbcon.get_all_player_status(player_id)
        license_list = self.dbcon.get_license(player_id)

        if not user_account_list and not license_list:
            await interaction.followup.send(content=ms.NO_ACCOUNT, ephemeral=True)
            return

        status_view = StatusView(self.dbcon, interaction, user_account_list, player_id, "atm")
        embedded_status_list = status_view.compute()
        await interaction.followup.send(content="Welcome to AutoTrade Manager", embeds=embedded_status_list, view=MasterView(self.dbcon, user_account_list, license_list), ephemeral=True)
    
    @discord.ui.button(label="Algo Trade", style=discord.ButtonStyle.green, custom_id="algo_trade_button")
    async def algo_trade_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer(ephemeral=True)

        player_id = str(interaction.user.id)
        user_account_list = self.dbcon.get_all_player_status(player_id, "strategy")

        if not user_account_list:
            await interaction.followup.send(content=ms.NO_ACCOUNT, ephemeral=True)
            return
        
        status_view = StatusView(self.dbcon, interaction, user_account_list, player_id, "strategy")
        embedded_status_list = status_view.compute()
        await interaction.followup.send(content="Welcome to AlgoTrade Manager", embeds=embedded_status_list, view=AlgoTradeView(self.dbcon, user_account_list), ephemeral=True)
        
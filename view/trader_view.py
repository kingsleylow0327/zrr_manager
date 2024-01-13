import discord
from discord.interactions import Interaction

class PlayerDropDown(discord.ui.Select):
    def __init__(self, trader_list, dbcon):
        self.dbcon = dbcon
        traders = [discord.SelectOption(label=t.get("player_id"),
                                        value=t.get("player_id")) for t in trader_list]
        super().__init__(placeholder="Trader Id", options=traders, min_values=1, max_values=1)

    async def callback(self, interaction: Interaction):
        trader_id = str(self.values[0])
        self.dbcon.updare_trader_list(trader_id, interaction.user.id)
        await interaction.response.send_message(f"You have selected <@{trader_id}> as your trader", ephemeral=True)

class TraderSelectView(discord.ui.View):
    def __init__(self, dbcon):
        super().__init__()
        trader_list = dbcon.get_trader_list()
        self.add_item(PlayerDropDown(trader_list, dbcon))
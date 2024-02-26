import discord
from discord.interactions import Interaction

class PlayerDropDown(discord.ui.Select):
    def __init__(self, trader_list, dbcon, ref_id):
        self.dbcon = dbcon
        self.ref_id = ref_id
        traders = [discord.SelectOption(label=t.get("trader_name"),
                                        value=f"{t.get('trader_name')}*{t.get('trader_id')}") for t in trader_list]
        super().__init__(placeholder="Trader Id", options=traders, min_values=1, max_values=1)

    async def callback(self, interaction: Interaction):
        trader_detail = self.values[0].split("*")
        trader_name = trader_detail[0]
        trader_id = trader_detail[1]
        self.dbcon.update_trader_list(trader_id, self.ref_id)
        await interaction.response.send_message(f"You have selected ***{trader_name}*** as your trader", ephemeral=True)


class TraderSelectView(discord.ui.View):
    def __init__(self, dbcon, ref_id):
        super().__init__()
        trader_list = dbcon.get_trader_list()
        self.add_item(PlayerDropDown(trader_list, dbcon, ref_id))
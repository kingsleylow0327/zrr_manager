import discord
from discord.interactions import Interaction

class DamageDropDown(discord.ui.Select):
    def __init__(self, dbcon, account_name):
        self.dbcon = dbcon
        self.account_name = account_name
        damage = [discord.SelectOption(label=str(num),
                                        value=str(num)) for num in range(1, 11)]
        super().__init__(placeholder="Damage Cost %", options=damage, min_values=1, max_values=1)

    async def callback(self, interaction: Interaction):
        damage_cost = self.values[0]
        self.dbcon.update_damage_cost(damage_cost, self.account_name)
        await interaction.response.edit_message(content=f"You have set your damage cost to ***{damage_cost}***", view=None)


class DamageSelectView(discord.ui.View):
    def __init__(self, dbcon, account_name):
        super().__init__()
        self.add_item(DamageDropDown(dbcon, account_name))
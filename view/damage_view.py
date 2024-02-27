import discord
from discord.interactions import Interaction

class DamageDropDown(discord.ui.Select):
    def __init__(self, dbcon, ref_id):
        self.dbcon = dbcon
        self.ref_id = ref_id
        damage = [discord.SelectOption(label=str(num),
                                        value=str(num)) for num in range(1, 11)]
        super().__init__(placeholder="Damage Cost %", options=damage, min_values=1, max_values=1)

    async def callback(self, interaction: Interaction):
        damage_cost = self.values[0]
        self.dbcon.update_damage_cost(damage_cost, self.ref_id)
        await interaction.response.send_message(f"You have set your damage cost to ***{damage_cost}***", ephemeral=True)


class DamageSelectView(discord.ui.View):
    def __init__(self, dbcon, ref_id):
        super().__init__()
        self.add_item(DamageDropDown(dbcon, ref_id))
import discord
from logger import Logger

logger_mod = Logger("Algo Strategy")
logger = logger_mod.get_logger()

class AlgoStrategyView(discord.ui.View):
    def __init__(self, dbcon, strategies):
        super().__init__(timeout=None)
        self.dbcon = dbcon
        self.strategies = strategies
        self.selected_values = []
        self.add_item(AlgoStrategySelect(self, strategies))

class AlgoStrategySelect(discord.ui.Select):
    def __init__(self, parent_view, strategies):
        self.parent_view = parent_view
        options = [
            discord.SelectOption(label=strategy['name'], value=str(strategy['id']))
            for strategy in strategies
        ]

        super().__init__(
            placeholder="Select up to 5 algo strategies...",
            min_values=0, # Allow no selection
            max_values=5, # Allow max 5 strategies
            options=options
        )

    async def callback(self, interaction: discord.Interaction):
        selected_strategies = self.values
        discord_id = interaction.user.id

        try:
            if selected_strategies:
                self.parent_view.dbcon.update_follower_strategy(', '.join(selected_strategies), discord_id)
                await interaction.response.send_message(f"Algo strategies successfully updated!", ephemeral=True, delete_after=1)
            else:
                self.parent_view.dbcon.update_follower_strategy("", discord_id)
                await interaction.response.send_message("No strategies selected. All strategies have been removed.", ephemeral=True, delete_after=1)
        except Exception as e:
            logger.error(e)
            await interaction.response.send_message(f"Algo strategies updated failed!", ephemeral=True, delete_after=1)

        await interaction.edit_original_response(view=None)

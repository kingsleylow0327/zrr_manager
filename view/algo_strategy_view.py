import discord
from logger import Logger

logger_mod = Logger("Algo Strategy")
logger = logger_mod.get_logger()

class AlgoStrategyView(discord.ui.View):
    def __init__(self, dbcon, strategies, selected_account):
        super().__init__(timeout=None)
        self.dbcon = dbcon
        self.strategies = strategies
        self.add_item(AlgoStrategySelect(self, strategies, selected_account))

class AlgoStrategySelect(discord.ui.Select):
    def __init__(self, parent_view, strategies, selected_account):
        self.parent_view = parent_view
        self.selected_account = selected_account
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
        discord_id = self.selected_account

        try:
            if selected_strategies:
                self.parent_view.dbcon.update_follower_strategy(','.join(selected_strategies), discord_id)
                await interaction.response.edit_message(content="Algo strategies successfully updated!", 
                                                        embed=None,
                                                        delete_after=5)
            else:
                self.parent_view.dbcon.update_follower_strategy("", discord_id)
                await interaction.response.edit_message(content="No strategies selected. All strategies have been removed.", 
                                                        embed=None,
                                                        delete_after=5)
        except Exception as e:
            logger.error(e)
            await interaction.response.edit_message(content="Algo strategies updated failed!", 
                                                    embed=None,
                                                    delete_after=5)

        await interaction.edit_original_response(view=None)

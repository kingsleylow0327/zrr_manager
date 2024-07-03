import discord
import message as ms
from bingx import BINGX

MIN_WALLET = 300
MAX_WALLET = 3000

class StatusView():
    
    def __init__(self, dbcon, interaction, trader_api_list):
        self.dbcon = dbcon
        self.interaction = interaction 
        self.trader_api_list = trader_api_list
    
    def compute(self):
        embed_list = []
        count = 1
        if not self.trader_api_list:
            return []
        for trader_api in self.trader_api_list:
            embed = discord.Embed(title=f"# Your AutoTrade Account {count} Status", description="")
            bingx = BINGX(trader_api.get("api_key"), trader_api.get("api_secret"))
            response = bingx.get_wallet()
            
            msg_api = "❌"
            msg_wallet_min = "❌"
            msg_wallet_max = "❌"
            msg_trader = "❌"
            balance = "❌"
            expiry = "None"
            if trader_api.get('expiry_date'):
                expiry = trader_api.get('expiry_date')

            if trader_api.get("trader_name"):
                msg_trader = f" `{trader_api.get('trader_name')}`"

            if response.get("code") == 0 or response.get("code") == 200:
                msg_api = "✅"
                balance = float(response.get("data").get("balance").get("availableMargin"))
                if balance > float(MIN_WALLET):
                    msg_wallet_min = "✅"
                if balance < float(MAX_WALLET):
                    msg_wallet_max = "✅"

            embed.add_field(name=f"Account Name: {trader_api.get('player_id')} \n", value="", inline=False)
            embed.add_field(name=f"\n", value="", inline=False)
            embed.add_field(name=f"API Setup: {msg_api} \n", value="", inline=False)
            embed.add_field(name=f"Future Wallet > {MIN_WALLET}: {msg_wallet_min} \n", value="", inline=False)
            embed.add_field(name=f"Future Wallet < {MAX_WALLET}: {msg_wallet_max} \n", value="", inline=False)
            embed.add_field(name=f"Wallet Amount: `{balance}`", value="", inline=False)
            embed.add_field(name=f"\n", value="", inline=False)
            embed.add_field(name=f"Following Traders: {msg_trader}", value="", inline=False)
            embed.add_field(name=f"Damage Cost: `{trader_api.get('damage_cost')}%`", value="", inline=False)
            embed.add_field(name=f"Expiry Date: `{expiry}`", value="", inline=False)
            embed_list.append(embed)
            count += 1
        
        return embed_list
from dataclasses import dataclass, field
from typing import TYPE_CHECKING

import discord

from ballsdex.core.models import Player

if TYPE_CHECKING:
    from ballsdex.core.bot import BallsDexBot
    from ballsdex.core.models import BallInstance, Trade


@dataclass(slots=True)
class TradingUser:
    user: "discord.User | discord.Member"
    player: "Player"
    proposal: list["BallInstance"] = field(default_factory=list)
    locked: bool = False
    cancelled: bool = False
    accepted: bool = False
    coins: int = 0

    async def add_coins(self, amount: int):
        self.coins += amount
        await self.player.remove_coins(amount)

    async def remove_coins(self, amount: int):
        self.coins -= amount
        await self.player.add_coins(amount)

    async def fetch_player_coins(self) -> int:
        player, _ = await Player.get_or_create(discord_id=self.user.id)
        return player.coins

    @classmethod
    async def from_trade_model(cls, trade: "Trade", player: "Player", bot: "BallsDexBot"):
        proposal = await trade.tradeobjects.filter(player=player).prefetch_related("ballinstance")
        user = await bot.fetch_user(player.discord_id)
        coins = player.coins if player else 0
        return cls(user, player, [x.ballinstance for x in proposal], coins)

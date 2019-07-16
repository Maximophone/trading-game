from dataclasses import dataclass

from typing import NamedTuple, Dict, List, Tuple
import random
from threading import Thread
import time

UPDATE_FREQUENCY = 60
CLOSING_TIME = UPDATE_FREQUENCY * 5 - 1

class Portfolio:
    def __init__(self):
        self.capital = 0
        self.assets = 0

    def buy_assets(self, n_assets, price):
        self.assets += n_assets
        self.capital -= n_assets*price

    def sell_assets(self, n_assets, price):
        self.assets -= n_assets
        self.capital += n_assets*price

    def liquidate(self, price):
        self.capital += self.assets*price

@dataclass
class Participant:
    name: str
    hidden_value: int
    portfolio: Portfolio
    bid_price: float = -1
    ask_price: float = -1
    open: bool = False

class Sides:
    BUY = True
    SELL = False

@dataclass
class Order:
    side: bool
    quantity: int
    price: float
    participant_id: str
    filled: int = 0

def watch(f):
    def inner(self, *args, **kwargs):
        ret = f(self, *args, **kwargs)
        for callback in self.watch_callbacks:
            callback()
        return ret
    return inner

class Market(Thread):
    def __init__(self, n_periods=5, time_per_period=60):
        self.open = True
        self.timer = 0
        self.closing_time = n_periods * time_per_period - 1
        self.update_frequency = time_per_period
        self.values = [self.pick_new_value()]
        self.final_value = None
        self.ip_tokens: Dict[str, str] = {}
        self.token_id: Dict[str, str] = {}
        self.participants: Dict[id, Participant] = {}
        self.buy_book: Dict[float, List[Order]] = {}
        self.sell_book: Dict[float, List[Order]] = {}
        self.watch_callbacks = []
        super().__init__()

    def run(self): 
        while(self.open):
            time.sleep(1)
            self.timer += 1
            if self.timer % self.update_frequency == 0:
                self.values.append(self.pick_new_value())
                print("Updating market")
            if self.timer >= self.closing_time:
                self.open = False
                self.liquidate()
                print("Closing market")

    def pick_new_value(self) -> int:
        return random.randint(1, 100)

    @staticmethod
    def gen_token() -> str:
        return f"{random.getrandbits(32):x}"
    
    def add_watch(self, callback):
        self.watch_callbacks.append(callback)

    @watch
    def liquidate(self):
        all_values = self.values + [p.hidden_value for p in self.participants.values()]
        self.final_value = sum(all_values)/len(all_values)
        for participant in self.participants.values():
            portfolio = participant.portfolio
            portfolio.capital += portfolio.assets * self.final_value
            portfolio.assets = 0

    def get_id(self, token: str) -> str:
        assert token in self.token_id
        return self.token_id[token]

    @watch
    def join_market(self, user_id: str) -> int:
        assert user_id not in self.participants
        hidden_value: int = self.pick_new_value()
        self.participants[user_id] = Participant(user_id, hidden_value, Portfolio())
        return hidden_value

    def post_order(self, user_id: str, side: bool, quantity: int, price: float):
        assert user_id in self.participants
        order = Order(side, quantity, price, user_id)
        book = self.get_book(side)
        book.setdefault(price, []).append(order)

    def take_order(self, user_id: str, side: bool, quantity: int, price: float) -> int:
        book = self.get_book(side)
        participant = self.participants[user_id]
        orders_at_price = book.get(price, [])
        filled = 0
        for order in orders_at_price:
            if order.filled == order.quantity:
                continue
            # We should lock this order here...
            # First compute how much we can take on this order
            taken = min(quantity, order.quantity-order.filled)
            # Then remove this quantity
            order.filled += taken
            # Modify participant's portfolio
            counterparty = self.participants.get(order.participant_id)
            if side == Sides.BUY:
                participant.portfolio.sell_assets(taken, price)
                counterparty.portfolio.buy_assets(taken, price)
            if side == Sides.SELL:
                participant.portfolio.buy_assets(taken, price)
                counterparty.portfolio.sell_assets(taken, price)
            filled += taken
            assert filled <= quantity, "filled more than asked, something has gone wrong..."
            if filled == quantity:
                break
        return filled

    def get_book(self, side: bool):
        assert(type(side) == bool)
        if side==Sides.BUY:
            return self.buy_book
        if side==Sides.SELL:
            return self.sell_book

    @watch
    def take_price(self, user_id: str, counterparty_id: str, side: bool, price: float) -> bool:
        assert user_id in self.participants
        assert counterparty_id in self.participants
        participant = self.participants[user_id]
        counterparty = self.participants[counterparty_id]
        assert participant.open
        if not counterparty.open:
            return False
        # TODO: there will be synchronisation problems, when somebody closes their
        # prices while somebody else is taking it
        current_price = counterparty.bid_price if side == Sides.BUY else counterparty.ask_price
        if price != current_price:
            # The price has changed, we don't take it
            return False
        if side == Sides.BUY:
            participant.portfolio.sell_assets(1, price)
            counterparty.portfolio.buy_assets(1, price)
        if side == Sides.SELL:
            participant.portfolio.buy_assets(1, price)
            counterparty.portfolio.sell_assets(1, price)
        return True

    @watch
    def set_price(self, user_id: str, side: bool, price: float):
        assert user_id in self.participants
        assert price >= 0
        participant = self.participants[user_id]
        if side == Sides.BUY:
            participant.bid_price = price
        else:
            participant.ask_price = price

    @watch
    def set_open(self, user_id: str, is_open: bool):
        assert user_id in self.participants
        participant = self.participants[user_id]
        assert participant.bid_price >= 0 and participant.ask_price >= 0, "Must set prices before opening for offers"
        participant.open = is_open

def clear_markets(markets):
    keys = list(markets.keys())
    for market_id in keys:
        market = markets.pop(market_id)
        market.open = False
        del market

def init_markets(markets):
    from traders.app import emit_market_view
    clear_markets(markets)
    market_test = Market()
    market_test.join_market("max")
    market_test.join_market("bob")
    market_test.join_market("john")
    market_test.set_price("john", Sides.BUY, 10)
    market_test.set_price("john", Sides.SELL, 12)
    market_test.set_open("john", True)
    market_test.post_order("max", True, 100, 10)
    market_test.post_order("bob", False, 100, 20)
    market_test.post_order("max", False, 50, 10)
    market_test.post_order("john", True, 100, 5)
    market_test.post_order("max", True, 30, 10)
    market_test.post_order("bob", True, 20, 10)
    markets["Market1"] = market_test
    market_test.start()
    market_test.add_watch(emit_market_view("Market1", market_test))

def init_with_bots(markets):
    from traders.app import emit_market_view
    from traders.bots import Bot
    clear_markets(markets)
    market_with_bots = Market()
    bot_names = ["bob", "will", "dawn", "jerry"]
    bots = []
    for name in bot_names:
        bots.append(Bot(name, market_with_bots))
    markets["BotLand"] = market_with_bots
    market_with_bots.start()
    market_with_bots.add_watch(emit_market_view("BotLand", market_with_bots))
    for bot in bots:
        bot.start()
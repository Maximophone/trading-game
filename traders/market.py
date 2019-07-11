from dataclasses import dataclass, asdict
from typing import NamedTuple, Dict, List, Tuple
import random
from threading import Thread
import time

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

class Participant(NamedTuple):
    name: str
    hidden_value: int
    portfolio: Portfolio

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

class Market(Thread):
    def __init__(self):
        self.open = True
        self.timer = 0
        self.closing_time = 100
        self.values = [self.pick_new_value()]
        self.ip_tokens: Dict[str, str] = {}
        self.token_id: Dict[str, str] = {}
        self.participants: Dict[id, Participant] = {}
        self.buy_book: Dict[float, List[Order]] = {}
        self.sell_book: Dict[float, List[Order]] = {}
        super().__init__()

    def run(self):
        # First phase, waiting for traders arrival
        while(self.open):
            time.sleep(1)
            self.timer += 1
            if self.timer >= self.closing_time:
                self.open=False

    def pick_new_value(self) -> int:
        return random.randint(1, 100)

    @staticmethod
    def gen_token() -> str:
        return f"{random.getrandbits(32):x}"

    def get_id(self, token: str) -> str:
        assert token in self.token_id
        return self.token_id[token]

    def join_market(self, user_ip: str, user_id: str) -> Tuple[str, int]:
        assert user_ip not in self.ip_tokens
        assert user_id not in self.participants
        token = self.gen_token()
        self.ip_tokens[user_ip] = token
        self.token_id[token] = user_id
        hidden_value: int = self.pick_new_value()
        self.participants[user_id] = Participant(user_id, hidden_value, Portfolio())
        return token, hidden_value

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

market_test = Market()
markets: Dict[str, Market] = {"Market1": market_test}
market_test.join_market("1", "max")
market_test.join_market("2", "bob")
market_test.join_market("3", "john")
market_test.post_order("max", True, 100, 10)
market_test.post_order("bob", False, 100, 20)
market_test.post_order("max", False, 50, 10)
market_test.post_order("john", True, 100, 5)
market_test.post_order("max", True, 30, 10)
market_test.post_order("bob", True, 20, 10)
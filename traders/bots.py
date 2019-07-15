from threading import Thread
from traders.market import Market, Sides
import time
import random

BOT_NAMES = [
    "joe",
    "bill",
    "chad",
    "mary",
    "susan",
    "connor",
    "sam",
    "bob",
    "bert",
    "gala"
]

class Bot(Thread):
    def __init__(self, name: str, market: Market, refresh_frequency=2, spread=0.1):
        self.bot_name = name
        self.market = market
        self.joined = False
        self.participant = None
        self.refresh_frequency = refresh_frequency
        self.spread=spread
        super().__init__()

    @property
    def guessed_value(self):
        if not self.joined:
            return None
        all_values = self.market.values + [self.participant.hidden_value]
        others_guesses = [(p.bid_price + p.ask_price)/2 for name, p in self.market.participants.items() if name != self.bot_name]
        all_values += others_guesses
        return sum(all_values)/len(all_values)

    @property
    def sell_price(self):
        return int(self.guessed_value * (1+self.spread))

    @property
    def buy_price(self):
        return int(self.guessed_value * (1-self.spread))

    def run(self):
        time.sleep(random.random()) #desynchronising the bots
        while(self.market.open):
            if not self.joined:
                self.join_market()
            self.adjust_prices()
            self.take_prices()
            time.sleep(self.refresh_frequency)
    
    def join_market(self):
        self.market.join_market(self.bot_name)
        self.participant = self.market.participants[self.bot_name]
        self.joined = True

    def adjust_prices(self):
        if self.participant.bid_price != self.buy_price:
            self.market.set_price(self.bot_name, Sides.BUY, self.buy_price)
        if self.participant.ask_price != self.sell_price:
            self.market.set_price(self.bot_name, Sides.SELL, self.sell_price)
        if not self.participant.open:
            self.market.set_open(self.bot_name, True)

    def take_prices(self):
        for name, counterparty in self.market.participants.items():
            if name == self.bot_name:
                continue
            if not counterparty.open:
                continue
            if not self.market.open:
                break
            if counterparty.bid_price > self.sell_price:
                self.market.take_price(self.bot_name, name, Sides.BUY, counterparty.bid_price)
            if counterparty.ask_price < self.buy_price:
                self.market.take_price(self.bot_name, name, Sides.SELL, counterparty.ask_price)
            
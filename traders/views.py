from traders.market import Market, Participant, Portfolio
from dataclasses import asdict
from typing import Dict, Any

def view_markets(markets):
    return [{
            "id": id,
            "is_open": mkt.open,
        }
        for id, mkt in markets.items()]

def view_market(id: str, market: Market):
    ret = {"name": id, "id": id}
    ret["books"] = view_books(market)
    ret["participants"] = view_participants(market)
    ret["market_values"] = market.values
    ret["open"] = market.open
    ret["final_value"] = market.final_value
    return ret

def view_books(market: Market):
    ret = {}
    for side, book in [("buy", market.buy_book), ("sell", market.sell_book)]:
        ret[side] = {
            price: [asdict(order) for order in orders]
            for price, orders in book.items()
            }
    return ret

def view_portfolio(portfolio: Portfolio) -> Dict[str, Any]:
    return {
        "assets": portfolio.assets,
        "capital": portfolio.capital
    }

def view_participant(id: str, participant: Participant) -> Dict[str, Any]:
    return {
        "id": id,
        "name": participant.name,
        "portfolio": view_portfolio(participant.portfolio),
        "open": participant.open,
        "bid_price": participant.bid_price,
        "ask_price": participant.ask_price
    }

def view_participants(market: Market):
    participants_list = []
    for p_id, participant in market.participants.items():
        participants_list.append(view_participant(p_id, participant))
    return participants_list
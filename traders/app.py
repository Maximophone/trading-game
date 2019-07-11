from flask import Flask, request, jsonify, render_template
from dataclasses import asdict

from traders.market import Market, Sides, markets
from traders.app_utils import error, check_market, check_participant, check_form_values

app = Flask(__name__, static_url_path="/static/")

def get_markets_list():
    return [{
            "id": id,
            "is_open": mkt.open,
        }
        for id, mkt in markets.items()]

@app.route("/ping")
def ping():
    return "pong"

@app.route("/")
def index():
    return render_template("index.html",  markets=get_markets_list())

@app.route("/markets/new", methods=["POST"])
@check_form_values(name=str)
def new_market():
    name = request.form["name"]
    if not name.isalnum():
        return jsonify(error("Market name must be alphanumeric without space"))
    if name in markets:
        return jsonify(error("Market name already taken"))
    markets[name] = Market()
    markets[name].start()
    return jsonify({"market_id": name})

@app.route("/markets", methods=["GET"])
def get_markets():
    return jsonify(get_markets_list())

@app.route("/market/<market_id>")
def market_index(market_id):
    return render_template("market.html", market_id=market_id)

@app.route("/market/<market_id>/join", methods=["POST"])
@check_form_values(name=str)
@check_market
def join_market(market_id):
    user_ip = request.remote_addr
    market = markets.get(market_id)
    if user_ip in market.ip_tokens:
        return jsonify(error(f"User already in market, can only join once"))
    if request.form["name"] in market.participants:
        return jsonify(error(f"Username is already taken, select a new one"))
    token, hidden_value = market.join_market(user_ip, request.form.get("name"))
    return jsonify({
        "token": token,
        "market_values": market.values,
        "hidden_value": hidden_value
    })

@app.route("/market/<market_id>/books", methods=["GET"])
@check_market
def get_books(market_id):
    market = markets.get(market_id)
    ret = {}
    for side, book in [("buy", market.buy_book), ("sell", market.sell_book)]:
        ret[side] = {
            price: [asdict(order) for order in orders]
            for price, orders in book.items()
            }
    return jsonify(ret)

@app.route("/market/<market_id>/order/post/buy", methods=["POST"])
@check_market
@check_participant
@check_form_values(quantity=int, price=float)
def post_order_buy(market_id):
    market = markets.get(market_id)
    user_id = market.get_id(request.form["token"])
    market.post_order(user_id, Sides.BUY, request.form["quantity"], request.form["price"])
    return jsonify({})

@app.route("/market/<market_id>/order/post/sell", methods=["POST"])
@check_market
@check_participant
@check_form_values(quantity=int, price=float)
def post_order_sell(market_id):
    market = markets.get(market_id)
    user_id = market.get_id(request.form["token"])
    market.post_order(user_id, Sides.SELL, request.form["quantity"], request.form["price"])
    return jsonify({})

@app.route("/market/<market_id>/order/take/buy", methods=["POST"])
@check_market
@check_participant
@check_form_values(quantity=int, price=float)
def take_order_buy(market_id):
    market = markets.get(market_id)
    user_id = market.get_id(request.form["token"])
    side, quantity, price = Sides.BUY, request.form["quantity"], request.form["price"]
    filled = market.take_order(user_id, side, quantity, price)
    return jsonify({
        "filled": filled
    })

@app.route("/market/<market_id>/order/take/sell", methods=["POST"])
@check_market
@check_participant
@check_form_values(quantity=int, price=float)
def take_order_sell(market_id):
    market = markets.get(market_id)
    user_id = market.get_id(request.form["token"])
    side, quantity, price = Sides.SELL, request.form["quantity"], request.form["price"]
    filled = market.take_order(user_id, side, quantity, price)
    return jsonify({
        "filled": filled
    })

@app.route("/market/<market_id>/portfolio", methods=["GET"])
@check_market
@check_participant
def get_portfolio(market_id):
    market = markets.get(market_id)
    user_id = market.get_id(request.form["token"])
    portfolio = market.participants[user_id].portfolio
    return jsonify({
        "capital": portfolio.capital,
        "assets": portfolio.assets
    })

if __name__ == "__main__":
    app.run(port=4000, debug=True)
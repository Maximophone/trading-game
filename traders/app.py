from flask import Flask, session, request, Response, jsonify, render_template
from flask_cors import CORS, cross_origin
from flask_socketio import SocketIO
from typing import Dict, Any

from traders.market import Market, Sides, Participant, Portfolio, init_markets, init_with_bots
from traders.bots import Bot, BOT_NAMES
from traders.secret import SECRET_KEY

app = Flask(__name__, static_url_path="/static/")
cors = CORS(app, supports_credentials=True)
socketio = SocketIO(app)
app.config["CORS_HEADERS"] = "Content-Type"

app.secret_key = SECRET_KEY

USERS = set()
MARKETS: Dict[str, Market] = {}

from traders.app_utils import error, check_market, check_participant, check_json_values, check_logged_in
from traders.views import *


@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    if "Access-Control-Allow-Credentials" in response.headers:
        response.headers.set('Access-Control-Allow-Credentials', 'true')
    else:
        response.headers.add('Access-Control-Allow-Credentials', 'true')
    return response

@socketio.on("connection")
def handle_connection(json):
    print(f"New connection: {json}")
    return request.sid

@socketio.on("disconnect")
def handle_disconnection():
    print(f"Session id: {request.sid} disconnected")

def ping_users():
    socketio.emit("ping", "ping")

def emit_market_view(market_id, market):
    def inner():
        socketio.emit(f"market_update_{market_id}", view_market(market_id, market))
    return inner

@app.route("/ping")
def ping():
    return "pong"

@app.route("/")
def index():
    return render_template("index.html",  markets=view_markets(MARKETS))

@app.route("/login", methods=["POST"])
@cross_origin()
@check_json_values(name=str)
def login():
    if "user_id" in session:
        return jsonify(error("Already logged in with username " + session["user_id"]))
    if request.checked_json["name"] in USERS:
        return jsonify(error("Username is already taken, please choose an other one"))
    session["user_id"] = request.checked_json["name"]
    USERS.add(request.checked_json["name"])
    return jsonify({"status": "login succesful"})

@app.route("/login", methods=["GET"])
@cross_origin()
def get_login():
    if "user_id" in session:
        return jsonify({
            "logged_in": True,
            "name": session["user_id"]
        })
    else:
        return jsonify({
            "logged_in": False
        })

@app.route("/markets/new", methods=["POST"])
@cross_origin()
@check_json_values(name=str, bots=int)
def new_market():
    name = request.checked_json["name"]
    if not name.isalnum():
        return jsonify(error("Market name must be alphanumeric without space"))
    if name in MARKETS:
        return jsonify(error("Market name already taken"))
    market = Market()
    market.start()
    market.add_watch(emit_market_view(name, market))
    MARKETS[name] = market
    n_bots = max(0, min(10, request.checked_json["bots"]))
    for name in BOT_NAMES[:n_bots]:
        bot = Bot(name, market)
        bot.start()
    return jsonify({"market_id": name})

@app.route("/markets", methods=["GET"])
@cross_origin()
def get_markets():
    return jsonify(view_markets(MARKETS))

@app.route("/market/<market_id>")
@cross_origin()
@check_logged_in
@check_market
def market_view(market_id):
    market = MARKETS.get(market_id)
    market_view = view_market(market_id, market)
    user_id = session["user_id"]
    market_view["joined"] = user_id in market.participants
    if user_id in market.participants:
        market_view["hidden_value"] = market.participants[user_id].hidden_value
    return jsonify(market_view)

@app.route("/market/<market_id>/join", methods=["POST"])
@cross_origin()
@check_market
@check_logged_in
def join_market(market_id):
    user_id = session["user_id"]
    market = MARKETS.get(market_id)
    if user_id in market.participants:
        return jsonify(error(f"User already in market, can only join once"))
    hidden_value = market.join_market(user_id)
    participants = view_participants(market)
    return jsonify({
        "market_values": market.values,
        "hidden_value": hidden_value,
        "participants": participants
    })

@app.route("/market/<market_id>/books", methods=["GET"])
@check_market
def market_books(market_id):
    market = MARKETS.get(market_id)
    return jsonify(view_books(market))

@app.route("/market/<market_id>/order/post/buy", methods=["POST"])
@check_market
@check_logged_in
@check_participant
@check_json_values(quantity=int, price=float)
def post_order_buy(market_id):
    market = MARKETS.get(market_id)
    user_id = session["user_id"]
    market.post_order(user_id, Sides.BUY, request.checked_json["quantity"], request.checked_json["price"])
    return jsonify({})

@app.route("/market/<market_id>/order/post/sell", methods=["POST"])
@check_market
@check_logged_in
@check_participant
@check_json_values(quantity=int, price=float)
def post_order_sell(market_id):
    market = MARKETS.get(market_id)
    user_id = session["user_id"]
    market.post_order(user_id, Sides.SELL, request.checked_json["quantity"], request.checked_json["price"])
    return jsonify({})

@app.route("/market/<market_id>/order/take/buy", methods=["POST"])
@check_market
@check_logged_in
@check_participant
@check_json_values(quantity=int, price=float)
def take_order_buy(market_id):
    market = MARKETS.get(market_id)
    user_id = session["user_id"]
    side, quantity, price = Sides.BUY, request.checked_json["quantity"], request.checked_json["price"]
    filled = market.take_order(user_id, side, quantity, price)
    return jsonify({
        "filled": filled
    })

@app.route("/market/<market_id>/order/take/sell", methods=["POST"])
@check_market
@check_logged_in
@check_participant
@check_json_values(quantity=int, price=float)
def take_order_sell(market_id):
    market = MARKETS.get(market_id)
    user_id = session["user_id"]
    side, quantity, price = Sides.SELL, request.checked_json["quantity"], request.checked_json["price"]
    filled = market.take_order(user_id, side, quantity, price)
    return jsonify({
        "filled": filled
    })

@app.route("/market/<market_id>/portfolio", methods=["GET"])
@cross_origin()
@check_market
@check_logged_in
@check_participant
def get_portfolio(market_id):
    market = MARKETS.get(market_id)
    user_id = session["user_id"]
    portfolio = market.participants[user_id].portfolio
    return jsonify({
        "capital": portfolio.capital,
        "assets": portfolio.assets
    })

@app.route("/market/<market_id>/offers/set", methods=["POST"])
@cross_origin()
@check_market
@check_participant
@check_json_values(is_open=bool, sell_price=float, buy_price=float)
def set_prices(market_id):
    market = MARKETS.get(market_id)
    user_id = session["user_id"]
    market.set_price(user_id, Sides.BUY, request.checked_json["buy_price"])
    market.set_price(user_id, Sides.SELL, request.checked_json["sell_price"])
    market.set_open(user_id, request.checked_json["is_open"])
    return jsonify({
        "status": "success"
    })

@app.route("/market/<market_id>/offers/set/<side>", methods=["POST"])
@cross_origin()
@check_market
@check_participant
@check_json_values(price=float)
def set_price(market_id, side):
    if side not in ("buy", "sell"):
        return jsonify(error("side must be 'buy' or 'sell'"))
    market = MARKETS.get(market_id)
    user_id = session["user_id"]
    market.set_price(user_id, Sides.BUY if side=="buy" else Sides.SELL, request.checked_json["price"])
    return jsonify({
        "status": "success"
    })

@app.route("/market/<market_id>/offers/set_open", methods=["POST"])
@cross_origin()
@check_market
@check_participant
@check_json_values(open=bool)
def set_open(market_id):
    market = MARKETS.get(market_id)
    user_id = session["user_id"]
    participant = market.participants[user_id]
    open_ = request.checked_json["open"]
    if open_ and (participant.bid_price < 0 or participant.ask_price < 0):
        return jsonify(error("bid and ask prices must be set before opening"))
    market.set_open(user_id, open_)
    return jsonify({
        "status": "success"
    })

@app.route("/market/<market_id>/offers/take", methods=["POST"])
@cross_origin()
@check_market
@check_participant
@check_json_values(counterparty_id = str, price = float, side = bool)
def take_offer(market_id):
    market = MARKETS.get(market_id)
    user_id = session["user_id"]
    participant = market.participants[user_id]
    if not participant.open:
        return jsonify(error("must be open to offers to be able to take offers"))
    counterparty_id, price, side = request.checked_json["counterparty_id"], request.checked_json["price"], request.checked_json["side"]
    if counterparty_id not in market.participants:
        return jsonify(error("counterparty is not in market"))
    counterparty = market.participants[counterparty_id]
    if not counterparty.open:
        return jsonify(error("counterparty is closed to offers"))
    counterparty_price = counterparty.bid_price if side==Sides.BUY else counterparty.ask_price
    if counterparty_price != price:
        return jsonify(error("counterparty price has changed"))
    success = market.take_price(user_id, counterparty_id, side, counterparty_price)
    if not success:
        return jsonify(error("counterparty has closed to offers or changed price"))
    return jsonify({
        "status": "success"
    })

# init_markets(MARKETS)
# init_with_bots(MARKETS)

if __name__ == "__main__":
    app.run(port=4000, debug=True)
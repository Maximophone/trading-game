from flask import Flask, session, request, Response, jsonify, render_template
from flask_cors import CORS, cross_origin
from dataclasses import asdict

from traders.market import Market, Sides, markets
from traders.app_utils import error, check_market, check_participant, check_json_values, check_logged_in

app = Flask(__name__, static_url_path="/static/")
cors = CORS(app, supports_credentials=True)
app.config["CORS_HEADERS"] = "Content-Type"

app.secret_key = b"dummy_key"

USERS = set()

@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    if "Access-Control-Allow-Credentials" in response.headers:
        response.headers.set('Access-Control-Allow-Credentials', 'true')
    else:
        response.headers.add('Access-Control-Allow-Credentials', 'true')
    return response

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
@check_json_values(name=str)
def new_market():
    name = request.checked_json["name"]
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
@check_market
@check_logged_in
def join_market(market_id):
    user_id = session["user_id"]
    market = markets.get(market_id)
    if user_id in market.participants:
        return jsonify(error(f"User already in market, can only join once"))
    hidden_value = market.join_market(user_id)
    return jsonify({
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
@check_logged_in
@check_participant
@check_json_values(quantity=int, price=float)
def post_order_buy(market_id):
    market = markets.get(market_id)
    user_id = session["user_id"]
    market.post_order(user_id, Sides.BUY, request.checked_json["quantity"], request.checked_json["price"])
    return jsonify({})

@app.route("/market/<market_id>/order/post/sell", methods=["POST"])
@check_market
@check_logged_in
@check_participant
@check_json_values(quantity=int, price=float)
def post_order_sell(market_id):
    market = markets.get(market_id)
    user_id = session["user_id"]
    market.post_order(user_id, Sides.SELL, request.checked_json["quantity"], request.checked_json["price"])
    return jsonify({})

@app.route("/market/<market_id>/order/take/buy", methods=["POST"])
@check_market
@check_logged_in
@check_participant
@check_json_values(quantity=int, price=float)
def take_order_buy(market_id):
    market = markets.get(market_id)
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
    market = markets.get(market_id)
    user_id = session["user_id"]
    side, quantity, price = Sides.SELL, request.checked_json["quantity"], request.checked_json["price"]
    filled = market.take_order(user_id, side, quantity, price)
    return jsonify({
        "filled": filled
    })

@app.route("/market/<market_id>/portfolio", methods=["GET"])
@check_market
@check_logged_in
@check_participant
def get_portfolio(market_id):
    market = markets.get(market_id)
    user_id = session["user_id"]
    portfolio = market.participants[user_id].portfolio
    return jsonify({
        "capital": portfolio.capital,
        "assets": portfolio.assets
    })

if __name__ == "__main__":
    app.run(port=4000, debug=True)
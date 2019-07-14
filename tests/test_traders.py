from traders import __version__
from traders.app import app, USERS
from traders.market import markets, init_markets, Sides

import pytest

@pytest.fixture(autouse=True)
def clear_users():
    USERS.clear()

@pytest.fixture(autouse=True)
def restart_markets():
    init_markets(markets)

@pytest.fixture
def client():
    app.config["TESTING"] = True
    client = app.test_client()
    yield client

@pytest.fixture(scope='session', autouse=True)
def stop_markets():
    # Will be executed before the first test
    yield None
    # Will be executed after the last test
    for market in markets.values():
        market.open = False

def get_200(client, req, *args, ip=None, **kwargs):
    if ip is not None:
        response = client.get(req, *args, environ_base={'REMOTE_ADDR': ip}, **kwargs)
    else:
        response = client.get(req, *args, **kwargs)
    assert response.status_code == 200
    return response.get_json()

def post_200(client, req, *args, ip=None, **kwargs):
    if ip is not None:
        response = client.post(req, *args, environ_base={'REMOTE_ADDR': ip}, **kwargs)
    else:
        response = client.post(req, *args, **kwargs)
    assert response.status_code == 200
    return response.get_json()


def test_version():
    assert __version__ == '0.1.0'

def test_ping(client):
    rv = client.get("/ping")
    assert rv.status=="200 OK"
    assert rv.data.decode() == "pong"

initial_market = {"id": list(markets.keys())[0], "is_open":True}

def test_get_markets(client):
    rv = client.get("/markets")
    assert rv.status_code == 200
    assert rv.get_json() == [initial_market]

def test_new_market(client):
    rv = client.post("/markets/new", json=dict(name="2"))
    assert rv.status_code == 200
    assert rv.get_json() == {"market_id": "2"}
    rv = client.get("/markets")
    assert rv.status_code == 200
    assert rv.get_json() == [initial_market, {"id": "2", "is_open": True}]

def test_login(client):
    resp = get_200(client, "/login")
    assert resp == {"logged_in": False}

    resp = post_200(client, "/login", json={"name": "max"})
    assert resp == {"status": "login succesful"}

    resp = get_200(client, "/login")
    assert resp == {"logged_in": True, "name": "max"}

def test_market_view(client):
    resp = get_200(client, "/market/Market1")
    assert "books" in resp
    assert "participants" in resp
    assert "name" in resp
    assert "id" in resp

    assert resp["id"] == "Market1"
    assert resp["name"] == "Market1"

    participants = resp["participants"]

    assert len(participants) == 3
    
    participant_max = participants[0]

    assert participant_max == {"id": "max", "name": "max", "portfolio": {"assets": 0, "capital": 0}, "open": False, "bid_price": -1, "ask_price": -1}

    books = resp["books"]

    assert "buy" in books
    assert "sell" in books

    buy_book = books["buy"]

    assert "10" in buy_book
    assert "5" in buy_book

    price_level_10 = buy_book["10"]

    assert len(price_level_10) == 3
    assert price_level_10[0] == {"filled": 0, "participant_id": "max", "price": 10, "quantity": 100, "side": True}

def test_scenario(client):
    post_200(client, "/markets/new", json=dict(name="2"))
    
    # Max logs in
    login_resp = post_200(client, "/login", json={"name": "max"})
    assert login_resp == {"status": "login succesful"}

    # Max joins market 2
    join_resp = post_200(client, "/market/2/join")
    assert "market_values" in join_resp
    assert "hidden_value" in join_resp

    # Max checks his portfolio
    portfolio_resp = get_200(client, "/market/2/portfolio")
    assert portfolio_resp == {"assets": 0, "capital": 0}

    # Max posts buy order
    post_200(client, "/market/2/order/post/buy", json=dict(quantity=100, price=10))
    book_resp = get_200(client, "/market/2/books")

    expected_book = {
        "buy": {
            "10.0": [
                {"filled": 0, "participant_id": "max", "price": 10., "quantity": 100, "side": True}
            ]
        }, 
        "sell": {}
    }
    assert book_resp == expected_book

    take_resp = post_200(client, "/market/2/order/take/sell", json=dict(quantity=50, price=10))
    assert take_resp == {"filled": 0}

    take_resp = post_200(client, "/market/2/order/take/buy", json=dict(quantity=40, price=10.))
    assert take_resp == {"filled": 40}

    # taking his own order
    book_resp = get_200(client, "/market/2/books")
    expected_book = {
        "buy": {
            "10.0": [
                {"filled": 40, "participant_id": "max", "price": 10., "quantity": 100, "side": True}
            ]
        },
        "sell": {}
    }
    assert book_resp == expected_book

    # Checking porfolio
    portfolio = get_200(client, "/market/2/portfolio")
    assert portfolio == {"assets": 0, "capital": 0.}

    # Bob logs in
    client_bob = app.test_client()
    login_resp = post_200(client_bob, "/login", json={"name": "bob"})
    assert login_resp == {"status": "login succesful"}

    # Bob joins market
    post_200(client_bob, "/market/2/join")

    take_resp = post_200(client_bob, "/market/2/order/take/buy", json=dict(quantity=100, price=10.))
    assert take_resp == {"filled": 60}

    book_resp = get_200(client_bob, "/market/2/books")
    expected_book = {
        "buy": {
            "10.0": [
                {"filled": 100, "participant_id": "max", "price": 10., "quantity": 100, "side": True}
            ]
        },
        "sell": {}
    }
    assert book_resp == expected_book

    # Checking porfolios
    portfolio_max = get_200(client, "/market/2/portfolio")
    assert portfolio_max == {"assets": 60, "capital": -600.}
    
    portfolio_bob = get_200(client_bob, "/market/2/portfolio")
    assert portfolio_bob == {"assets": -60, "capital": 600.}

def login_test(name, client=None):
    if client is None:
        client = app.test_client()
    login_resp = post_200(client, "/login", json={"name": name})
    assert login_resp == {"status": "login succesful"}
    return client

def join_test(client, market_id):
    join_resp = post_200(client, f"/market/{market_id}/join")
    assert "market_values" in join_resp
    assert "hidden_value" in join_resp

def portfolio_test(client, market_id, expected_assets, expected_capital):
    portfolio = get_200(client, f"/market/{market_id}/portfolio")
    assert portfolio == {"assets": expected_assets, "capital": expected_capital}

def test_taking_price(client):
    post_200(client, "/markets/new", json=dict(name="2"))
    
    # Max logs in
    login_test("max", client)

    # Max joins the market
    join_test(client, "2")

    # Max tries to open his offers but gets an error
    open_error = post_200(client, "market/2/offers/set_open", json={"open": True})
    assert open_error == {"error": "bid and ask prices must be set before opening"}

    # Max sets his prices
    set_price_buy_resp = post_200(client, "market/2/offers/set/buy", json={"price": 10})
    assert set_price_buy_resp == {"status": "success"}

    set_price_sell_resp = post_200(client, "market/2/offers/set/sell", json={"price": 12})
    assert set_price_sell_resp == {"status": "success"}

    # Max opens his offers
    open_resp = post_200(client, "market/2/offers/set_open", json={"open": True})
    assert open_resp == {"status": "success"}

    # Bob logs in
    client_bob = login_test("bob")

    # Bob joins the market
    join_test(client_bob, "2")

    # Bob sets his prices
    set_price_buy_resp = post_200(client_bob, "market/2/offers/set/buy", json={"price": 8})
    set_price_sell_resp = post_200(client_bob, "market/2/offers/set/sell", json={"price": 15})

    # Bob opens his offers
    open_resp = post_200(client_bob, "market/2/offers/set_open", json={"open": True})
    assert open_resp == {"status": "success"}
    assert markets["2"].participants["bob"].open

    # Bob takes Max's sell price
    take_sell_resp = post_200(client_bob, "market/2/offers/take", json={"counterparty_id": "max", "price": 12, "side": Sides.SELL})
    assert take_sell_resp == {"status": "success"}

    # checking portfolios
    portfolio_test(client, "2", -1, 12)
    portfolio_test(client_bob, "2", 1, -12)


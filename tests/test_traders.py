from traders import __version__
from traders.app import app, USERS
from traders.market import markets

import pytest

@pytest.fixture(autouse=True)
def clear_users():
    USERS.clear()

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
    rv = client.post("/markets/new", data=dict(name="2"))
    assert rv.status_code == 200
    assert rv.get_json() == {"market_id": "2"}
    rv = client.get("/markets")
    assert rv.status_code == 200
    assert rv.get_json() == [initial_market, {"id": "2", "is_open": True}]

def test_login(client):
    resp = get_200(client, "/login")
    assert resp == {"logged_in": False}

    resp = post_200(client, "/login", data={"name": "max"})
    assert resp == {"status": "login succesful"}

    resp = get_200(client, "/login")
    assert resp == {"logged_in": True, "name": "max"}

def test_scenario(client):
    post_200(client, "/markets/new", data=dict(name="2"))
    
    # Max logs in
    login_resp = post_200(client, "/login", data={"name": "max"})
    assert login_resp == {"status": "login succesful"}

    # Max joins market 2
    join_resp = post_200(client, "/market/2/join")
    assert "market_values" in join_resp
    assert "hidden_value" in join_resp

    # Max checks his portfolio
    portfolio_resp = get_200(client, "/market/2/portfolio")
    assert portfolio_resp == {"assets": 0, "capital": 0}

    # Max posts buy order
    post_200(client, "/market/2/order/post/buy", data=dict(quantity=100, price=10))
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

    take_resp = post_200(client, "/market/2/order/take/sell", data=dict(quantity=50, price=10))
    assert take_resp == {"filled": 0}

    take_resp = post_200(client, "/market/2/order/take/buy", data=dict(quantity=40, price=10.))
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
    login_resp = post_200(client_bob, "/login", data={"name": "bob"})
    assert login_resp == {"status": "login succesful"}

    # Bob joins market
    post_200(client_bob, "/market/2/join")

    take_resp = post_200(client_bob, "/market/2/order/take/buy", data=dict(quantity=100, price=10.))
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

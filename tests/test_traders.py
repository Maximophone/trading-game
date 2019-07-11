from traders import __version__
from traders.app import app
from traders.market import markets

import pytest

@pytest.fixture
def client():
    app.config["TESTING"] = True
    client = app.test_client()
    return client

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

def test_scenario(client):
    post_200(client, "/markets/new", data=dict(name="2"))
    join_resp = post_200(client, "/market/2/join", data={"name":"max"})
    assert "market_values" in join_resp
    assert "hidden_value" in join_resp
    assert "token" in join_resp
    token = join_resp["token"]

    portfolio_resp = get_200(client, "/market/2/portfolio", data={"token":token})
    assert portfolio_resp == {"assets": 0, "capital": 0}

    post_200(client, "/market/2/order/post/buy", data=dict(quantity=100, price=10, token=token))
    book_resp = get_200(client, "/market/2/books", data=dict(token=token))

    expected_book = {
        "buy": {
            "10.0": [
                {"filled": 0, "participant_id": "max", "price": 10., "quantity": 100, "side": True}
            ]
        }, 
        "sell": {}
    }
    assert book_resp == expected_book

    take_resp = post_200(client, "/market/2/order/take/sell", data=dict(quantity=50, price=10, token=token))
    assert take_resp == {"filled": 0}

    take_resp = post_200(client, "/market/2/order/take/buy", data=dict(quantity=40, price=10., token=token))
    assert take_resp == {"filled": 40}

    # taking his own order
    book_resp = get_200(client, "/market/2/books", data=dict(token=token))
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
    portfolio = get_200(client, "/market/2/portfolio", data=dict(token=token))
    assert portfolio == {"assets": 0, "capital": 0.}

    # New participant joins
    join_resp_bob = post_200(client, "/market/2/join", data={"name": "bob"}, ip="bob")
    token_bob = join_resp_bob["token"]

    take_resp = post_200(client, "/market/2/order/take/buy", data=dict(quantity=100, price=10., token=token_bob))
    assert take_resp == {"filled": 60}

    book_resp = get_200(client, "/market/2/books", data=dict(token=token_bob))
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
    portfolio_max = get_200(client, "/market/2/portfolio", data=dict(token=token))
    assert portfolio_max == {"assets": 60, "capital": -600.}
    
    portfolio_bob = get_200(client, "/market/2/portfolio", data=dict(token=token_bob))
    assert portfolio_bob == {"assets": -60, "capital": 600.}

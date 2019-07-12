from flask import session, request, jsonify
from traders.market import markets


def error(message: str):
    return {
        "error": message
    }

def check_json_values(**form_values):
    def wrapper(f):
        def inner(*args, **kwargs):
            checked_form = dict(request.json)
            for arg, typ in form_values.items():
                arg_value = request.json.get(arg)
                if arg_value is None:
                    return jsonify(error(f"Parameter {arg} must be passed"))
                try:
                    checked_form[arg] = typ(arg_value)
                except ValueError:
                    return jsonify(error(f"Parameter {arg} type should be {typ} but got {type(arg_value)}"))


            request.getJson = lambda: checked_form
            return f(*args, **kwargs)
        inner.__name__ = f.__name__
        return inner
    return wrapper

def check_params(*param_types):
    def wrapper(f):
        def inner(*args, **kwargs):
            print(kwargs)
            new_kwargs = {}
            for (k, v), typ in zip(kwargs.items(), param_types):
                try:
                    new_kwargs[k] = typ(v)
                except ValueError:
                    return jsonify(error(f"Parameter {k} can't be casted to {typ}"))
            print(new_kwargs)
            return f(*args, **new_kwargs)
        inner.__name__ = f.__name__
        return inner
    return wrapper

def check_market(f):
    def inner(market_id, *args, **kwargs):
        if market_id not in markets:
            return jsonify(error(f"Can't find market with id {market_id}"))
        return f(market_id, *args, **kwargs)
    inner.__name__ = f.__name__
    return inner

def check_participant(f):
    def inner(market_id, *args, **kwargs):
        market = markets.get(market_id)
        user_id = session["user_id"]
        if user_id not in market.participants:
            return jsonify(error(f"User needs to join market first"))
        return f(market_id, *args, **kwargs)
    inner.__name__ = f.__name__
    return inner

def check_logged_in(f):
    def inner(*args, **kwargs):
        if "user_id" not in session:
            return jsonify(error("User needs to be logged in to access this service"))
        return f(*args, **kwargs)
    inner.__name__ = f.__name__
    return inner
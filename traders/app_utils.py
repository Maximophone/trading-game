from flask import request, jsonify
from traders.market import markets


def error(message: str):
    return {
        "error": message
    }

def check_form_values(**form_values):
    def wrapper(f):
        def inner(*args, **kwargs):
            checked_form = dict(request.form)
            for arg, typ in form_values.items():
                arg_value = request.form.get(arg)
                if arg_value is None:
                    return jsonify(error(f"Parameter {arg} must be passed"))
                try:
                    checked_form[arg] = typ(arg_value)
                except ValueError:
                    return jsonify(error(f"Parameter {arg} type should be {typ} but got {type(arg_value)}"))


            request.form = checked_form
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
        token = request.form.get("token")
        if token is None:
            return jsonify(error(f"User needs to pass authentication token"))
        if token not in market.token_id:
            return jsonify(error(f"Invalid token. Has user joined this market?"))
        return f(market_id, *args, **kwargs)
    inner.__name__ = f.__name__
    return inner
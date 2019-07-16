# Trading Game

A simple card game. Each player is given a hidden value from 1 to 100 and the market has an expanding list of public values. Players trade between each other for what they think is the average value.
Very beta...

**Play the game [here](http://35.197.192.156:5000/) !**

## Running the server

**Requirements**:
* poetry
* python 3.7

```bash
poetry install
make gen_secret
make run_prod
```

## Running the client

**Requirements**:
* nodejs

```bash
cd ui
echo '<server_host>:5001' > server_address.txt
make gen_server_address
make build_ui
make serve_ui
```

## Running the tests

```bash
poetry install
make test
```
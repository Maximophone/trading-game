import React, { Component } from "react";
import { PageHeader, ListGroup, ListGroupItem, Panel, Form, Checkbox, FormGroup, ControlLabel, FormControl } from "react-bootstrap"
import LoaderButton from "../components/LoaderButton";
import Slider from '@material-ui/core/Slider';
import Switch from '@material-ui/core/Switch';
import Grid from '@material-ui/core/Grid';
import { VictoryChart, VictoryScatter, VictoryTheme } from "victory"
import { get, post, is_float, Sides } from "../utils";
import "./Market.css"


export default class Market extends Component {
    constructor(props) {
        super(props);

        this.state = {
            name: "",
            participants: [],
            books: {},
            joined: false,
            is_joining: false,
            market_values: [],
            hidden_value: null,
            final_value: null,
            portfolio: null,
            participant: null,
            is_setting: false,
            open: null,
            price_setting: {
                sell_price: null,
                buy_price: null,
                open: false,
            }
        };
    }

    async componentDidMount() {
        this.refresh(
            () => {
                if (this.state.participant == null) { return; }
                this.setState({
                    price_setting: {
                        sell_price: this.state.participant.ask_price,
                        buy_price: this.state.participant.bid_price,
                        open: this.state.participant.open
                    }
                })
            }
        );
    }

    refresh = (callback) => {
        get(`market/${this.props.match.params.id}`, (data) => {
            if ("error" in data) {
                alert(data.error);
            } else {
                this.setState({
                    name: data.name,
                    participants: data.participants,
                    participant: data.participants.filter(p => p.id == this.props.user_name)[0],
                    books: data.books,
                    joined: data.joined,
                    market_values: data.market_values,
                    hidden_value: data.hidden_value,
                    final_value: data.final_value,
                    open: data.open,
                });
                if (data.joined) {
                    this.getPortfolio();
                }
                if (callback) {
                    callback();
                }
            }
        }, (error) => {
            alert(error);
        });
    }

    refresh_from_public_data = (data) => {
        var participant = data.participants.filter(p => p.id == this.props.user_name)[0];
        this.setState({
            name: data.name,
            participants: data.participants,
            books: data.books,
            market_values: data.market_values,
            open: data.open,
            participant: participant,
            portfolio: participant.portfolio,
        });
    }

    getPortfolio() {
        get(`market/${this.props.match.params.id}/portfolio`, (data) => {
            if ("error" in data) {
                alert(data.error);
            } else {
                this.setState({
                    portfolio: data
                });
            }
        }, (error) => {
            alert(error);
        });
    }

    handleJoin = async event => {
        event.preventDefault();
        this.setState({ is_joining: true })
        post(`market/${this.props.match.params.id}/join`, {}, (data) => {
            if ("error" in data) {
                alert(data.error);
                this.setState({ is_joining: false });
            } else {
                this.setState({
                    joined: true,
                    market_values: data.market_values,
                    hidden_value: data.hidden_value,
                    participants: data.participants,
                    participant: data.participants.filter(p => p.id == this.props.user_name)[0],
                });
                this.getPortfolio();
                this.props.socket.on("market_update_" + this.state.name, (data) => {
                    this.refresh_from_public_data(data);
                });
            }
        }, (error) => {
            alert(error);
            this.setState({ is_joining: false });
        });
    }

    render_join() {
        if (this.state.joined) {
            return;
        }
        return (
            <form onSubmit={this.handleJoin}>
                <LoaderButton
                    block
                    bsStyle="primary"
                    bsSize="large"
                    type="submit"
                    is_loading={this.state.is_joining}
                    text="Join Market"
                    loading_text="Joining..."
                />
            </form>
        )
    }

    handleSetPrices = event => {
        event.preventDefault();
        this.setState({ is_setting: true });
        post(`market/${this.props.match.params.id}/offers/set`, {
            sell_price: this.state.price_setting.sell_price,
            buy_price: this.state.price_setting.buy_price,
            is_open: this.state.price_setting.open
        }, (data) => {
            if ("error" in data) {
                alert(data.error);
            }
            this.setState({ is_setting: false });
            this.refresh();
        }, (error) => {
            alert(error);
            this.setState({ is_setting: false });
        });
    }

    handleOpen = event => {
        var price_setting = this.state.price_setting;
        price_setting.open = event.target.checked;
        this.setState({
            price_setting: price_setting
        });
        this.handleSetPrices(event);
    }

    handleSetPriceChangeSlider = (event, new_value) => {
        var price_setting = this.state.price_setting
        price_setting.buy_price = new_value[0] || 0
        price_setting.sell_price = new_value[1] || 0
        this.setState({
            price_setting: price_setting
        });
        this.handleSetPrices(event);
    }

    validatePrices() {
        var sell_price = this.state.price_setting.sell_price;
        var buy_price = this.state.price_setting.buy_price;
        return is_float(sell_price) && is_float(buy_price) && sell_price >= 0 && buy_price >= 0 && sell_price >= buy_price;
    }

    canTakePrices() {
        // TODO: check if participant is open as well
        return this.state.open;
    }

    handleTakePrice = event => {
        event.preventDefault();
        post(`market/${this.props.match.params.id}/offers/take`, {
            counterparty_id: event.target.attributes.counterparty_id.value,
            price: event.target.attributes.price.value,
            side: event.target.attributes.side.value == "buy" ? Sides.BUY : Sides.SELL,
        }, (data) => {
            if ("error" in data) {
                alert(data.error);
            }
            this.refresh();
        }, (error) => {
            alert(error);
        });
    }

    render_participant_item(participant) {
        if (this.state.open) {
            if (participant.open) {
                return (
                    <Form inline>
                        <p>Open to offers:
                        <FormGroup controlId="take_buy">
                                <ControlLabel>BID = ${participant.bid_price} </ControlLabel>
                                <LoaderButton
                                    inline
                                    bsSize="small"
                                    type="submit"
                                    disabled={!this.canTakePrices()}
                                    is_loading={false}
                                    text="Sell"
                                    loading_text="Selling..."
                                    onClick={this.handleTakePrice}
                                    counterparty_id={participant.id}
                                    side="buy"
                                    price={participant.bid_price}
                                />
                            </FormGroup>
                            <FormGroup controlId="take_sell">
                                <ControlLabel>ASK = ${participant.ask_price} </ControlLabel>
                                <LoaderButton
                                    inline
                                    bsSize="small"
                                    type="submit"
                                    disabled={!this.canTakePrices()}
                                    is_loading={false}
                                    text="Buy"
                                    loading_text="Buying..."
                                    onClick={this.handleTakePrice}
                                    counterparty_id={participant.id}
                                    side="sell"
                                    price={participant.ask_price}
                                />
                            </FormGroup>
                        </p>
                    </Form>
                )
            } else {
                return (
                    <p>Closed to offers.</p>
                )
            };
        } else {
            return (
                <p>Final Profits: ${participant.portfolio.capital}</p>
            )
        }
    }

    render_participants_list(participants) {
        return participants.map(
            (participant, i) =>
                <ListGroupItem header={participant.name} key={i}>
                    {this.render_participant_item(participant)}
                </ListGroupItem>
        );
    }

    render_set_prices() {
        if (!this.state.joined || !this.state.open) {
            return;
        }
        return (
            <div className="price_setting">
                <Form inline onSubmit={this.handleSetPrices}>
                    <Slider
                        value={[this.state.price_setting.buy_price, this.state.price_setting.sell_price]}
                        onChange={this.handleSetPriceChangeSlider}
                        valueLabelDisplay="auto"
                        aria-labelledby="range-slider"
                        marks={[
                            { value: this.state.participant.bid_price, label: "buy" },
                            { value: this.state.participant.ask_price, label: "sell" }
                        ]}
                    />
                    {"  "}
                    <Grid component="label" container alignItems="center" spacing={1}>
                        <Grid item>Closed</Grid>
                        <Grid item>
                            <Switch
                                inline
                                checked={this.state.price_setting.open}
                                disabled={!this.validatePrices()}
                                onChange={this.handleOpen}
                            />
                        </Grid>
                        <Grid item>Open</Grid>
                    </Grid>

                </Form>
                <br />
            </div>
        )
    }

    render_values() {
        if (!this.state.joined) {
            return;
        }
        return (
            <div className="values">
                <div className="market_values">
                    <Panel>
                        <ListGroup variant="flush">
                            <ListGroupItem><h4>Public Values</h4></ListGroupItem>
                            {this.state.market_values.map(
                                (value, i) => <ListGroupItem key={i}> {value} </ListGroupItem>
                            )}
                        </ListGroup>
                    </Panel>
                </div>
                <div className="hidden_value">
                    <Panel>
                        <ListGroup variant="flush">
                            <ListGroupItem key="title"><h4>Hidden Value</h4></ListGroupItem>
                            <ListGroupItem key="value">{this.state.hidden_value}</ListGroupItem>
                        </ListGroup>
                    </Panel>
                </div>
                {this.render_final_value()}
            </div>
        );
    }

    render_final_value() {
        if (this.state.open) {
            return;
        }
        return (
            <div className="final_value">
                <Panel>
                    <ListGroup variant="flush">
                        <ListGroupItem key="title"><h4>Final Value</h4></ListGroupItem>
                        <ListGroupItem key="value"><b>{this.state.final_value}</b></ListGroupItem>
                    </ListGroup>
                </Panel>
            </div>
        )
    }

    render_portfolio() {
        if (!this.state.joined) {
            return;
        }
        if (!this.state.portfolio) {
            return;
        }
        return (
            <div className="portfolio">
                <Panel>
                    <ListGroup variant="flush">
                        <ListGroupItem key="title"><h4>Your Portfolio</h4></ListGroupItem>
                        <ListGroupItem key="assets"><b>Assets: </b>{this.state.portfolio.assets}</ListGroupItem>
                        <ListGroupItem key="capital"><b>Capital: </b>${this.state.portfolio.capital}</ListGroupItem>
                    </ListGroup>
                </Panel>
            </div>
        )
    }

    render_history() {
        if (!this.state.joined) {
            return;
        }
        /*         return (
                    <VictoryChart
                        theme={VictoryTheme.material}
                        height={150}
                        domain={{ x: [0, 5], y: [0, 100] }}
                        >
                        <VictoryScatter
                            style={{ data: { fill: "#c43a31" } }}
                            size={1}
                            data={[
                            { x: 1, y: 2 },
                            { x: 2, y: 3 },
                            { x: 3, y: 5 },
                            { x: 4, y: 4 }, 
                            { x: 5, y: 7 }
                            ]}
                        />
                        </VictoryChart>
                ) */
    }

    render() {
        return <div className="Market">
            <PageHeader>{this.state.name} - {this.state.open ? "Open" : "Closed"} <LoaderButton
                inline
                bsSize="small"
                type="submit"
                disabled={!this.state.open}
                is_loading={false}
                text="Refresh"
                loading_text="Refreshing..."
                onClick={this.refresh}
            /></PageHeader>
            {this.render_history()}
            <h3>Participants</h3>
            <ListGroup>
                {this.render_participants_list(this.state.participants)}
            </ListGroup>
            {this.render_set_prices()}
            {this.render_join()}
            {this.render_values()}
            {this.render_portfolio()}
        </div>;
    }
}

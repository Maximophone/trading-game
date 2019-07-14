import React, { Component } from "react";
import { PageHeader, ListGroup, ListGroupItem, Panel, Form, Checkbox, FormGroup, ControlLabel, FormControl} from "react-bootstrap"
import LoaderButton from "../components/LoaderButton";
import { get, post, is_float } from "../utils";
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
            portfolio: null,
            is_setting: false,
            price_setting: {
                sell_price: null,
                buy_price: null,
                open: false,
            }
        };
    }

    async componentDidMount(){
        console.log("mounted")
        this.refresh();
    }

    refresh(){
        get(`market/${this.props.match.params.id}`, (data) => {
            if("error" in data){
                alert(data.error);
            } else {
                this.setState({
                    name: data.name,
                    participants: data.participants,
                    books: data.books,
                    joined: data.joined,
                    market_values: data.market_values,
                    hidden_value: data.hidden_value,
                });
                if(data.joined){
                    this.getPortfolio();
                }
            }
        }, (error) => {
            alert(error);
        });
    }

    getPortfolio(){
        get(`market/${this.props.match.params.id}/portfolio`, (data) => {
            if("error" in data){
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

    render_participant_item(participant){
        if(participant.open){
            return (
                `Open to offers: BID=${participant.bid_price} ASK=${participant.ask_price}`
            )
        } else {
            return (
                `Closed to offers.`
            )
        };
    }

    render_participants_list(participants){
        return participants.map(
            (participant, i) => 
                <ListGroupItem header={participant.name} key={i}>
                    { this.render_participant_item(participant) }
                </ListGroupItem>
        );
    }

    handleJoin = async event => {
        event.preventDefault();
        this.setState({is_joining: true})
        post(`market/${this.props.match.params.id}/join`, {}, (data) => {
            if("error" in data){
                alert(data.error);
                this.setState({ is_joining: false}); 
            } else {
                this.setState({ 
                    joined: true,
                    market_values: data.market_values,
                    hidden_value: data.hidden_value,
                    participants: data.participants
                });
                this.getPortfolio();
            }
        }, (error) => {
            alert(error);
            this.setState({ is_joining: false });
        });
    }

    render_join(){
        if(this.state.joined){
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
        this.setState({is_setting: true});
        post(`market/${this.props.match.params.id}/offers/set`, {
            sell_price: this.state.price_setting.sell_price,
            buy_price: this.state.price_setting.buy_price,
            is_open: this.state.price_setting.open
        }, (data) => {
            if("error" in data){
                alert(data.error);
            }
            this.setState({is_setting: false});
            this.refresh();
        }, (error) => {
            alert(error);
            this.setState({is_setting: false});
        });
    }

    handleSetPriceChange = event => {
        var price_setting = this.state.price_setting
        if(event.target.id == "buy_price"){
            price_setting.buy_price = parseFloat(event.target.value) || 0;
        } else if (event.target.id == "sell_price"){
            price_setting.sell_price = parseFloat(event.target.value) || 0;
        } else {
            price_setting.open = event.target.checked;
        }
        this.setState({
            price_setting: price_setting
        });
    }

    validatePrices(){
        var sell_price = this.state.price_setting.sell_price;
        var buy_price = this.state.price_setting.buy_price;
        return is_float(sell_price) && is_float(buy_price) && sell_price >= 0 && buy_price >= 0 && sell_price >= buy_price;
    }

    render_set_prices(){
        if(!this.state.joined){
            return;
        }
        return (
            <Form inline onSubmit={this.handleSetPrices}>
                <FormGroup controlId="sell_price">
                    <ControlLabel>Sell Price</ControlLabel>
                    <FormControl
                        onChange={this.handleSetPriceChange}
                        value={this.state.price_setting.sell_price}
                        componentClass="input"
                    />
                </FormGroup>
                {"  "}
                <FormGroup controlId="buy_price">
                    <ControlLabel>Buy Price</ControlLabel>
                    <FormControl
                        onChange={this.handleSetPriceChange}
                        value={this.state.price_setting.buy_price}
                        componentClass="input"
                    />
                </FormGroup>
                {"  "}
                <FormGroup controlId="price_open">
                    <Checkbox 
                        name="test"
                        checked={this.state.price_setting.open}
                        onChange={this.handleSetPriceChange}
                        >Open</Checkbox>
                </FormGroup>
                <LoaderButton
                    inline
                    bsStyle="primary"
                    bsSize="small"
                    type="submit"
                    disabled={!this.validatePrices()}
                    is_loading={this.state.is_setting}
                    text="Set Your Prices"
                    loading_text="Setting..."
                />
            </Form>
        )
    }

    render_values(){
        if(!this.state.joined){
            return;
        }
        return (
            <div className="values">
                <div className="market_values">
                    <Panel>
                        <ListGroup variant="flush">
                            <ListGroupItem><h4>Public Values</h4></ListGroupItem>
                            { this.state.market_values.map(
                                (value, i) => <ListGroupItem key={i}> {value} </ListGroupItem>
                            ) }
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
            </div>
        );
    }

    render_portfolio(){
        if(!this.state.joined){
            return;
        }
        if(!this.state.portfolio){
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

    render(){
        return <div className="Market">
            <PageHeader>{this.state.name}</PageHeader>
            <h3>Participants</h3>
            <ListGroup>
                { this.render_participants_list(this.state.participants)}
            </ListGroup>
            { this.render_set_prices() }
            { this.render_join() }
            { this.render_values() }
            { this.render_portfolio() }
        </div>;
    }
}

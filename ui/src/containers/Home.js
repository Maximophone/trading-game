import React, { Component } from "react";
import { PageHeader, ListGroup, ListGroupItem } from "react-bootstrap"
import { LinkContainer } from "react-router-bootstrap"
import { get } from "../utils"
import "./Home.css";

export default class Home extends Component {
  constructor(props){
    super(props);

    this.state = {
      is_loading: true,
      markets: []
    };
  }

  async componentDidMount() {
    get("markets", (markets) => {
      this.setState({ 
        markets: markets,
        is_loading: false
      });
    }, (error) => {
      alert(error);
      this.setState({is_loading: false});
    });
  }

  render_market_list(markets){
    return [{}].concat(markets).map(
      (market, i) => 
        i != 0
          ? <LinkContainer
              key={market.id}
              to={`/market/${market.id}`}
              >
                <ListGroupItem header={market.id}>
                  {market.is_open?"Open":"Closed"}
                </ListGroupItem>
              </LinkContainer>
          : <LinkContainer
              key="new"
              to="/markets/new"
              >
                <ListGroupItem>
                  <h4>
                    <b>{"\uFF0B"}</b> Create a new market
                  </h4>
                </ListGroupItem>
          </LinkContainer>
      
    );
  }

  render_lander(){
    return (
      <div className="lander">
        <h1>Traders</h1>
        <p>A Trading Card Game</p>
      </div>
    );
  }

  render_markets(){
    return (
      <div className="markets">
        <PageHeader>Markets</PageHeader>
        <ListGroup>
          {!this.state.is_loading && this.render_market_list(this.state.markets)}
        </ListGroup>
      </div>
    )
  }
  render() {
    return (
      <div className="Home">
        {this.props.is_logged_in ? this.render_markets() : this.render_lander()}
      </div>
    );
  }
}
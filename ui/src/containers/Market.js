import React, { Component } from "react";
import { PageHeader, ListGroup, ListGroupItem, Panel } from "react-bootstrap"
import LoaderButton from "../components/LoaderButton";
import { get, post } from "../utils";


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
        };
    }

    async componentDidMount(){
        console.log("mounted")
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
                <ListGroupItem header={participant.name}>
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
                                (value, i) => <ListGroupItem> {value} </ListGroupItem>
                            ) }
                        </ListGroup>
                    </Panel>
                </div>
                <div className="hidden_value">
                    <Panel>
                        <ListGroup variant="flush">
                            <ListGroupItem><h4>Hidden Value</h4></ListGroupItem>
                            <ListGroupItem>{this.state.hidden_value}</ListGroupItem>
                        </ListGroup>
                    </Panel>
                </div>
            </div>
        );
    }

    render(){
        return <div className="Market">
            <PageHeader>{this.state.name}</PageHeader>
            <h3>Participants</h3>
            <ListGroup>
                { this.render_participants_list(this.state.participants)}
            </ListGroup>
            { this.render_join() }
            { this.render_values() }
        </div>;
    }
}

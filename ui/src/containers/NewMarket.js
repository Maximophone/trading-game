import React, { Component } from "react"
import { FormGroup, FormControl, ControlLabel } from "react-bootstrap";
import Slider from '@material-ui/core/Slider';
import LoaderButton from "../components/LoaderButton";
import { post } from "../utils";
import "./NewMarket.css";

export default class NewMarket extends Component {
    constructor(props){
        super(props);

        this.state = {
            is_loading: null,
            market_name: "",
            n_periods: 5,
            period_time: 60,
            bots: 0,
        };
    }

    validateForm(){
        return this.state.market_name.length > 0 && this.state.n_periods > 0 && this.state.period_time > 1 && this.state.n_periods*this.state.period_time < 3600;
    }

    handleChange = event => {
        this.setState({
            [event.target.id]: event.target.value
        });
    }

    handleChangeBots = (event, new_value) => {
        this.setState({
            bots: new_value
        });
    }

    handleSubmit = async event => {
        event.preventDefault();
        this.setState({is_loading: true})
        post("markets/new", {
            name: this.state.market_name,
            bots: this.state.bots,
            n_periods: this.state.n_periods,
            period_time: this.state.period_time,
        }, (data) => {
            if("error" in data){
                alert(data.error);
                this.setState({ is_loading: false}); 
            } else {
                this.props.history.push("/");
            }
        }, (error) => {
            alert(error);
            this.setState({ is_loading: false });
        });
    }

    render(){
        return (
            <div className="NewMarket">
                <form onSubmit={this.handleSubmit}>
                    <FormGroup controlId="market_name">
                        <ControlLabel>Market Name</ControlLabel>
                        <FormControl
                            onChange={this.handleChange}
                            value={this.state.market_name}
                            componentClass="input"
                            type="text"
                        />
                    </FormGroup>
                    <FormGroup controlId="n_periods">
                        <ControlLabel>Number of Stages</ControlLabel>
                        <FormControl
                            onChange={this.handleChange}
                            value={this.state.n_periods}
                            componentClass="input"
                            type="number"
                        />
                    </FormGroup>
                    <FormGroup controlId="period_time">
                        <ControlLabel>Time per Stage</ControlLabel>
                        <FormControl
                            onChange={this.handleChange}
                            value={this.state.period_time}
                            componentClass="input"
                            type="number"
                        />
                    </FormGroup>
                    <FormGroup controlId="bots">
                        <ControlLabel>Bots</ControlLabel>
                        <Slider
                            value={this.state.bots}
                            onChange={this.handleChangeBots}
                            valueLabelDisplay="auto"
                            aria-labelledby="discrete-slider"
                            min={0}
                            max={10}
                            marks
                        />
                    </FormGroup>
                    <LoaderButton
                        block
                        bsStyle="primary"
                        bsSize="large"
                        disabled={!this.validateForm()}
                        type="submit"
                        is_loading={this.state.is_loading}
                        text="Create"
                        loading_text="Creating..."
                    />
                </form>
            </div>
        );
    }
}
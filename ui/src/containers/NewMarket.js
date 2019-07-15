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
            bots: 0,
        };
    }

    validateForm(){
        return this.state.market_name.length > 0;
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
                            componentClass="textarea"
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
import React, { Component } from "react"
import { FormGroup, FormControl } from "react-bootstrap";
import LoaderButton from "../components/LoaderButton";
import { post } from "../utils";
import "./NewMarket.css";

export default class NewMarket extends Component {
    constructor(props){
        super(props);

        this.state = {
            is_loading: null,
            market_name: ""
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

    handleSubmit = async event => {
        event.preventDefault();
        this.setState({is_loading: true})
        post("markets/new", {name: this.state.market_name}, (data) => {
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
                        <FormControl
                            onChange={this.handleChange}
                            value={this.state.market_name}
                            componentClass="textarea"
                        />
                    </FormGroup>
                    <LoaderButton
                        block
                        bsStyle="primary"
                        bsSize="large"
                        disable={!this.validateForm()}
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
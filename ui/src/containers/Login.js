import React, { Component } from "react";
import { FormGroup, FormControl, ControlLabel } from "react-bootstrap";
import { post } from "../utils"
import "./Login.css";
import LoaderButton from "../components/LoaderButton";

export default class Login extends Component {
  constructor(props) {
    super(props);

    this.state = {
      user_name: "",
      is_loading: false,
    };
  }

  validateForm() {
    return this.state.user_name.length > 0;
  }

  handleChange = event => {
    this.setState({
      [event.target.id]: event.target.value
    });
  }

  handleSubmit = event => {
    event.preventDefault();
    this.setState({is_loading: true});
    post("http://localhost:5000/login", {
      name: this.state.user_name
    }, (resp) => {
      if(resp.status === "login succesful"){
        this.props.user_has_logged_in(true, this.state.user_name);
        this.props.history.push("/");
      } else {
        alert(resp.error);
        this.setState({is_loading: false});
      }
    }, (error) => {
      console.error(error);
    })
  }

  render() {
    return (
      <div className="Login">
        <form onSubmit={this.handleSubmit}>
          <FormGroup controlId="user_name" bsSize="large">
            <ControlLabel>User Name</ControlLabel>
            <FormControl
              autoFocus
              type="user_name"
              value={this.state.user_name}
              onChange={this.handleChange}
            />
          </FormGroup>
          <LoaderButton
            block
            bsSize="large"
            disabled={!this.validateForm()}
            type="submit"
            is_loading={this.state.is_loading}
            text="Login"
            loading_text="Logging in..."
            />
        </form>
      </div>
    );
  }
}
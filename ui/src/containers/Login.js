import React, { Component } from "react";
import { Button, FormGroup, FormControl, ControlLabel } from "react-bootstrap";
import "./Login.css";

export default class Login extends Component {
  constructor(props) {
    super(props);

    this.state = {
      user_name: "",
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
    fetch("http://localhost:5000/login", {
        method:"POST",
        headers: {
            'Accept': 'application/json',
            'Content-Type': 'application/json',
          },
        body: JSON.stringify({
            name: this.state.user_name
        })
    }).then((response) => response.json())
    .then((data) => {
        if(data.status === "login succesful"){
            this.props.userHasLoggedIn(true);
        } else {
            alert(data.error);
        }
    }).catch((error) => {console.error(error);});
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
          <Button
            block
            bsSize="large"
            disabled={!this.validateForm()}
            type="submit"
          >
            Login
          </Button>
        </form>
      </div>
    );
  }
}
import React, { Component } from "react";
import { Link } from "react-router-dom";
import { Navbar, Nav, NavItem } from "react-bootstrap";
import { LinkContainer } from "react-router-bootstrap";
import Routes from "./Routes";
import {get} from "./utils";
import "./App.css";

class App extends Component {
  constructor(props) {
    super(props);
  
    this.state = {
      is_logged_in: false,
      is_logging_in: true,
      user_name: "",
    };
  }

  async componentDidMount(){
    get("http://localhost:5000/login", (data) => {
      this.user_has_logged_in(data.logged_in, data.name)
    }, (error) => {
      console.error(error);
    });
    this.setState({is_logging_in: false});
  }

  user_has_logged_in = (logged_in, name) => {
    this.setState({ 
      is_logged_in: logged_in,
      user_name: name
     });
  }

  render() {
    const child_props = {
      is_logged_in: this.state.is_logged_in,
      user_has_logged_in: this.user_has_logged_in,
    }
    return (
      !this.state.is_logging_in &&
      <div className="App container">
        <Navbar fluid collapseOnSelect>
          <Navbar.Header>
            <Navbar.Brand>
              <Link to="/">Traders</Link>
            </Navbar.Brand>
            <Navbar.Toggle />
          </Navbar.Header>
          <Navbar.Collapse>
            <Nav pullRight>
              {this.state.is_logged_in?<Navbar.Text>Logged in as {this.state.user_name}</Navbar.Text>:
              <LinkContainer to="/login">
                <NavItem href="/login">Login</NavItem>
              </LinkContainer>
              }
            </Nav>
          </Navbar.Collapse>
        </Navbar>
        <Routes child_props={child_props}/>
      </div>
    );
  }
}

export default App;



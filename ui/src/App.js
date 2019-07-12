import React, { Component } from "react";
import { Link } from "react-router-dom";
import { Navbar, Nav, NavItem } from "react-bootstrap";
import { LinkContainer } from "react-router-bootstrap";
import Routes from "./Routes";
import "./App.css";

class App extends Component {
  constructor(props) {
    super(props);
  
    this.state = {
      is_logged_in: false
    };
  }

  user_has_logged_in = logged_in => {
    this.setState({ is_logged_in: logged_in });
  }

  render() {
    const child_props = {
      is_logged_in: this,
      user_has_authenticated: this.user_has_authenticated
    }
    return (
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
              <LinkContainer to="/login">
                <NavItem href="/login">Login</NavItem>
              </LinkContainer>
            </Nav>
          </Navbar.Collapse>
        </Navbar>
        <Routes child_props={child_props}/>
      </div>
    );
  }
}

export default App;



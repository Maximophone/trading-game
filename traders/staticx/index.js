var Form = ReactBootstrap.Form;
var Button = ReactBootstrap.Button;

class App extends React.Component {
    constructor(props){
        super(props);
        this.state = {
            logged_in: false,
        };
        $.get("/login", data => {
            if(data.logged_in){
                this.onLogin();
            }
        })
    }

    onLogin = () => {
        this.setState({
            logged_in: true,
        });
    }

    render() {
        if(this.state.logged_in){
            return (
                <h2>Welcome</h2>
            )
        } else {
            return (
                <Login onLogin={this.onLogin}/>
            )
        }
    }
}

class Login extends React.Component {
    constructor(props) {
      super(props);

      this.state = {
        user_name: ""
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
      $.post("/login", {name: this.state.user_name}, (data) => {
          if(data.status == "login succesful"){
            this.props.onLogin();
          } else {
            console.log(data);
          }
      })
      
    }

    render() {
      return (
        <div className="Login">
          <Form onSubmit={this.handleSubmit}>
            <Form.Group controlId="user_name" bsSize="large">
              <Form.Control
                autoFocus
                type="user_name"
                value={this.state.user_name}
                onChange={this.handleChange}
              />
            </Form.Group>
            <Button
              block
              bsSize="small"
              disabled={!this.validateForm()}
              type="submit"
            >
              Login
            </Button>
          </Form>
        </div>
      );
    }
  }

ReactDOM.render(
    <App/>,
    document.getElementById('root')
);
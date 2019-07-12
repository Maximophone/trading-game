var _createClass = function () { function defineProperties(target, props) { for (var i = 0; i < props.length; i++) { var descriptor = props[i]; descriptor.enumerable = descriptor.enumerable || false; descriptor.configurable = true; if ("value" in descriptor) descriptor.writable = true; Object.defineProperty(target, descriptor.key, descriptor); } } return function (Constructor, protoProps, staticProps) { if (protoProps) defineProperties(Constructor.prototype, protoProps); if (staticProps) defineProperties(Constructor, staticProps); return Constructor; }; }();

function _defineProperty(obj, key, value) { if (key in obj) { Object.defineProperty(obj, key, { value: value, enumerable: true, configurable: true, writable: true }); } else { obj[key] = value; } return obj; }

function _classCallCheck(instance, Constructor) { if (!(instance instanceof Constructor)) { throw new TypeError("Cannot call a class as a function"); } }

function _possibleConstructorReturn(self, call) { if (!self) { throw new ReferenceError("this hasn't been initialised - super() hasn't been called"); } return call && (typeof call === "object" || typeof call === "function") ? call : self; }

function _inherits(subClass, superClass) { if (typeof superClass !== "function" && superClass !== null) { throw new TypeError("Super expression must either be null or a function, not " + typeof superClass); } subClass.prototype = Object.create(superClass && superClass.prototype, { constructor: { value: subClass, enumerable: false, writable: true, configurable: true } }); if (superClass) Object.setPrototypeOf ? Object.setPrototypeOf(subClass, superClass) : subClass.__proto__ = superClass; }

var Form = ReactBootstrap.Form;
var Button = ReactBootstrap.Button;

var App = function (_React$Component) {
  _inherits(App, _React$Component);

  function App(props) {
    _classCallCheck(this, App);

    var _this = _possibleConstructorReturn(this, (App.__proto__ || Object.getPrototypeOf(App)).call(this, props));

    _this.onLogin = function () {
      _this.setState({
        logged_in: true
      });
    };

    _this.state = {
      logged_in: false
    };
    $.get("/login", function (data) {
      if (data.logged_in) {
        _this.onLogin();
      }
    });
    return _this;
  }

  _createClass(App, [{
    key: "render",
    value: function render() {
      if (this.state.logged_in) {
        return React.createElement(
          "h2",
          null,
          "Welcome"
        );
      } else {
        return React.createElement(Login, { onLogin: this.onLogin });
      }
    }
  }]);

  return App;
}(React.Component);

var Login = function (_React$Component2) {
  _inherits(Login, _React$Component2);

  function Login(props) {
    _classCallCheck(this, Login);

    var _this2 = _possibleConstructorReturn(this, (Login.__proto__ || Object.getPrototypeOf(Login)).call(this, props));

    _this2.handleChange = function (event) {
      _this2.setState(_defineProperty({}, event.target.id, event.target.value));
    };

    _this2.handleSubmit = function (event) {
      event.preventDefault();
      $.post("/login", { name: _this2.state.user_name }, function (data) {
        if (data.status == "login succesful") {
          _this2.props.onLogin();
        } else {
          console.log(data);
        }
      });
    };

    _this2.state = {
      user_name: ""
    };
    return _this2;
  }

  _createClass(Login, [{
    key: "validateForm",
    value: function validateForm() {
      return this.state.user_name.length > 0;
    }
  }, {
    key: "render",
    value: function render() {
      return React.createElement(
        "div",
        { className: "Login" },
        React.createElement(
          Form,
          { onSubmit: this.handleSubmit },
          React.createElement(
            Form.Group,
            { controlId: "user_name", bsSize: "large" },
            React.createElement(Form.Control, {
              autoFocus: true,
              type: "user_name",
              value: this.state.user_name,
              onChange: this.handleChange
            })
          ),
          React.createElement(
            Button,
            {
              block: true,
              bsSize: "small",
              disabled: !this.validateForm(),
              type: "submit"
            },
            "Login"
          )
        )
      );
    }
  }]);

  return Login;
}(React.Component);

ReactDOM.render(React.createElement(App, null), document.getElementById('root'));
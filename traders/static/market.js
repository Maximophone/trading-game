var _slicedToArray = function () { function sliceIterator(arr, i) { var _arr = []; var _n = true; var _d = false; var _e = undefined; try { for (var _i = arr[Symbol.iterator](), _s; !(_n = (_s = _i.next()).done); _n = true) { _arr.push(_s.value); if (i && _arr.length === i) break; } } catch (err) { _d = true; _e = err; } finally { try { if (!_n && _i["return"]) _i["return"](); } finally { if (_d) throw _e; } } return _arr; } return function (arr, i) { if (Array.isArray(arr)) { return arr; } else if (Symbol.iterator in Object(arr)) { return sliceIterator(arr, i); } else { throw new TypeError("Invalid attempt to destructure non-iterable instance"); } }; }();

var _createClass = function () { function defineProperties(target, props) { for (var i = 0; i < props.length; i++) { var descriptor = props[i]; descriptor.enumerable = descriptor.enumerable || false; descriptor.configurable = true; if ("value" in descriptor) descriptor.writable = true; Object.defineProperty(target, descriptor.key, descriptor); } } return function (Constructor, protoProps, staticProps) { if (protoProps) defineProperties(Constructor.prototype, protoProps); if (staticProps) defineProperties(Constructor, staticProps); return Constructor; }; }();

function _classCallCheck(instance, Constructor) { if (!(instance instanceof Constructor)) { throw new TypeError("Cannot call a class as a function"); } }

function _possibleConstructorReturn(self, call) { if (!self) { throw new ReferenceError("this hasn't been initialised - super() hasn't been called"); } return call && (typeof call === "object" || typeof call === "function") ? call : self; }

function _inherits(subClass, superClass) { if (typeof superClass !== "function" && superClass !== null) { throw new TypeError("Super expression must either be null or a function, not " + typeof superClass); } subClass.prototype = Object.create(superClass && superClass.prototype, { constructor: { value: subClass, enumerable: false, writable: true, configurable: true } }); if (superClass) Object.setPrototypeOf ? Object.setPrototypeOf(subClass, superClass) : subClass.__proto__ = superClass; }

var Market = function (_React$Component) {
    _inherits(Market, _React$Component);

    function Market(props) {
        _classCallCheck(this, Market);

        var _this = _possibleConstructorReturn(this, (Market.__proto__ || Object.getPrototypeOf(Market)).call(this, props));

        _this.state = {
            "book_buy": {},
            "book_sell": {}
        };
        $.get("/market/" + _this.props.market_id + "/books", function (books) {
            _this.setState({ "book_buy": books.buy, "book_sell": books.sell });
        });
        return _this;
    }

    _createClass(Market, [{
        key: "render",
        value: function render() {
            return React.createElement(
                "div",
                { className: "market" },
                React.createElement(
                    "h1",
                    null,
                    "Market ",
                    this.props.market_id
                ),
                React.createElement(Book, { side: "buy", value: this.state.book_buy }),
                React.createElement(Book, { side: "sell", value: this.state.book_sell })
            );
        }
    }]);

    return Market;
}(React.Component);

var Book = function (_React$Component2) {
    _inherits(Book, _React$Component2);

    function Book() {
        _classCallCheck(this, Book);

        return _possibleConstructorReturn(this, (Book.__proto__ || Object.getPrototypeOf(Book)).apply(this, arguments));
    }

    _createClass(Book, [{
        key: "render",
        value: function render() {
            price_levels = [];
            Object.entries(this.props.value).map(function (_ref, _) {
                var _ref2 = _slicedToArray(_ref, 2),
                    price = _ref2[0],
                    orders = _ref2[1];

                price_levels.push(React.createElement(
                    "li",
                    { className: "price-level" },
                    React.createElement(
                        "p",
                        null,
                        price
                    ),
                    React.createElement(Orders, { value: orders })
                ));
            });
            return React.createElement(
                "div",
                { className: "book-list" },
                React.createElement(
                    "h2",
                    null,
                    this.props.side,
                    " Orders"
                ),
                React.createElement(
                    "ul",
                    null,
                    price_levels
                )
            );
        }
    }]);

    return Book;
}(React.Component);

var Orders = function (_React$Component3) {
    _inherits(Orders, _React$Component3);

    function Orders() {
        _classCallCheck(this, Orders);

        return _possibleConstructorReturn(this, (Orders.__proto__ || Object.getPrototypeOf(Orders)).apply(this, arguments));
    }

    _createClass(Orders, [{
        key: "render",
        value: function render() {
            orders_list = [];
            this.props.value.map(function (order) {
                orders_list.push(React.createElement(
                    "li",
                    null,
                    React.createElement(Order, { quantity: order.quantity, filled: order.filled, participant: order.participant_id })
                ));
            });
            return React.createElement(
                "ul",
                null,
                orders_list
            );
        }
    }]);

    return Orders;
}(React.Component);

var Order = function (_React$Component4) {
    _inherits(Order, _React$Component4);

    function Order() {
        _classCallCheck(this, Order);

        return _possibleConstructorReturn(this, (Order.__proto__ || Object.getPrototypeOf(Order)).apply(this, arguments));
    }

    _createClass(Order, [{
        key: "render",
        value: function render() {
            return React.createElement(
                "p",
                null,
                "Quantity: ",
                this.props.quantity,
                " Filled: ",
                this.props.filled,
                " Participant: ",
                this.props.participant
            );
        }
    }]);

    return Order;
}(React.Component);

ReactDOM.render(React.createElement(Market, { market_id: market_id }), document.getElementById('root'));
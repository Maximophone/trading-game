class Market extends React.Component {
    constructor(props){
        super(props);
        this.state = {
            "book_buy": {},
            "book_sell": {},
        };
        $.get("/market/" + this.props.market_id + "/books", books =>{
            this.setState({"book_buy": books.buy, "book_sell": books.sell});
        })
    }
    render(){
        return (
            <div className="market">
                <h1>Market {this.props.market_id}</h1>
                <Book side="buy" value={this.state.book_buy}/>
                <Book side="sell" value={this.state.book_sell}/>
            </div>
        )
    }
}

class Book extends React.Component {
    render(){
        price_levels = [];
        Object.entries(this.props.value).map(([price, orders], _) => {
            price_levels.push(<li className="price-level">
                <p>{price}</p>
                <Orders value={orders}/>
                </li>);
        })
        return (
            <div className="book-list">
                <h2>{this.props.side} Orders</h2>
                <ul>
                    {price_levels}
                </ul>
            </div>
        )
    }
}

class Orders extends React.Component {
    render(){
        orders_list = [];
        this.props.value.map(order => {
            orders_list.push(<li><Order quantity={order.quantity} filled={order.filled} participant={order.participant_id}/></li>);
        })
        return (
            <ul>{orders_list}</ul>
        )
    }
}

class Order extends React.Component {
    render(){
        return (
            <p>Quantity: {this.props.quantity} Filled: {this.props.filled} Participant: {this.props.participant}</p>
        )
    }
}

ReactDOM.render(
    <Market market_id={market_id}/>,
    document.getElementById('root')
);
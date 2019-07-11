show_book = function(books, side){
    prices_list = $("ul#"+side);
    for(var [price, orders] of Object.entries(books[side])){
        var price_li = $("<li/>").addClass(side).appendTo(prices_list);
        var price_content = $("<p/>").addClass(side + "-price").text(price).appendTo(price_li);
        var orders_list = $("<ul/>").addClass(side + "-price-orders").appendTo(price_li);
        for(var order of orders){
            var order_li = $("<li/>").addClass(side + "-price-order").appendTo(orders_list);
            var order_content = $("<p/>").addClass(side + "-price-order-content").text(`${order.quantity - order.filled} - ${order.participant_id}`).appendTo(order_li);
        }
    }
}

response = $.get("/market/" + market_id + "/books", books => {
    show_book(books, "buy");
    show_book(books, "sell");
});


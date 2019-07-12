import React from "react";
import { Route } from "react-router-dom";
import { SSL_OP_CRYPTOPRO_TLSEXT_BUG } from "constants";

export default ({ component: C, props: cProps, ...rest}) =>
    <Route {...rest} render={props => <C {...props} {...cProps} />} />;
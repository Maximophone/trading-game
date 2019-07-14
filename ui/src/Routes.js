import React from "react";
import { Route, Switch } from "react-router-dom";
import AppliedRoute from "./components/AppliedRoute";
import Home from "./containers/Home";
import NotFound from "./containers/NotFound";
import Login from "./containers/Login";
import NewMarket from "./containers/NewMarket";


export default ({ child_props }) =>
  <Switch>
    <AppliedRoute path="/" exact component={Home} props={child_props}/>
    <AppliedRoute path="/login" exact component={Login} props={child_props}/>
    <AppliedRoute path="/markets/new" exact component={NewMarket} props={child_props}/>

    <Route component={NotFound}/>
  </Switch>;
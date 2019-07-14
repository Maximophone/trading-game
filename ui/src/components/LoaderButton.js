import React from "react";
import {Button, Glyphicon} from "react-bootstrap"
import "./LoaderButton.css"

export default ({
    is_loading,
    text,
    loading_text,
    class_name = "",
    disabled = false,
    ...props
}) => 
    <Button
        className={`LoaderButton ${class_name}`}
        disabled={disabled || is_loading}
        {...props}
        >
            {is_loading && <Glyphicon glyph="refresh" className="spinning" />}
            {!is_loading ? text : loading_text}
    </Button>;
    
#!/usr/bin/env python

import marimo

__generated_with = "0.15.0"
app = marimo.App(
    width="medium",
    app_title="monotes",
    css_file="./style/output.css",
    html_head_file="./style/templates/head.html",
)

with app.setup:
    # Initialization code that runs before all other cells
    import marimo as mo
    from mohtml import (
        div,  # pyrefly: ignore
        p,  # pyrefly: ignore
        span,  # pyrefly: ignore
        h1,  # pyrefly: ignore
        h2,  # pyrefly: ignore
        h3,  # pyrefly: ignore
        a,  # pyrefly: ignore
        button,  # pyrefly: ignore
        script,  # pyrefly: ignore
        head,  # pyrefly: ignore
    )
    from monotes.elements import note, button_note


@app.cell
def _():
    head(
        """<script type="module" src="https://cdn.jsdelivr.net/gh/starfederation/datastar@main/bundles/datastar.js"></script>"""
    )
    return


@app.cell
def _():
    note("Hello World")
    return


@app.cell
def _():
    button_note()
    return


if __name__ == "__main__":
    app.run()

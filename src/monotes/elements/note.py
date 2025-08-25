import marimo as mo
from mohtml import div, p, span, h1, h2, h3, button, a  # pyrefly: ignore
from datastar_py import attribute_generator as data


def note(text: str) -> div:
    return div(
        p(text),
        klass="text-sm text-green-700 bg-green-100 p-4 rounded-lg",
        data=data.on_load("@get('/update')"),
    )


data_on_click = data.on("click", "alert('Alert!')")


def button_note() -> None:
    return button(
        "Click me!",
        data_on_click="alert('Alert!')",
        klass="bg-green-500 hover:bg-blue-700 text-black hover:text-yellow-400 font-bold py-2 px-4 rounded-b-2xl",
    )

# Standard Imports

# Third Party Imports
from mohtml import (
    div,  # pyrefly: ignore
    button,  # pyrefly: ignore
    textarea,  # pyrefly: ignore
)

# My Imports


# ------------------Elements-------------------#
def note(text: str) -> str:
    return str(
        div(
            div(  # This is the main note container
                textarea(
                    text,
                    data_bind="note_text",
                    klass="text-base text-[var(--base05)] glow-text glass-card p-10 rounded-xl shadow-lg w-full h-full transition-all duration-300 hover:shadow-xl hover:scale-[1.02] flex flex-col justify-between items-start space-y-4",
                ),
                div(  # Wrapper for the button to position it
                    submit_note_button(),
                    klass="absolute top-4 right-4 z-10",  # Position button in top right
                ),
                klass="relative w-full max-w-4xl h-[calc(100vh-4rem)] mx-auto my-4",  # Responsive note container
            ),
            id="note",
            klass="flex justify-center items-center min-h-screen p-4",  # Centering div with padding
        )
    )


def submit_note_button() -> str:
    return str(
        button(
            "Submit",
            data_on_click="@post('/note/submit')",
            klass="glass-button text-[var(--base05)] hover:text-[var(--base07)] font-bold py-2 px-4 rounded-lg text-sm",
        )
    )

import marimo as mo
from mohtml import div, p, span, h1, h2, h3, button, a, textarea  # pyrefly: ignore
from datastar_py import attribute_generator as data


def note(text: str) -> str:
    """
    Generates a cloud sticky note HTML element with a glassy, modern UI.
    Uses the 'spaceduck' theme and is responsive.
    """
    return str(
        div(
            textarea(
                text,
                data_bind="note_text",
                klass="text-base text-[var(--base05)] glow-text glass-card p-6 rounded-xl shadow-lg w-full min-h-[calc(100vh-2rem)] transition-all duration-300 hover:shadow-xl hover:scale-[1.02] flex flex-col justify-between items-start space-y-4",
            ),
            id="note",
            klass="flex justify-center items-center min-h-screen p-10",  # Centering div with padding
        )
    )

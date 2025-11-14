"""
Glass Card Component
Reusable context manager for glassmorphism card containers
"""

import streamlit as st
from contextlib import contextmanager
from typing import Optional


@contextmanager
def glass_card(
    hover: bool = False,
    padding: str = "1.5rem",
    margin: str = "0",
    border_radius: str = "1rem"
):
    """
    Context manager for creating glassmorphism card containers.

    Usage:
        with glass_card():
            st.write("Content goes here")

        with glass_card(hover=True):
            st.write("Card with hover effect")

    Args:
        hover: Whether to add hover effect (default: False)
        padding: CSS padding value (default: "1.5rem")
        margin: CSS margin value (default: "0")
        border_radius: CSS border-radius value (default: "1rem")

    Yields:
        None (manages opening and closing div tags)

    Example:
        >>> with glass_card():
        ...     st.markdown("### Title")
        ...     st.write("Content")

        >>> with glass_card(hover=True, padding="2rem"):
        ...     st.metric("Stat", "1,234")
    """
    # Hover effect styles
    hover_style = """
        transition: all 0.2s ease;
        cursor: pointer;
    """ if hover else ""

    hover_pseudo = """
        <style>
        .glass-card-hover:hover {
            transform: translateY(-2px);
            box-shadow: 0 8px 32px rgba(59, 130, 246, 0.2);
            border-color: rgba(59, 130, 246, 0.3);
        }
        </style>
    """ if hover else ""

    # Opening div
    hover_class = " glass-card-hover" if hover else ""

    st.markdown(
        f"""
        {hover_pseudo}
        <div class="glass-card{hover_class}" style="
            background: rgba(255, 255, 255, 0.05);
            backdrop-filter: blur(10px);
            -webkit-backdrop-filter: blur(10px);
            border: 1px solid rgba(255, 255, 255, 0.1);
            border-radius: {border_radius};
            padding: {padding};
            margin: {margin};
            {hover_style}
        ">
        """,
        unsafe_allow_html=True
    )

    try:
        yield
    finally:
        # Closing div
        st.markdown("</div>", unsafe_allow_html=True)


def render_glass_container(
    content: str,
    hover: bool = False,
    padding: str = "1.5rem",
    margin: str = "0 0 1rem 0",
    border_radius: str = "1rem"
):
    """
    Render a glass card container with HTML content.

    Use this function when you need to wrap pre-generated HTML in a glass card.
    For Streamlit components, use the glass_card() context manager instead.

    Args:
        content: HTML content to display inside the card
        hover: Whether to add hover effect (default: False)
        padding: CSS padding value (default: "1.5rem")
        margin: CSS margin value (default: "0 0 1rem 0")
        border_radius: CSS border-radius value (default: "1rem")

    Example:
        >>> html_content = "<h3>Title</h3><p>Some content</p>"
        >>> render_glass_container(html_content, hover=True)
    """
    hover_style = """
        transition: all 0.2s ease;
        cursor: pointer;
    """ if hover else ""

    hover_pseudo = """
        <style>
        .glass-container-hover:hover {
            transform: translateY(-2px);
            box-shadow: 0 8px 32px rgba(59, 130, 246, 0.2);
            border-color: rgba(59, 130, 246, 0.3);
        }
        </style>
    """ if hover else ""

    hover_class = " glass-container-hover" if hover else ""

    html = f"""
    {hover_pseudo}
    <div class="glass-card{hover_class}" style="
        background: rgba(255, 255, 255, 0.05);
        backdrop-filter: blur(10px);
        -webkit-backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: {border_radius};
        padding: {padding};
        margin: {margin};
        {hover_style}
    ">
        {content}
    </div>
    """

    st.markdown(html, unsafe_allow_html=True)

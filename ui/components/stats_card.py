"""
Stats Card Component
Reusable component for displaying statistics with glassmorphism styling
"""

import streamlit as st
from typing import Optional


def render_stat_card(
    value: str,
    label: str,
    container: Optional[st.delta_generator.DeltaGenerator] = None,
    gradient_start: str = "#60a5fa",
    gradient_end: str = "#a78bfa"
):
    """
    Render a statistics card with glass styling and gradient text.

    Args:
        value: The statistic value to display (e.g., "1,234" or "$5.2M")
        label: The label/description for the statistic
        container: Optional Streamlit container to render in (default: None uses st)
        gradient_start: Starting color for gradient (default: blue)
        gradient_end: Ending color for gradient (default: purple)

    Example:
        >>> render_stat_card("1,234", "Total Properties")
        >>> render_stat_card("$5.2M", "Portfolio Value", gradient_start="#10b981", gradient_end="#3b82f6")
    """
    # Use provided container or default to st
    display = container if container else st

    # Generate the HTML for the stat card
    html = f"""
    <div style="background: rgba(255, 255, 255, 0.05);
                padding: 1rem;
                border-radius: 0.75rem;
                text-align: center;
                border: 1px solid rgba(255, 255, 255, 0.08);
                transition: all 0.2s ease;">
        <div style="font-size: 1.5rem;
                    font-weight: 700;
                    background: linear-gradient(135deg, {gradient_start} 0%, {gradient_end} 100%);
                    -webkit-background-clip: text;
                    -webkit-text-fill-color: transparent;
                    background-clip: text;
                    margin-bottom: 0.375rem;">
            {value}
        </div>
        <div style="font-size: 0.6875rem;
                    color: #71717a;
                    text-transform: uppercase;
                    letter-spacing: 0.05em;
                    font-weight: 600;">
            {label}
        </div>
    </div>
    """

    display.markdown(html, unsafe_allow_html=True)


def render_metric_card(
    value: str,
    label: str,
    icon: str = "📊",
    container: Optional[st.delta_generator.DeltaGenerator] = None
):
    """
    Render a metric card with an icon and glass styling.

    Args:
        value: The metric value to display
        label: The label/description for the metric
        icon: Emoji or icon to display (default: "📊")
        container: Optional Streamlit container to render in

    Example:
        >>> render_metric_card("42", "Active Markets", icon="🏙️")
    """
    display = container if container else st

    html = f"""
    <div style="background: rgba(255, 255, 255, 0.05);
                padding: 1.25rem;
                border-radius: 0.75rem;
                border: 1px solid rgba(255, 255, 255, 0.08);
                display: flex;
                align-items: center;
                gap: 1rem;
                transition: all 0.2s ease;">
        <div style="font-size: 2rem;">
            {icon}
        </div>
        <div style="flex: 1;">
            <div style="font-size: 1.75rem;
                        font-weight: 700;
                        background: linear-gradient(135deg, #60a5fa 0%, #a78bfa 100%);
                        -webkit-background-clip: text;
                        -webkit-text-fill-color: transparent;
                        background-clip: text;
                        line-height: 1.2;">
                {value}
            </div>
            <div style="font-size: 0.875rem;
                        color: #9ca3af;
                        margin-top: 0.25rem;">
                {label}
            </div>
        </div>
    </div>
    """

    display.markdown(html, unsafe_allow_html=True)


def format_number(num: float) -> str:
    """
    Format a number for display with appropriate suffix.

    Args:
        num: Number to format

    Returns:
        Formatted string (e.g., "1.2K", "3.5M", "4.2B")

    Example:
        >>> format_number(1234)
        '1.2K'
        >>> format_number(5678901)
        '5.7M'
    """
    if num >= 1_000_000_000:
        return f"{num / 1_000_000_000:.1f}B"
    elif num >= 1_000_000:
        return f"{num / 1_000_000:.1f}M"
    elif num >= 1_000:
        return f"{num / 1_000:.1f}K"
    else:
        return f"{num:,.0f}"


def format_currency(amount: float) -> str:
    """
    Format a currency amount for display with appropriate suffix.

    Args:
        amount: Currency amount to format

    Returns:
        Formatted string with $ prefix (e.g., "$1.2K", "$3.5M")

    Example:
        >>> format_currency(1234)
        '$1.2K'
        >>> format_currency(5678901)
        '$5.7M'
    """
    if amount >= 1_000_000:
        return f"${amount / 1_000_000:.1f}M"
    elif amount >= 1_000:
        return f"${amount / 1_000:.0f}K"
    else:
        return f"${amount:.0f}"

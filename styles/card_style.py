"""Reusable card helpers for consistent dashboard visuals."""
import streamlit as st


CARD_STYLE = """
<style>
  .sd-card {
    background: var(--surface);
    border-radius: 14px;
    border: 1px solid rgba(31, 75, 153, 0.12);
    box-shadow: 0 12px 30px -18px rgba(16, 24, 40, 0.35);
    padding: 1.5rem;
    margin-bottom: 1.5rem;
  }

  .sd-metric-card {
    background: var(--surface);
    border-radius: 14px;
    border: 1px solid rgba(19, 163, 110, 0.18);
    box-shadow: 0 16px 28px -20px rgba(19, 163, 110, 0.65);
    padding: 1.2rem 1.4rem;
    display: flex;
    flex-direction: column;
    gap: 0.35rem;
  }

  .sd-metric-card h4 {
    margin: 0;
    font-size: 0.95rem;
    font-weight: 600;
    color: var(--muted-text);
    letter-spacing: 0.01em;
    text-transform: uppercase;
  }

  .sd-metric-card .metric-value {
    font-size: calc(var(--metric-value-size));
    font-weight: 700;
    color: var(--brand-primary);
  }

  .sd-metric-card p {
    margin: 0;
    font-size: 0.92rem;
    color: var(--muted-text);
  }

  .sd-dashboard-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
    gap: 1.5rem;
    margin-bottom: 2rem;
  }
</style>
"""


def apply_card_styles() -> None:
    """Ensure card styling CSS is present for the current page."""
    st.markdown(CARD_STYLE, unsafe_allow_html=True)


def create_metric_card(title: str, value: str, description: str | None = None) -> str:
    """Return HTML for a metric tile."""
    description_html = f"<p>{description}</p>" if description else ""
    return (
        f"<div class=\"sd-metric-card\">"
        f"  <h4>{title}</h4>"
        f"  <div class=\"metric-value\">{value}</div>"
        f"  {description_html}"
        f"</div>"
    )


def create_dashboard_container() -> None:
    """Open a responsive grid container."""
    st.markdown('<div class="sd-dashboard-grid">', unsafe_allow_html=True)


def end_dashboard_container() -> None:
    """Close the grid container."""
    st.markdown('</div>', unsafe_allow_html=True)

"""Tiny display helpers (Indian-style money, percentages)."""


def inr(x: float) -> str:
    """Compact rupee format: Crore for big numbers, Lakh for medium, plain for small."""
    sign = "-" if x < 0 else ""
    x = abs(x)
    if x >= 1e7:
        return f"{sign}₹{x / 1e7:,.1f} Cr"
    if x >= 1e5:
        return f"{sign}₹{x / 1e5:,.1f} L"
    return f"{sign}₹{x:,.0f}"


def pct(x: float, digits: int = 1) -> str:
    """0.774 -> '77.4%'"""
    return f"{x * 100:.{digits}f}%"


def pp(x: float, digits: int = 1) -> str:
    """Percentage-point difference: 0.0123 -> '+1.2 pp'"""
    return f"{x * 100:+.{digits}f} pp"

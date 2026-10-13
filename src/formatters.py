"""Tiny display helpers (Indian-style money, percentages)."""


def inr(x: float) -> str:
    """Compact rupee format: Crore for big numbers, Lakh for medium, plain for small."""
    sign = "-" if x < 0 else ""
    x = abs(x)
    if x >= 1e10:                      # 1,000 Cr and above: decimals add noise
        return f"{sign}₹{x / 1e7:,.0f} Cr"
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


def compact(x: float) -> str:
    """Compact plain number: 1,543,767 -> '1.54M', 12,345 -> '12.3k', 3.14159 -> '3.14'."""
    sign = "-" if x < 0 else ""
    x = abs(x)
    if x >= 1e6:
        return f"{sign}{x / 1e6:,.2f}M"
    if x >= 1e4:
        return f"{sign}{x / 1e3:,.1f}k"
    if x >= 100:
        return f"{sign}{x:,.0f}"
    return f"{sign}{x:,.2f}"

from django import template

register = template.Library()


@register.filter(is_safe=False)
def rupiah(value):
    """Format number as Indonesian Rupiah, e.g. 1000000 -> 'Rp 1.000.000'

    If value is not a number, return as-is.
    """
    try:
        # support Decimal, float, int, and numeric strings
        amount = int(round(float(value)))
    except Exception:
        return value

    # use comma thousands then replace with dot for Indonesian format
    s = f"{amount:,}".replace(",", ".")
    return f"Rp {s}"

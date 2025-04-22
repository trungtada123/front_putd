from django import template

register = template.Library()

@register.filter(name='dinh_dang_tien')
def dinh_dang_tien(so):
    """
    Format a number as currency with dot as thousand separator and comma as decimal separator.
    Example: 1234567.89 -> 1.234.567,89
    """
    if so is None:
        so = 0
    
    # Convert to float to ensure consistent handling
    try:
        so = float(so)
    except (ValueError, TypeError):
        so = 0
        
    # Format with thousand separators and 2 decimal places
    formatted = "{:,.0f}".format(so)  # No decimal places for currency
    
    # Replace commas with dots for thousand separators
    return formatted.replace(",", ".") 
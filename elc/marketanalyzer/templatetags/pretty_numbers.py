from django import template
import locale

register = template.Library()

@register.filter(name='comma_trunc')
def comma_trunc(value, default):
    """
    A filter to add commas to numbers and truncate right of radix. Also
    implements the built-in ``default_if_none`` template filter's behavior.    
    That is, if (and only if) ``value`` is ``None``, use given ``default``,
    otherwise format and display ``value``.
    """    
    if value == None:
        return default
    else:
        return locale.format('%.0f', value, grouping=True)
        
@register.filter(name='isk')
def isk(value):
    """
    A filter to add the currency symbol "ISK" to the end of strings.
    """
    
    if value and (value != 'N/A'):
        return value + ' ISK'
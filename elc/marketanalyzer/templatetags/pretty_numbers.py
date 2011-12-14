from django import template
import locale

register = template.Library()

@register.filter(name='addcommas')
def addcommas(value, default):
    """
    A filter to add commas to numbers and display 2 decimal places. Also
    implements the built-in ``default_if_none`` template filter's behavior.    
    That is, if (and only if) ``value`` is ``None``, use given ``default``,
    otherwise format and display ``value``.
    
    For example, if ``var`` contains ``15023145.3200``, then
    ``{{ var|addcommas:"N/A" }}`` would return ``15,023,145.32``.
    If ``var`` were equal to ``None``, then ``N/A`` would be the result.
    """    
    if value == None:
        return default
    else:
        return locale.format('%.2f', value, grouping=True)
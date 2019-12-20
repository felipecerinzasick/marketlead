from django import template

register = template.Library()

@register.simple_tag
def get_cpc(page_obj, cost, click):
    return page_obj.calculate_cpc(cost, click)

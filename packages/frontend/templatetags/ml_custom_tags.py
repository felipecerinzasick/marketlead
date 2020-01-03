from django import template

register = template.Library()

@register.simple_tag
def get_cpc(page_obj, cost, days):
    click = page_obj.get_visit_count_by_day(days)
    return page_obj.calculate_cpc(cost, click)


@register.simple_tag
def get_visit_count_by_day(model_obj, day):
    return model_obj.get_visit_count_by_day(day=day)


@register.simple_tag
def get_bounce_rate_by_day(page_obj, day):
    return page_obj.get_bounce_rate_by_day(day=day)

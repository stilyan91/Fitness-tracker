from datetime import date

from django import template

register = template.Library()


@register.filter(name="placeholder")
def placeholder(value, token):
    value.widget.attrs['placeholder'] = token
    return value


@register.filter(name='find_report_for_date')
def find_report_for_date(reports, day):
    for report in reports:
        if report.date.day == day:
            return report
    return None

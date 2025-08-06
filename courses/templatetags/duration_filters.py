from django import template

register = template.Library()

@register.filter
def duration_hm(seconds):
    try:
        seconds = int(seconds)
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        return f"{hours} ساعت و {minutes} دقیقه" if hours else f"{minutes} دقیقه"
    except (ValueError, TypeError):
        return "مدت نامعتبر"


@register.filter
def duration_from_hours(hours_float):
    try:
        hours_float = float(hours_float)
        hours = int(hours_float)
        minutes = int(round((hours_float - hours) * 60))
        if hours and minutes:
            return f"{hours} ساعت و {minutes} دقیقه"
        elif hours:
            return f"{hours} ساعت"
        elif minutes:
            return f"{minutes} دقیقه"
        else:
            return "۰ دقیقه"
    except (ValueError, TypeError):
        return "مدت نامعتبر"
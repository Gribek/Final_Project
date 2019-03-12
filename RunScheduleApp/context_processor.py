from RunScheduleApp.views import get_month_counter
from RunScheduleApp.models import WorkoutPlan


def pass_month_counter_to_base_html(request):
    if request.user.is_anonymous:
        ctx = {'get_month_counter': 0}
        return ctx
    if not WorkoutPlan.objects.filter(owner=request.user).filter(is_active=True).exists():
        ctx = {'get_month_counter': 0}
        return ctx
    plan_start_date = WorkoutPlan.objects.filter(owner=request.user).filter(is_active=True)[0].date_range.lower
    ctx = {
        'get_month_counter': get_month_counter(plan_start_date)
    }
    return ctx

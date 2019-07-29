from RunScheduleApp.views import WorkoutPlanView


def pass_month_counter_to_base_html(request):
    current_user = request.user
    ctx = {'get_month_counter': 1}
    if not current_user.is_anonymous:
        workout_plan = WorkoutPlanView.get_active_workout_plan(current_user)
        if workout_plan:
            plan_start_date = workout_plan.date_range.lower
            month_number = WorkoutPlanView.get_present_month_number(
                plan_start_date)
            ctx['get_month_counter'] = month_number
    return ctx

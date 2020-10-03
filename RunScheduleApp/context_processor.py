from datetime import datetime


def get_current_month_and_year(request):
    current_time = datetime.now()
    return {'month': current_time.month, 'year': current_time.year}

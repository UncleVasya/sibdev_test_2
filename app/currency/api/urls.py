from django.urls import path

from app.currency.api import views

app_name = 'currency'

urlpatterns = [
    path(
        'currency/user-currency/',
        views.UserCurrencyCreateView.as_view(),
        name='user-currency'
    ),
    path(
        'currency/<int:id>/analytics/',
        views.AnalyticsView.as_view(),
        name='analytics'
    ),
    path(
        'rates/',
        views.RatesView.as_view(),
        name='rates'
    ),
]

from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),

    path('api/v1/user/', include('app.users.api.urls', namespace='v1')),
    path('api/v1/', include('app.currency.api.urls', namespace='v1'))
]

"""
URL configuration for quit_smoking project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from quit_smoking_webapp.views import register_view, login_view, welcome_view, dashboard_view, logout_view, ui_add_daily_log_view, ui_edit_daily_log_view, ui_delete_log_view, ui_profile, ui_daily_log, ui_starting_point, ui_home, password_reset_confirm_view, password_reset_view

urlpatterns = [
    path('admin/', admin.site.urls),
    path("", welcome_view, name='welcome'),
    path('register', register_view, name='register'),
    path('login/', login_view, name='login'),
    path('password-reset', password_reset_view, name='password-reset'),
    path('password-reset/<uidb64>/<token>', password_reset_confirm_view, name='password-reset-confirm'),
    path('dashboard', dashboard_view, name='dashboard'),
    path('logout', logout_view, name='logout'),
    path("app/ui/home/", ui_home, name="ui_home"),
    path("app/ui/starting-point/", ui_starting_point, name="ui_starting_point"),
    path("app/ui/profile/", ui_profile, name="ui_profile"),
    path("app/ui/daily-log/", ui_daily_log, name="ui_daily_log"),
    path("app/ui/daily-log/add/", ui_add_daily_log_view, name="ui_daily_log_add"),
    path("app/ui/daily-log/edit/<int:log_id>", ui_edit_daily_log_view, name="ui_daily_log_edit"),
    path("app/ui/daily-log/delete/<int:log_id>", ui_delete_log_view, name="ui_daily_log_delete"),
]

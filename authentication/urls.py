from django.urls import path
from .views import KeycloakSSOLoginView, DashboardView

urlpatterns = [
    path('auth/login/', KeycloakSSOLoginView.as_view(), name='keycloak-sso-login'),
    path('dashboard/', DashboardView.as_view(), name='user-dashboard'),
]

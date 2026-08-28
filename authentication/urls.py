from django.urls import path
from .views import (
    KeycloakSSOLoginView,
    DashboardView,
    PermissionListView,
    RoleListCreateView,
    RoleDetailView,
    RolePermissionAssignView,
    RoleAdminTemplateView
)

urlpatterns = [
    path('auth/login/', KeycloakSSOLoginView.as_view(), name='keycloak-sso-login'),
    path('dashboard/', DashboardView.as_view(), name='user-dashboard'),
    path('permissions/', PermissionListView.as_view(), name='permission-list'),
    path('roles/', RoleListCreateView.as_view(), name='role-list-create'),
    path('roles/<int:pk>/', RoleDetailView.as_view(), name='role-detail'),
    path('roles/<int:pk>/permissions/', RolePermissionAssignView.as_view(), name='role-permission-assign'),
    path('roles/admin/', RoleAdminTemplateView.as_view(), name='roles-admin-ui'),
]

from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static
from django.conf import settings
from subscription.views import home_view, subscribe, success_page, subscribed_users, others
from django.contrib.auth.views import (
    LoginView, LogoutView, PasswordChangeView, PasswordChangeDoneView,
    PasswordResetView, PasswordResetDoneView, PasswordResetConfirmView,
    PasswordResetCompleteView,
)
from accounts.views import ProfileView, register, activate, account_settings, change_info

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('django.contrib.auth.urls')),
    path('acounts/login/', LoginView.as_view(), name='login'),
    path('accounts/logout/', LogoutView.as_view(), name='logout'),
    path('accounts/profile/', ProfileView.as_view(), name='profile'),
    path('accounts/register/', register, name='register'),
    path('accounts/activate/<uidb64>/<token>/', activate, name='activate'),
    path('accounts/account_settings/', account_settings, name='account_settings'),
    path('accounts/change_info/', change_info, name='change_info'),
    path('accounts/password_change/', PasswordChangeView.as_view(), name='password_change'),
    path('accounts/password_change/done/', PasswordChangeDoneView.as_view(), name='password_change_done'),
    path('accounts/password_reset/', PasswordResetView.as_view(), name='password_reset'),
    path('accounts/password_reset/done/', PasswordResetDoneView.as_view(), name='password_reset_done'),
    path('accounts/reset/<uidb64>/<token>/', PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('accounts/reset/done/', PasswordResetCompleteView.as_view(), name='password_reset_complete'),
    path('', home_view, name='home'),
    path('subscribe/', subscribe, name='subscribe'),
    path('others/', others, name='others'),
    path('success/', success_page, name='success'),
    path('admin/subscribed-users/', subscribed_users, name='subscribed_users'),
]
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

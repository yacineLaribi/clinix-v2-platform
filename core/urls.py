from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static


app_name = 'core'
urlpatterns = [
    path('', views.index, name='index'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('challenges/', views.challenges, name='challenges'),
    path('challenges/<int:pk>/', views.challenge_details, name='challenge_details'),
    path('profile/', views.profile, name='profile'),
    path('use-hint/<int:hint_id>/', views.use_hint, name='use_hint'),
    path('leaderboard/', views.leaderboard, name='leaderboard'),
    path('api/leaderboard/', views.api_leaderboard, name='api_leaderboard'),
    # Admin Dashboard Routes
    path('admin-access/dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('admin-access/submission/<int:submission_id>/update/', views.update_submission_status, name='update_submission_status'),
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

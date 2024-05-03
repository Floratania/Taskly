from django.urls import path, include
from . import views
from .views import CustomPasswordResetDoneView, CustomPasswordResetConfirmView, CustomPasswordResetCompleteView, CustomPasswordResetView
# from django.conf.urls.i18n import set_language
from django.conf.urls.i18n import i18n_patterns
from django.views.i18n import set_language



urlpatterns = [
    
    path('', views.home, name=""),

    path('register', views.register, name="register"),
    
    path('my-login', views.my_login, name="my-login"),
    
    path('set-language/', set_language, name='set_language'),
    
    path('change-password/', views.change_password, name='change-password'),
    
    path('dashboard', views.dashboard, name="dashboard"),
    
    path('profile-management', views.profile_management, name="profile-management"),
    
    path('activity', views.activity, name="activity"),
    
    path('delete-account', views.deleteAccount, name="delete-account"),

    path('create-task', views.createTask, name="create-task"),
    
    path('view-tasks', views.viewTasks, name="view-tasks"),
    
    path('profile/task/<int:task_id>/', views.viewTask, name='view_task'),
    
    path('view-task/<int:task_id>/', views.viewTask, name="view-task"),

    path('update-task/<str:pk>/' , views.updateTask, name="update-task"),
    
    path('delete-task/<str:pk>/', views.deleteTask, name="delete-task"),
    
    path('user-logout', views.user_logout, name="user-logout"),
    
    path('task/<int:pk>/', views.task_detail, name='task-detail'),
  
    path('', include('cal.urls')),
    
    path('activity_chart/', views.ActivityView.as_view(), name='activity_chart'),
    
    path('task_daily_count', views.task_daily_count, name='task_daily_count'),
    
    path('password-reset/', CustomPasswordResetView.as_view(), name='password_reset'),
    
    path('password-reset/done/', CustomPasswordResetDoneView.as_view(), name='password_reset_done'),
    
    path('reset/<uidb64>/<token>/', CustomPasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    
    path('reset/done/', CustomPasswordResetCompleteView.as_view(), name='password_reset_complete'),
    
    
     
]
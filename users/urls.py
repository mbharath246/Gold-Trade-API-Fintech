from django.urls import path
from users import views

urlpatterns = [
    path('list/',views.UsersListView.as_view(), name='users-list'),
    path('create/',views.CreateUser.as_view(), name='user-create'),
    path('reset/',views.PasswordResetView.as_view(), name='password-reset'),
    path('details/',views.UserDetailView.as_view(), name='user-detail'),
]
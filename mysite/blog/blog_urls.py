from django.urls import path
from . import views
app_name = 'blog'

urlpatterns = [
    path('index/', views.index, name='index'),
    path('members/<int:pk>/',views.members, name='members'),
    path('members/', views.members, name='members'),
    path('', views.login_register,kwargs=None,name='login'),
    path('article/<int:pk>/', views.article_detail, name='article_detail'),
    path('article/<int:pk>/comment/',views.add_comment, name='add_comment'),
    path('index/submit/',views.submit,name='submit'),
    path('edit_article/<int:pk>/',views.edit_article,name='edit_article'),
    path('edit_member/',views.edit_member,name='edit_member'),
    path('placeholder/',views.placeholder,name='placeholder'),
    path("logout/", views.logout_view, name="logout"),
    path("upload-avatar/", views.upload_avatar, name="upload_avatar")
]
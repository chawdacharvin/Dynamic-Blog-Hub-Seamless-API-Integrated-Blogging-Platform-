from django.urls import path
from . import views
from .views import BlogListView, Detailview

urlpatterns = [
    path('', views.home, name="home"),
    path('login', views.login, name="login"),
    path('logout', views.logout, name="logout"),
    path('register', views.register, name="register"),
    path('post/<str:pk>', views.singlepost, name="singlepost"),
    path('addpost/', views.addpost, name="addpost"),
    path('post/delete-post/<int:post_id>', views.delpost, name="deletepost"),
    path('post/delete-comment/<int:comment_id>', views.delcomment, name="deletecomment"),
    path('post/edit-post/<int:post_id>', views.editpost, name="editpost"),
    path('post/edit-comment/<int:comment_id>', views.editcomment, name="editcomment"),
    path('like-post/<int:post_id>', views.like_post, name="likepost"),
    path('dislike-post/<int:post_id>', views.dislike_post, name="dislikepost"),
    path('search/', views.search_posts, name="search"),
    path('api/blogs', BlogListView.as_view(), name="apiblog"),
    path('api/blogs/<int:id>/', Detailview.as_view(), name="apiblogdetail"),
    path("healthcheck/", views.health_check, name="health_check"),
]

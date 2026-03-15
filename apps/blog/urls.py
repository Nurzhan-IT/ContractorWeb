from django.urls import path

from .views import ArticleDetailView, BlogListView

app_name = 'blog'

urlpatterns = [
    path('', BlogListView.as_view(), name='index'),
    path('<slug:slug>/', ArticleDetailView.as_view(), name='detail'),
]

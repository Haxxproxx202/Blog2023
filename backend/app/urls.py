from django.urls import path
from .views import PostListView, post_detail

app_name = "app"

urlpatterns = [
    path('', PostListView.as_view(), name='post_list'),
    path('<int:year>/<int:month>/<int:day>/<slug:post>/', post_detail, name='post_detail')
]

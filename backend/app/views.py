from django.shortcuts import render, get_object_or_404

from django.views.generic import ListView
from .models import Post


# from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
#
# def post_list(request):
#     object_list = Post.published.all()
#
#     paginator = Paginator(object_list, 2)
#     page = request.GET.get('page')
#     print(page)
#     try:
#         posts = paginator.page(page)
#     except PageNotAnInteger:
#         posts = paginator.page(1)
#     except EmptyPage:
#         posts = paginator.page(paginator.num_pages)
#
#     ctx = {'posts': posts, 'page': page}
#
#     return render(request, 'app/post/list.html', ctx)

class PostListView(ListView):
    queryset = Post.published.all()
    # model = Post
    template_name = 'app/post/list.html'
    context_object_name = 'posts'  # default name = object_list
    paginate_by = 2


def post_detail(request, year, month, day, post):
    post = get_object_or_404(Post,
                             slug=post,
                             status='published',
                             publish__year=year,
                             publish__month=month,
                             publish__day=day)
    ctx = {'post': post}
    return render(request, 'app/post/detail.html', ctx)


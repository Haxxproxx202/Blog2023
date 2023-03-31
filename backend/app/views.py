from django.shortcuts import render, get_object_or_404
from django.core.mail import send_mail
from django.views.generic import ListView
from .models import Post
from .forms import EmailPostForm


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


def post_share(request, post_id):
    post = get_object_or_404(Post, id=post_id, status='published')
    sent = False

    if request.method == "POST":
        form = EmailPostForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            post_url = request.build_absolute_uri(post.get_absolute_url())
            subject = '{} ({}) encourages you to read "{}"'.format(cd['name'], cd['email'], post.title)
            message = 'Read this post "{}" na the site {}\n\n Comment added by {}: {}'\
                .format(post.title, post_url, cd['name'], cd['comments'])

            send_mail(subject, message, 'coding.accto@gmail.com', [cd['recipient']])
            sent = True
    else:
        form = EmailPostForm()
    return render(request, 'app/post/share.html', {'post': post, 'form': form, 'sent': sent})


def post_detail(request, year, month, day, post):
    post = get_object_or_404(Post,
                             slug=post,
                             status='published',
                             publish__year=year,
                             publish__month=month,
                             publish__day=day)
    ctx = {'post': post}
    return render(request, 'app/post/detail.html', ctx)


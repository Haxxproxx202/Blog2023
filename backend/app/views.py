from django.shortcuts import render, get_object_or_404
from django.core.mail import send_mail
from django.db.models import Count
from django.views.generic import ListView
from .models import Post, Comment
from .forms import EmailPostForm, CommentForm
from taggit.models import Tag


from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger


def post_list(request, tag_slug=None):
    object_list = Post.published.all()
    tag = None

    if tag_slug:
        tag = get_object_or_404(Tag, slug=tag_slug)
        object_list = object_list.filter(tags__in=[tag])

    paginator = Paginator(object_list, 3)
    page = request.GET.get('page')
    try:
        posts = paginator.page(page)
    except PageNotAnInteger:
        posts = paginator.page(1)
    except EmptyPage:
        posts = paginator.page(paginator.num_pages)

    ctx = {'posts': posts,
           'page': page,
           'tag': tag}

    return render(request, 'app/post/list.html', ctx)

# class PostListView(ListView):
#     queryset = Post.published.all()
#     # model = Post
#     template_name = 'app/post/list.html'
#     context_object_name = 'posts'  # default name = object_list
#     paginate_by = 2


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
    comments = post.comments.filter(active=True)

    new_comment = None

    if request.method == 'POST':
        comment_form = CommentForm(data=request.POST)
        if comment_form.is_valid():
            new_comment = comment_form.save(commit=False)
            new_comment.post = post
            new_comment.save()
    else:
        comment_form = CommentForm()

    # List of similar posts

    post_tags_ids = post.tags.values_list('id', flat=True)
    similar_posts = Post.published.filter(tags__in=post_tags_ids)\
                                  .exclude(id=post.id)
    similar_posts = similar_posts.annotate(same_tags=Count('tags'))\
                                 .order_by('-same_tags', '-publish')[:4]

    ctx = {'post': post,
           'comments': comments,
           'comment_form': comment_form,
           'new_comment': new_comment,
           'similar_posts': similar_posts}

    return render(request, 'app/post/detail.html', ctx)


from django.shortcuts import render, get_object_or_404
from django.core.mail import send_mail
from django.db.models import Count
from django.views.generic import ListView
from .models import Post, Comment
from .forms import EmailPostForm, CommentForm, SearchForm
from taggit.models import Tag
from django.contrib.postgres.search import SearchVector, SearchRank, SearchQuery, TrigramSimilarity


from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger


def post_list(request, tag_slug=None):
    """
    Render a paginated list of published blog posts.

    :param request: the HTTP request object
    :param tag_slug: a clicked Tag slug

    :return: If tag_slug provided, filter posts be the corresponding Tag object
    """
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


# Alternative option for post_list function, but without Tag objects
# class PostListView(ListView):
#     queryset = Post.published.all()
#     # model = Post
#     template_name = 'app/post/list.html'
#     context_object_name = 'posts'  # default name = object_list
#     paginate_by = 2


def post_share(request, post_id):
    """
    Render a form to share a published blog post via email.

    :param request: the HTTP request object
    :param post_id: the ID of the published post to be shared

    :return: if POST and the form is valid, send an email with the post information and render a confirmation page.
    """
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
    """
    Render a detailed view of a published blog post and handle the addition of new comments

    :param year:
    :param request: HTTP request object
    :param year, month, day: publication date
    :param post: slug of the post

    :return:
    -GET: detailed view of the post with comments and a form to add new comments
    -POST: refreshed view with new comment
    """
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


def post_search(request):
    """
    Search for published posts that match the provided query

    :param request: HTTP request object

    :return: Render the results
    """
    form = SearchForm()
    query = None
    results = []
    if 'query' in request.GET:
        form = SearchForm(request.GET)
        if form.is_valid():
            query = form.cleaned_data['query']
            search_vector = SearchVector('title', 'body')
            search_query = SearchQuery(query)
            results = Post.published.annotate(
                search=search_vector,
                rank=SearchRank(search_vector, search_query)
            ).filter(search=search_query). order_by('-rank')
    return render(request,
                  'app/post/search.html',
                  {'form': form,
                   'query': query,
                   'results': results})

# TRIGRAM SIMILARITY

# def post_search(request):
#     form = SearchForm()
#     query = None
#     results = []
#     if 'query' in request.GET:
#         form = SearchForm(request.GET)
#         if form.is_valid():
#             query = form.cleaned_data['query']
#             search_vector = SearchVector('title', weight='A') + SearchVector('body', weight='B')
#             search_query = SearchQuery(query)
#             results = Post.published.annotate(
#                 similarity=TrigramSimilarity('title', query)
#                 # rank=SearchRank(search_vector, search_query)
#             ).filter(similarity__gt=0.1).order_by('-similarity')
#     return render(request,
#                   'app/post/search.html',
#                   {'form': form,
#                    'query': query,
#                    'results': results})

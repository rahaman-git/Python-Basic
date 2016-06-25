#
# from urllib import quote_plus
#
from django.contrib import messages
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http import HttpResponse, HttpResponseRedirect,Http404
from django.shortcuts import render, get_object_or_404, redirect
from .forms import PostForm
from .models import Post
from django.utils import timezone
from django.db.models import Q
from comments.models import Comment
from django.contrib.contenttypes.models import ContentType
from comments.forms import CommentForm
from django.contrib.auth.decorators import login_required


@login_required
def post_create(request):
    if not (request.user.is_staff or request.user.is_superuser):
        raise Http404
    form = PostForm(request.POST or None, request.FILES or None)
    if form.is_valid():
        instance = form.save(commit=False)
        instance.user = request.user
        print form.cleaned_data.get("title")
        print instance.id
        instance.save()
        messages.success(request, "Successfully Created")
        return HttpResponseRedirect(instance.get_absolute_url())
    context = {
        "form": form,
    }
    return render(request, "post_form.html", context)


def post_detail(request, slug=None):
    today = timezone.now()
    # instance = Post.objects.get(id=3)
    instance = get_object_or_404(Post, slug=slug)
    if instance.publish > timezone.now() or instance.draft:
        if not request.user.is_staff or not request.user.is_superuser:
            raise Http404

    #
    # share_string = quote_plus(instance.content)
    #

    #
    # comments = Comment.objects.filter_by_instance(instance)
    #

    initial_data = {
        "content_type": instance.get_content_type,
        "object_id": instance.id
    }

    form = CommentForm(request.POST or None, initial=initial_data)
    if form.is_valid():
        c_type = form.cleaned_data.get('content_type')
        content_type = ContentType.objects.get(model=c_type)
        obj_id = form.cleaned_data.get('object_id')
        content_data = form.cleaned_data.get('content')
        parent_obj = None
        try:
            parent_id = int(request.POST.get('parent_id'))
        except:
            parent_id = None
        if parent_id:
            parent_qs = Comment.objects.filter(id=parent_id)
            if parent_qs.exists() and parent_qs.count() == 1:
                parent_obj = parent_qs.first()

        new_comment, created = Comment.objects.get_or_create(
                            user=request.user,
                            content_type=content_type,
                            object_id=obj_id,
                            content=content_data,
                            parent=parent_obj,
                        )
        return HttpResponseRedirect(new_comment.content_object.get_absolute_url())

    comments = instance.comments
    context = {
        "title": instance.title,
        "instance": instance,
        "today": today,
        "comments": comments,
        "comment_form": form,

        # "share_string": share_string,
    }
    return render(request, "Post_detail.html", context)


def post_list(request):
    today = timezone.now()
    query_list = Post.objects.active()
    if request.user.is_superuser:
        query_list = Post.objects.all()

    query = request.GET.get("q")
    if query:
        query_list = query_list.filter(
            Q(title__icontains=query) |
            Q(content__icontains=query) |
            Q(user__first_name__icontains=query) |
            Q(user__last_name__icontains=query)
        ).distinct()

    paginator = Paginator(query_list, 3)

    page_request_var = "page"
    page = request.GET.get(page_request_var)
    try:
        queryset = paginator.page(page)
    except PageNotAnInteger:
        #
        # If page is not an integer, deliver first page.
        #
        queryset = paginator.page(1)
    except EmptyPage:
        #
        # If page is out of range, deliver last page of results
        #
        queryset = paginator.page(paginator.num_pages)
    context = {
        "object_list": queryset,
        "title": "List",
        "page_request_var": page_request_var,
        "today": today,
    }
    return render(request, "post_list.html", context)


@login_required
def post_update(request, slug=None):
    instance = get_object_or_404(Post, slug=slug)
    if not ((request.user.is_staff and request.user.username == instance.user.username) or request.user.is_superuser):
        response = HttpResponse("You do not have permission to do this.")
        response.status_code = 403
        return response
        #
        # return render(request, "confirm_delete.html", context, status_code=403)
    form = PostForm(request.POST or None, request.FILES or None,instance=instance)
    if form.is_valid():
        instance = form.save(commit=False)
        instance.save()
        messages.success(request, "Successfully Updated")
        return HttpResponseRedirect(instance.get_absolute_url())
    context = {
        "title": instance.title,
        "instance": instance,
        "form": form,
    }
    return render(request, "post_form.html", context)


def post_delete(request, slug=None):
    instance = get_object_or_404(Post, slug=slug)
    instance.delete()
    return redirect("posts:list")

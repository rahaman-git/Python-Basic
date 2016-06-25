from django.conf.urls import url

# from . import views

# urlpatterns = [
#     url(r'^$', "posts.views.post_list"),
#     url(r'^create$', "posts.views.post_create"),
#     url(r'^detail$', "posts.views.post_detail"),
#     url(r'^update$', "posts.views.post_update"),
#     url(r'^delete$', "posts.views.post_delete"),
#     # url(r'^posts/$', "posts.views.post_home"),
# ]


from .views import (
    post_list,
    post_create,
    post_detail,
    post_update,
    post_delete,
)

urlpatterns = [
    url(r'^$', post_list, name='list'),
    url(r'^create$', post_create),
    url(r'^(?P<slug>[\w-]+)/$', post_detail, name='detail'),
    url(r'^(?P<slug>[\w-]+)/edit$', post_update, name='update'),
    url(r'^(?P<slug>[\w-]+)/delete$', post_delete),
]
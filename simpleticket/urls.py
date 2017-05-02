from django.conf.urls import url, include
from . import views

urlpatterns = [
    url(r'^$', views.view_all),
    url(r'^view/(?P<ticket_id>\d+)/$', views.view),
    url(r'^new/$', views.create),
    url(r'^submit_ticket/$', views.submit_ticket),
    url(r'^update/(?P<ticket_id>\d+)/$', views.update),
    url(r'^update_ticket/(?P<ticket_id>\d+)/$', views.update_ticket),
    url(r'^submit_comment/(?P<ticket_id>\d+)/$', views.submit_comment),
    url(r'^delete/(?P<ticket_id>\d+)/$', views.delete_ticket),
    url(r'^delete_comment/(?P<comment_id>\d+)/$', views.delete_comment),
    url(r'^project/$', views.project),
]

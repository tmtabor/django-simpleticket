from django.conf.urls import patterns, url

urlpatterns = patterns('',
                       url(r'^$', 'simpleticket.views.view_all'),
                       url(r'^view/(?P<ticket_id>\d+)/$', 'simpleticket.views.view'),
                       url(r'^new/$', 'simpleticket.views.create'),
                       url(r'^submit_ticket/$', 'simpleticket.views.submit_ticket'),
                       url(r'^update/(?P<ticket_id>\d+)/$', 'simpleticket.views.update'),
                       url(r'^update_ticket/(?P<ticket_id>\d+)/$', 'simpleticket.views.update_ticket'),
                       url(r'^submit_comment/(?P<ticket_id>\d+)/$', 'simpleticket.views.submit_comment'),
                       url(r'^delete/(?P<ticket_id>\d+)/$', 'simpleticket.views.delete_ticket'),
                       url(r'^delete_comment/(?P<comment_id>\d+)/$', 'simpleticket.views.delete_comment'),
                       url(r'^project/$', 'simpleticket.views.project'),
                       )

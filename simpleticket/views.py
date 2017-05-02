from datetime import datetime
from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.contrib.auth.models import User
from simpleticket.models import Priority, Status, Project, Ticket, TicketComment
from django.shortcuts import get_object_or_404
from django.core.paginator import Paginator, InvalidPage, EmptyPage
from django.contrib import messages

try:
    from urllib.parse import urlencode
except ImportError:
    from urllib import urlencode

from simpleticket.utils import email_user


def create(request):
    priority_list = Priority.objects.all()
    status_list = Status.objects.all()
    project_list = Project.objects.all()
    user_list = User.objects.all()

    return render(request, 'create.html', {'tab_users': user_list,
                                              'priority_list': priority_list, 'status_list': status_list,
                                              'project_list': project_list})


def view(request, ticket_id=1):
    ticket = get_object_or_404(Ticket, pk=ticket_id)
    status_list = Status.objects.all()

    # Paginate Ticket_Comments
    ticket_comments = ticket.ticketcomment_set.order_by('-id')
    paginator = Paginator(ticket_comments, 10)
    try: # Make sure page request is an int. If not, deliver first page.
        page = int(request.GET.get('page', '1'))
    except ValueError:
        page = 1
    try:
        ticket_comments = paginator.page(page)
    except (EmptyPage, InvalidPage):
        ticket_comments = paginator.page(paginator.num_pages)

    return render(request, 'view.html', {'ticket': ticket,
                                         'status_list': status_list, 'ticket_comments': ticket_comments})


def view_all(request):
    # Handle GET parameters
    assigned_filter = request.GET.get("assigned_to")
    created_filter = request.GET.get("created_by")
    priority_filter = request.GET.get("priority")
    status_filter = request.GET.get("status")
    project_filter = request.GET.get("project")
    closed_filter = request.GET.get("show_closed")
    sort_setting = request.GET.get("sort")
    order_setting = request.GET.get("order")

    # Set the default sort and order params
    if not sort_setting:
        sort_setting = "id"
    if not order_setting:
        order_setting = "dsc"

    # Do filtering for GET parameters
    args = {}
    if assigned_filter and assigned_filter != 'unassigned':
        args['assigned_to'] = assigned_filter
    if assigned_filter and assigned_filter == 'unassigned':
        args['assigned_to__exact'] = None
    if created_filter:
        args['created_by'] = created_filter
    if priority_filter:
        args['priority'] = priority_filter
    if status_filter:
        args['status'] = status_filter
    if project_filter:
        args['project'] = project_filter
    tickets = Ticket.objects.filter(**args)

    # Filter out closed tickets
    if not closed_filter or closed_filter.lower() != "true":
        tickets = tickets.exclude(status__hide_by_default=True)

    # Sort the tickets
    sort_filter = sort_setting
    if sort_filter == 'assigned':
        sort_filter = 'assigned_to'
    if sort_filter == 'updated':
        sort_filter = 'update_time'
    if order_setting == 'dsc':
        sort_filter = '-' + sort_filter
    tickets = tickets.order_by(sort_filter)

    # Create filter string
    try:
        filterArray = []
        if assigned_filter and assigned_filter != 'unassigned':
            assigned = User.objects.get(pk=assigned_filter)
            filterArray.append("Assigned to: " + assigned.username)
        if assigned_filter and assigned_filter == 'unassigned':
            filterArray.append("Assigned to: Unassigned")
        if created_filter:
            created = User.objects.get(pk=created_filter)
            filterArray.append("Assigned to: " + created.username)
        if priority_filter:
            priority = Priority.objects.get(pk=priority_filter)
            filterArray.append("Priority: " + priority.name)
        if status_filter:
            status = Status.objects.get(pk=status_filter)
            filterArray.append("Status: " + status.name)
        if project_filter:
            project = Project.objects.get(pk=project_filter)
            filterArray.append("Project: " + project.name)
        if filterArray:
            filter = ', '.join(filterArray)
        else:
            filter = "All"
        filter_message = None
    except Exception as e:
        filter = "Filter Error"
        filter_message = e

    # Handle the case of no visible tickets
    if tickets.count() < 1:
        filter_message = "No tickets meet the current filtering critera."

    # Generate the base URL for showing closed tickets & sorting
    get_dict = request.GET.copy()
    if get_dict.get('show_closed'):
        del get_dict['show_closed']
    if get_dict.get('sort'):
        del get_dict['sort']
    if get_dict.get('order'):
        del get_dict['order']
    base_url = request.path_info + "?" + urlencode(get_dict)

    if closed_filter == 'true':
        show_closed = 'true'
    else:
        show_closed = 'false'

    # Paginate
    paginator = Paginator(tickets, 20)
    try: # Make sure page request is an int. If not, deliver first page.
        page = int(request.GET.get('page', '1'))
    except ValueError:
        page = 1
    try:
        tickets = paginator.page(page)
    except (EmptyPage, InvalidPage):
        tickets = paginator.page(paginator.num_pages)

    # Generate next page link
    pairs = []
    for key in request.GET.keys():
        if key != 'page':
            pairs.append(key + "=" + request.GET.get(key))
    if tickets.has_next():
        pairs.append('page=' + str(tickets.next_page_number()))
    else:
        pairs.append('page=0')
    get_params = '&'.join(pairs)
    next_link = request.path + '?' + get_params

    # Generate previous page link
    pairs = []
    for key in request.GET.keys():
        if key != 'page':
            pairs.append(key + "=" + request.GET.get(key))
    if tickets.has_previous():
        pairs.append('page=' + str(tickets.previous_page_number()))
    else:
        pairs.append('page=0')
    get_params = '&'.join(pairs)
    prev_link = request.path + '?' + get_params

    return render(request, 'view_all.html', {'tickets': tickets, 'filter': filter,
                                                          'filter_message': filter_message, 'base_url': base_url,
                                                          'next_link': next_link, 'prev_link': prev_link,
                                                          'sort': sort_setting, 'order': order_setting,
                                                          'show_closed': show_closed})


def submit_ticket(request):
    ticket = Ticket()
    ticket.project = Project.objects.get(pk=int(request.POST['project']))
    ticket.priority = Priority.objects.get(pk=int(request.POST['priority']))
    ticket.status = Status.objects.get(pk=int(request.POST['status']))
    ticket.created_by = request.user

    # Handle case of unassigned tickets
    assigned_option = request.POST['assigned']
    if assigned_option == 'unassigned':
        ticket.assigned_to = None
    else:
        ticket.assigned_to = User.objects.get(pk=int(assigned_option))

    ticket.creation_time = datetime.now()
    ticket.update_time = datetime.now()
    ticket.name = request.POST['name']
    ticket.desc = request.POST['desc']
    ticket.time_logged = 0
    ticket.save()

    # Email the assigned user if different than creating user
    if ticket.assigned_to is not None and (ticket.assigned_to != ticket.created_by):
        message_preamble = 'You have been assigned a ticket:\n' + \
                           request.get_host() + '/tickets/view/' + str(ticket.id) + '/\n\n'
        email_user(ticket.assigned_to, "Ticket Assigned: " + ticket.name, message_preamble + ticket.desc)

    messages.success(request, "The ticket has been created.")

    return HttpResponseRedirect("/tickets/view/" + str(ticket.id) + "/")


def submit_comment(request, ticket_id):
    text = request.POST["comment-text"]
    time_logged = float(request.POST["comment-time-logged"])
    status = Status.objects.get(pk=int(request.POST["comment-status"]))
    ticket = get_object_or_404(Ticket, pk=ticket_id)

    # Create ticket comment
    comment = TicketComment()

    # Update status if necessary
    if status != ticket.status:
        if text != "":
            text += "\n\n"
        else:
            comment.automated = True
        text += "<strong>Automated Comment:</strong> Status changed from " + ticket.status.name + " to " + status.name
        ticket.status = status
        ticket.save()

    # Set ticket comment properties
    comment.commenter = request.user
    comment.text = text
    comment.ticket = ticket
    comment.time_logged = time_logged
    comment.update_time = datetime.now()
    comment.save()

    # Email the assigned user if different than commenting user
    if ticket.assigned_to is not None and (ticket.assigned_to != comment.commenter):
        message_preamble = 'A ticket you are assigned to has received a comment:\n' + \
                           request.get_host() + '/tickets/view/' + str(ticket.id) + '/\n\n'
        email_user(ticket.assigned_to, "Ticket Comment: " + ticket.name, message_preamble + ticket.desc)

    messages.success(request, "The comment has been added.")

    return HttpResponseRedirect("/tickets/view/" + str(ticket.id) + "/")


def update(request, ticket_id):
    ticket = get_object_or_404(Ticket, pk=ticket_id)

    priority_list = Priority.objects.all()
    status_list = Status.objects.all()
    project_list = Project.objects.all()
    users_list = User.objects.all()

    return render(request, 'update.html', {'ticket': ticket, 'tab_users': users_list,
                                                        'priority_list': priority_list, 'status_list': status_list,
                                                        'project_list': project_list})


def update_ticket(request, ticket_id):
    ticket = get_object_or_404(Ticket, pk=ticket_id)

    project = Project.objects.get(pk=int(request.POST['project']))
    priority = Priority.objects.get(pk=int(request.POST['priority']))
    status = Status.objects.get(pk=int(request.POST['status']))

    # Handle case of unassigned tickets
    assigned_option = request.POST['assigned']
    if assigned_option == 'unassigned':
        assigned_to = None
    else:
        assigned_to = User.objects.get(pk=int(assigned_option))

    name = request.POST['name']
    desc = request.POST['desc']

    # Generate change auto-comment
    changes = []
    if project != ticket.project:
        changes.append("Changed project from " + ticket.project.name + " to " + project.name)
    if priority != ticket.priority:
        changes.append("Changed priority from " + ticket.priority.name + " to " + priority.name)
    if status != ticket.status:
        changes.append("Changed status from " + ticket.status.name + " to " + status.name)
    if assigned_to != ticket.assigned_to:
        changes.append("Changed assigned to from " + str(ticket.assigned_to) + " to " + str(assigned_to))
    if name != ticket.name:
        changes.append("Changed summary from " + ticket.name + " to " + name)
    if desc != ticket.desc:
        changes.append("Updated description")

    # Save changes to the ticket
    ticket.project = project
    ticket.priority = priority
    ticket.status = status
    ticket.assigned_to = assigned_to
    ticket.name = name
    ticket.desc = desc
    ticket.update_time = datetime.now()
    ticket.save()

    # Add the auto-generated comment if necessary
    if len(changes) > 0:
        auto = TicketComment()
        auto.ticket = ticket
        auto.commenter = request.user
        auto.time_logged = 0
        auto.update_time = datetime.now()
        auto.text = "<strong>Automated Comment:</strong> " + ("; ".join(changes))
        auto.automated = True
        auto.save()

    # Email the assigned user if updated
    if ticket.assigned_to is not None and (ticket.assigned_to != auto.commenter):
        message_preamble = 'A ticket you are assigned to you has been updated:\n' +\
                           request.get_host() + '/tickets/view/' + str(ticket.id) + '/\n\n'
        email_user(ticket.assigned_to, "Ticket Update: " + ticket.name, message_preamble + ticket.desc)

    messages.success(request, "The ticket has been updated.")

    return HttpResponseRedirect("/tickets/view/" + str(ticket.id) + "/")


def delete_ticket(request, ticket_id):
    # Get the ticket
    ticket = get_object_or_404(Ticket, pk=ticket_id)

    # Delete all the ticket comments
    TicketComment.objects.filter(ticket=ticket).delete()

    # Delete the ticket
    ticket.delete()

    messages.success(request, "The ticket has been deleted.")
    return HttpResponseRedirect("/tickets/")


def delete_comment(request, comment_id):
    # Get the ticket
    comment = get_object_or_404(TicketComment, pk=comment_id)

    # Delete the ticket
    comment.delete()

    messages.success(request, "The comment has been deleted.")
    return HttpResponseRedirect("/tickets/view/" + str(comment.ticket.id) + "/")


def project(request):
    project_list = Project.objects.all()

    return render(request, 'project.html', {'project_list': project_list})
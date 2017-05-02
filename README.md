# django-simpleticket

The intent of this project is to provide a simple ticket-tracking app that can easily be dropped into 
a new or existing Django site. It aims for bare bones simplicity rather than elaborate features, 
minimizing dependencies and allowing the app to be set up in as little time as possible.

## Requirements
* Python 2.7 or 3.5+
* Django 1.10+

## Setup Instructions
1. Copy the django-simpleticket app into the appropriate directory.
2. Add the add to Django's INSTALLED_APPS list.
3. Run Django's database migration to pick up the app's models.
4. Log into the Django's admin app and create the app's Projects, ticket Priorities and  ticket 
Statuses. The django-simpleticket app requires that at least one project, priority, status and at 
least one User is defined.

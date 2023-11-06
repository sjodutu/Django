from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('events', views.all_events, name="list-events"),
    path('venues', views.all_venues, name="list-venues"),
    path('event/<str:id>/', views.event_detail, name='event-detail'),
    path('venue/<str:id>/', views.venue_detail, name='venue-detail'),
    path('add_event', views.add_event, name='add-event'),
    path('add_venue', views.add_venue, name='add-venue'),
    path('search_events', views.search_events, name='search-events'),
    path('search_venues', views.search_venues, name='search-venues'),
    path('update_event/<str:id>/', views.update_event, name='update-event'),
    path('update_venue/<str:id>/', views.update_venue, name='update-venue'),
    path('delete_event/<str:id>/', views.delete_event, name='delete-event'),
    path('delete_venue/<str:id>/', views.delete_venue, name='delete-venue'),
    path('my_events', views.my_events, name='my-events'),
    path('venue_events/<str:id>/', views.venue_events, name='venue-events'),
    path('admin_approval', views.admin_approval, name='admin-approval'),
    path('venue_text', views.venue_text, name='venue-text'),
]
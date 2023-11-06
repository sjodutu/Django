from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required


from .models import *
from .forms import EventForm, VenueForm, EventFormAdmin
from django.http import HttpResponseRedirect
from django.contrib.auth.models import User
from django.contrib import messages
from django.http import HttpResponse
from django.core.paginator import Paginator

def home(request):
	return render(request, 'events/home.html', {})

def all_events(request):
	event_list = Event.objects.all().order_by('-event_date')
	#current_page = resolve(request.path_info).url_name

	paginator = Paginator(event_list, 5)
	page_number = request.GET.get("page")
	page_obj = paginator.get_page(page_number)
	
	return render(request, 'events/event_list.html', {'event_list':event_list, 'page_obj':page_obj})

def all_venues(request):
	venue_list = Venue.objects.all()

	paginator = Paginator(venue_list, 5)
	page_number = request.GET.get("page")
	page_obj = paginator.get_page(page_number)
	return render(request, 'events/venue_list.html', {'venue_list':venue_list, 'page_obj':page_obj})

@login_required(login_url='login')
def event_detail(request, id):
	event = Event.objects.get(pk=id)
	return render(request, 'events/event_detail.html', {'event':event})

@login_required(login_url='login')
def venue_detail(request, id):
	venue = Venue.objects.get(pk=id)
	return render(request, 'events/venue_detail.html', {'venue':venue})

@login_required(login_url='login')
def add_event(request):
	submitted = False
	if request.method == "POST":
			form = EventForm(request.POST)
			if form.is_valid():
				#form.save()
				event = form.save(commit=False)
				event.manager = request.user # logged in user
				event.save()
				return 	HttpResponseRedirect('/add_event?submitted=True')	
	else:
		form = EventForm
		if 'submitted' in request.GET:
			submitted = True

	return render(request, 'events/add_event.html', {'form':form, 'submitted':submitted})

@login_required(login_url='login')
def add_venue(request):
	submitted = False
	if request.method == "POST":
		form = VenueForm(request.POST)
		if form.is_valid():
			venue = form.save(commit=False)
			venue.owner = request.user.id # logged in user
			venue.save()
			#form.save()
			return 	HttpResponseRedirect('/add_venue?submitted=True')	
	else:
		form = VenueForm
		if 'submitted' in request.GET:
			submitted = True

	return render(request, 'events/add_venue.html', {'form':form, 'submitted':submitted})
	
def search_events(request):
	if request.method == "POST":
		searched = request.POST['searched']
		event_list = Event.objects.filter(description__contains=searched)

		return render(request, 'events/search_events.html', {'searched':searched, 'event_list':event_list})
	else:
		return render(request, 'events/search_events.html', {})
	
def search_venues(request):
	if request.method == "POST":
		searched = request.POST['searched']
		venue_list = Venue.objects.filter(name__icontains=searched)

		return render(request, 'events/search_venue.html', {'searched':searched, 'venue_list':venue_list})
	else:
		return render(request, 'events/search_venue.html', {})

@login_required(login_url='login')
def update_event(request, id):
	event = Event.objects.get(pk=id)
	if request.user.is_superuser:
		form = EventFormAdmin(request.POST or None, instance=event)	
	else:
		form = EventForm(request.POST or None, instance=event)
	
	if form.is_valid():
		form.save()
		return redirect('list-events')

	return render(request, 'events/update_event.html', 
		{'event': event,
		'form':form})

@login_required(login_url='login')
def update_venue(request, id):
	venue = Venue.objects.get(pk=id)
	form = VenueForm(request.POST or None, instance=venue)
	if form.is_valid():
		form.save()
		return redirect('list-venues')
	return render(request, 'events/update_venue.html', {'venue':'venue', 'form':form})

@login_required(login_url='login')
def delete_venue(request, id):
	venue = Venue.objects.get(pk=id)
	venue.delete()
	messages.success(request, "Venue Deleted")
	return redirect('list-venues')

@login_required(login_url='login')
def delete_event(request, id):
	event = Event.objects.get(pk=id)
	event.delete()
	messages.success(request, "Event Deleted")
	return redirect('list-events')

@login_required(login_url='login')
def my_events(request):
	if request.user.is_authenticated:
		me = request.user.id
		events = Event.objects.filter(manager=me)
		return render(request, 'events/my_events.html', {"events":events})
	else:
		messages.success(request, ("You Aren't Authorized To View This Page"))
		return redirect('list-events')

@login_required(login_url='login')
def venue_events(request, id):
	# Grab the venue
	venue = Venue.objects.get(pk=id)	
	# Grab the events from that venue
	events = venue.event_set.all()
	if events:
		return render(request, 'events/venue_events.html', {
			"events":events
			})
	else:
		messages.success(request, ("That Venue Has No Events At This Time..."))
		return redirect('admin_approval')

@login_required(login_url='login')
def admin_approval(request):
	# Get The Venues
	venue_list = Venue.objects.all()
	# Get Counts
	event_count = Event.objects.all().count()
	venue_count = Venue.objects.all().count()
	user_count = User.objects.all().count()

	event_list = Event.objects.all().order_by('-event_date')
	if request.user.is_superuser:
		if request.method == "POST":
			# Get list of checked box id's
			id_list = request.POST.getlist('boxes')

			# Uncheck all events
			event_list.update(approved=False)

			# Update the database
			for x in id_list:
				Event.objects.filter(pk=int(x)).update(approved=True)
			
			# Show Success Message and Redirect
			messages.success(request, ("Event List Approval Has Been Updated!"))
			return redirect('list-events')
		else:
			return render(request, 'events/admin_approval.html',
				{"event_list": event_list,
				"event_count":event_count,
				"venue_count":venue_count,
				"user_count":user_count,
				"venue_list":venue_list})
	else:
		messages.success(request, ("You aren't authorized to view this page!"))
		return redirect('list-events')

# Generate Text File Venue List
@login_required(login_url='login')
def venue_text(request):
	response = HttpResponse(content_type='text/plain')
	response['Content-Disposition'] = 'attachment; filename=venues.txt'
	# Designate The Model
	venues = Venue.objects.all()

	# Create blank list
	lines = []
	# Loop Thu and output
	for venue in venues:
		lines.append(f'{venue.name}\n{venue.address}\n{venue.zip_code}\n{venue.phone}\n{venue.web}\n{venue.email_address}\n\n\n')

	#lines = ["This is line 1\n", 
	#"This is line 2\n",
	#"This is line 3\n\n",
	#"John Elder Is Awesome!\n"]

	# Write To TextFile
	response.writelines(lines)
	return response

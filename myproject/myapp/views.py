import datetime
from urllib import request
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User, auth
from django.contrib import messages
from .models import Trip, Driver, Message, TripPassenger
from django.db import models
from .models import Trip, Driver, Message, TripPassenger, MessageRead


def index(request):
    trips = Trip.objects.filter(is_accepted=True, date__gte=datetime.date.today())
    joined_trip_ids = []
    my_trips = []
    pending_trips = []
    if request.user.is_authenticated:
        joined_trip_ids = TripPassenger.objects.filter(
            user=request.user).values_list('trip_id', flat=True)
        my_trips = Trip.objects.filter(requested_by=request.user, is_accepted=True)
        pending_trips = Trip.objects.filter(requested_by=request.user, is_accepted=False)
    unread_counts = {}
    if request.user.is_authenticated:
        for trip in trips:
            read = MessageRead.objects.filter(user=request.user, trip=trip).first()
            if read:
                unread_counts[trip.id] = Message.objects.filter(trip=trip, timestamp__gt=read.last_read).count()
            else:
                unread_counts[trip.id] = Message.objects.filter(trip=trip).count()
    return render(request, 'index.html', {
        'trips': trips,
        'joined_trip_ids': joined_trip_ids,
        'my_trips': my_trips,
        'pending_trips': pending_trips,
        'unread_counts': unread_counts,
})


def choose(request):
    return render(request, 'choose.html')


# ───── USER AUTH ─────

def register(request):
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        password2 = request.POST['password2']
        if password == password2:
            if not email.endswith('@rhodes.edu'):
                messages.info(request, 'Only @rhodes.edu email addresses are allowed.')
                return redirect('register')
            if User.objects.filter(email=email).exists():
                messages.info(request, 'Email Already Used')
                return redirect('register')
            else:
                user = User.objects.create_user(username=username, password=password, email=email)
                user.save()
                return redirect('login')
        else:
            messages.info(request, 'Passwords Not The Same')
            return redirect('register')
    else:
        return render(request, 'register.html')


def user_login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = auth.authenticate(username=username, password=password)
        if user is not None:
            auth.login(request, user)
            if hasattr(user, 'driver'):
                return redirect('driver_dashboard')
            else:
                return redirect('index')
        else:
            messages.info(request, 'Invalid Credentials')
            return redirect('login')
    else:
        return render(request, 'login.html')


def user_logout(request):
    auth.logout(request)
    return redirect('choose')


# ───── DRIVER AUTH ─────

def driver_register(request):
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        password2 = request.POST['password2']
        name = request.POST['name']
        car_model = request.POST['car_model']
        license_plate = request.POST['license_plate']
        if password != password2:
            messages.info(request, 'Passwords Not The Same')
            return redirect('driver_register')
        if not email.endswith('@rhodes.edu'):
            messages.info(request, 'Only @rhodes.edu email addresses are allowed.')
            return redirect('driver_register')
        if User.objects.filter(email=email).exists():
            messages.info(request, 'Email Already Used')
            return redirect('driver_register')
        user = User.objects.create_user(username=username, password=password, email=email)
        user.save()
        Driver.objects.create(user=user, name=name, car_model=car_model, license_plate=license_plate)
        return redirect('driver_login')
    else:
        return render(request, 'driver_register.html')


def driver_login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = auth.authenticate(username=username, password=password)
        if user is not None and hasattr(user, 'driver'):
            auth.login(request, user)
            return redirect('driver_dashboard')
        else:
            messages.info(request, 'Invalid driver credentials')
            return redirect('driver_login')
    else:
        return render(request, 'driver_login.html')


def driver_logout(request):
    auth.logout(request)
    return redirect('choose')


# ───── DRIVER DASHBOARD ─────

def driver_dashboard(request):
    if not hasattr(request.user, 'driver'):
        return redirect('driver_login')
    pending_trips = Trip.objects.filter(is_accepted=False)
    my_trips = Trip.objects.filter(accepted_by=request.user.driver)
    return render(request, 'driver_dashboard.html', {
        'pending_trips': pending_trips,
        'my_trips': my_trips
    })


def accept_trip(request, trip_id):
    if not hasattr(request.user, 'driver'):
        return redirect('driver_login')
    trip = get_object_or_404(Trip, id=trip_id)
    trip.accepted_by = request.user.driver
    trip.is_accepted = True
    trip.save()
    return redirect('driver_dashboard')


# ───── TRIPS ─────

def user_post_trip(request):
    if not request.user.is_authenticated:
        messages.info(request, 'You must be logged in to post a trip')
        return redirect('login')
    if request.method == 'POST':
        name = request.POST['name']
        import datetime
        date = request.POST['date']
        time = request.POST['time']
        trip_date = datetime.datetime.strptime(date, "%Y-%m-%d").date()
        trip_time = datetime.datetime.strptime(time, "%H:%M").time()
        now = datetime.datetime.now()
        trip_datetime = datetime.datetime.combine(trip_date, trip_time)
        if trip_datetime < now:
            messages.error(request, "Cannot post a trip in the past.")
            return redirect('post_trip')
        latitude = request.POST.get('latitude') or None
        longitude = request.POST.get('longitude') or None
        location_name = request.POST.get('location_name') or None
        trip = Trip.objects.create(
            name=name,
            date=date,
            time=time,
            num_of_people=1,
            requested_by=request.user,
            is_accepted=False,
            latitude=latitude,
            longitude=longitude,
            location_name=location_name
        )
        TripPassenger.objects.create(trip=trip, user=request.user)
        messages.info(request, 'Trip request submitted! Waiting for a driver to accept.')
        return redirect('index')
    else:
        return render(request, 'post-trip.html')


def driver_post_trip(request):
    if not hasattr(request.user, 'driver'):
        return redirect('driver_login')
    if request.method == 'POST':
        name = request.POST['name']
        date = request.POST['date']
        time = request.POST['time']
        latitude = request.POST.get('latitude') or None
        longitude = request.POST.get('longitude') or None
        location_name = request.POST.get('location_name') or None
        Trip.objects.create(
            name=name,
            date=date,
            time=time,
            num_of_people=0,
            requested_by=None,
            accepted_by=request.user.driver,
            is_accepted=True,
            latitude=latitude,
            longitude=longitude,
            location_name=location_name
        )
        messages.success(request, 'Trip posted successfully!')
        return redirect('driver_dashboard')
    return render(request, 'driver_post_trip.html')


# ───── CHAT ─────

def chat(request, trip_id):
    trip = get_object_or_404(Trip, id=trip_id)
    is_driver = hasattr(request.user, 'driver')
    is_requester = trip.requested_by == request.user
    is_assigned_driver = is_driver and trip.accepted_by == request.user.driver
    is_passenger = TripPassenger.objects.filter(trip=trip, user=request.user).exists()
    if not (is_requester or is_assigned_driver or is_passenger):
        return redirect('index')
    if request.method == 'POST':
        content = request.POST['content']
        Message.objects.create(trip=trip, sender=request.user, content=content)
        return redirect('chat', trip_id=trip_id)
    messages_list = Message.objects.filter(trip=trip).order_by('timestamp')
    passengers = TripPassenger.objects.filter(trip=trip).select_related('user')
    MessageRead.objects.update_or_create(
    user=request.user, trip=trip,
    defaults={'last_read': datetime.datetime.now()}
    )
    return render(request, 'chat.html', {
        'trip': trip,
        'messages_list': messages_list,
        'passengers': passengers
    })


# ───── JOIN TRIP ─────

def join_trip(request, trip_id):
    if not request.user.is_authenticated:
        return redirect('login')
    trip = get_object_or_404(Trip, id=trip_id)
    if trip.requested_by == request.user:
        messages.info(request, "You can't join your own trip.")
        return redirect('index')
    if hasattr(request.user, 'driver'):
        messages.info(request, "Drivers can't join trips as passengers.")
        return redirect('index')
    already_joined = TripPassenger.objects.filter(trip=trip, user=request.user).exists()
    if already_joined:
        messages.info(request, "You already joined this trip!")
        return redirect('index')
    TripPassenger.objects.create(trip=trip, user=request.user)
    Trip.objects.filter(id=trip_id).update(num_of_people=models.F('num_of_people') + 1)
    messages.success(request, f"You joined {trip.name}!")
    return redirect('index')

def delete_trip(request, trip_id):
    trip = get_object_or_404(Trip, id=trip_id)
    if request.user != trip.requested_by:
        return redirect('index')
    trip.delete()
    messages.success(request, 'Trip deleted successfully!')
    return redirect('index')
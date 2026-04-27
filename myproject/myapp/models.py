from django.db import models
from django.contrib.auth.models import User


class Driver(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    car_model = models.CharField(max_length=100)
    license_plate = models.CharField(max_length=20)

    def __str__(self):
        return self.name


class Trip(models.Model):
    requested_by = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    accepted_by = models.ForeignKey(Driver, on_delete=models.SET_NULL, null=True, blank=True)
    name = models.CharField(max_length=200)
    date = models.DateField()
    time = models.TimeField()
    num_of_people = models.PositiveIntegerField()
    is_accepted = models.BooleanField(default=False)
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    location_name = models.CharField(max_length=300, null=True, blank=True)

    def __str__(self):
        return self.name

    @property
    def space_availability(self):
        if self.num_of_people < 4:
            return "Yes"
        else:
            return "No"


class Message(models.Model):
    trip = models.ForeignKey(Trip, on_delete=models.CASCADE)
    sender = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.sender.username}: {self.content[:30]}"
    
class TripPassenger(models.Model):
    trip = models.ForeignKey(Trip, on_delete=models.CASCADE, related_name='passengers')
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('trip', 'user')

    def __str__(self):
        return f"{self.user.username} on {self.trip.name}"
from django.db import models
from django.conf import settings


from django.contrib.auth import get_user_model
User = get_user_model()

# Choices
# ----------------------------------------------------------------------
class PlanStatus(models.TextChoices):
    PLANNED = 'PLANNED','Planned'
    ACTIVE = 'ACTIVE', 'Active'
    COMPLETED = 'COMPLETED', 'Completed'
    CANCELLED = 'CANCELLED', 'Cancelled'

class TransportMode(models.TextChoices):
    FLIGHT = 'FLIGHT', 'Flight'
    TRAIN = 'TRAIN', 'Train'
    BUS = 'BUS', 'Bus'
    SEEKING = 'SEEK', 'Seeking a Ride'
    OTHER = 'OTHER', 'Other'


# User data
# ----------------------------------------------------------------------
class TravelPlan(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='travel_plans'
    )

    title = models.CharField(
        max_length=150
    )
    
    status = models.CharField(
        max_length=10,
        choices=PlanStatus.choices,
        default=PlanStatus.PLANNED
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.title} (by {self.user.username})"

    class Meta:
        ordering = ['-created_at']

    @property
    def first_trip(self):
        return self.trips.first()

    @property
    def last_trip(self):
        return self.trips.last()
    
    @property
    def all_passengers(self):
        return User.objects.filter(models.Q(joined_trips__plan=self) | models.Q(travel_plans = self)).distinct()



class Trip(models.Model):

    plan = models.ForeignKey(
        TravelPlan,
        on_delete=models.CASCADE,
        related_name='trips',
    )

    title = models.CharField(
        max_length=150,
    )



    origin_name = models.CharField(
        max_length=255,
    )
    origin_lat = models.CharField(
        max_length=50, null=True, blank=True
    )
    origin_lon = models.CharField(
        max_length=50, null=True, blank=True
    )



    destination_name = models.CharField(
        max_length=255,
    )
    destination_lat = models.CharField(
        max_length=50, null=True, blank=True
    )
    destination_lon = models.CharField(
        max_length=50, null=True, blank=True
    )

    departure_time = models.DateTimeField()
    estimated_arrival_time = models.DateTimeField(
        null=True, blank=True
    )

    transport_mode = models.CharField(
        max_length=6,
        choices=TransportMode.choices,
        default=TransportMode.TRAIN
    )

    passengers = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name='joined_trips',
        blank=True,
        help_text="Students who have joined this trip",
    )

    notes = models.TextField(
        blank=True,
    )

    status = models.CharField(
        max_length=10,
        choices=PlanStatus.choices,
        default=PlanStatus.PLANNED
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['departure_time']



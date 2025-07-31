from django.contrib.auth.models import AbstractUser
from django.db import models

# Used lazy relationship to avoid not-defined error
# due to class declaration position
class User(AbstractUser):
    watchlist = models.ManyToManyField('Listing',
                                       blank=True,
                                       related_name="watchers")
    
    def __str__(self):
        return f"{super().username} | {super().first_name} {super().last_name}"
    
class Category(models.Model):
    title = models.CharField(max_length=64)

    def __str__(self):
        return f"{self.title}"

class Listing(models.Model):
    active = models.BooleanField(default=True)
    author = models.ForeignKey(User,
                               on_delete=models.CASCADE)
    created_at = models.DateTimeField()
    title = models.CharField(max_length=64)
    description = models.TextField(max_length=300)
    img_url = models.CharField(max_length=200)
    category = models.ForeignKey(Category,
                                 blank=True,
                                 on_delete=models.CASCADE)
    
    def __str__(self):
        return f"{"ACTIVE" if self.active  else "INACTIVE"} | {self.title} ({self.author})"

class Bid(models.Model):
    user = models.ForeignKey(User,
                             on_delete=models.CASCADE)
    listing = models.ForeignKey(Listing,
                                on_delete=models.CASCADE,
                                related_name="bids")
    ammount = models.FloatField()
    created_at = models.DateTimeField()

    def __str__(self):
        return f"{self.listing} -> {self.ammount} ({self.user})"

class Comment(models.Model):
    author = models.ForeignKey(User,
                               on_delete=models.CASCADE)
    listing = models.ForeignKey(Listing,
                                on_delete=models.CASCADE,
                                related_name="comments")
    body = models.TextField(max_length=300)
    created_at = models.DateTimeField()

    def __str__(self):
        return f"{self.listing} - {self.author} ({self.created_at})"

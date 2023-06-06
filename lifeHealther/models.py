from django.db import models
from django.contrib.auth.models import User


class MyUser(models.Model):
    ROLES = [
        ("Mo", "Moder"),
        ("Ad", "Administrator"),
        ("Cr", "Creator"),
        ("Cu", "Customer"),
    ]
    id = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        primary_key=True,
    )
    role = models.CharField(max_length=2, choices=ROLES)


class Administrator(models.Model):
    id = models.OneToOneField(
        MyUser,
        on_delete=models.CASCADE,
        primary_key=True,
    )
    firstName = models.CharField(max_length=50)
    lastName = models.CharField(max_length=50)


class Moderator(models.Model):
    id = models.OneToOneField(
        MyUser,
        on_delete=models.CASCADE,
        primary_key=True,
    )
    firstName = models.CharField(max_length=50)
    lastName = models.CharField(max_length=50)


class Customer(models.Model):
    id = models.OneToOneField(
        MyUser,
        on_delete=models.CASCADE,
        primary_key=True,
    )
    payment_details = models.CharField(blank=True, max_length=400)


class Creator(models.Model):
    id = models.OneToOneField(
        MyUser,
        on_delete=models.CASCADE,
        primary_key=True,
    )
    info = models.TextField()
    is_validated = models.BooleanField(default=False)
    payment_details = models.CharField(max_length=400)


class Subscription(models.Model):
    creator = models.ForeignKey(Creator, on_delete=models.CASCADE)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)


class SponsorTier(models.Model):
    creator = models.ForeignKey(Creator, on_delete=models.CASCADE)
    price = models.IntegerField()
    name = models.CharField(max_length=50)


class Content(models.Model):
    creator = models.ForeignKey(Creator, on_delete=models.CASCADE)
    content_type = models.CharField(max_length=50)
    like_count = models.IntegerField()
    is_paid = models.BooleanField(default=False)


class ContentLike(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    content = models.ForeignKey(Content, on_delete=models.CASCADE)


class Comment(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    text = models.CharField(max_length=500)
    like_count = models.IntegerField()
    content = models.ForeignKey(Content, on_delete=models.CASCADE)


class CommentLike(models.Model):
    comment = models.ForeignKey(Comment, on_delete=models.CASCADE)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)


class SponsorSubscription(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    sponsor_tier = models.ForeignKey(SponsorTier, on_delete=models.CASCADE)


class SponsorTierContent(models.Model):
    content = models.ForeignKey(Content, on_delete=models.CASCADE)
    sponsor_tier = models.ForeignKey(SponsorTier, on_delete=models.CASCADE)

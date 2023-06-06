from rest_framework import serializers
from lifeHealther.models import (
    User,
    MyUser,
    Administrator,
    Moderator,
    Customer,
    Creator,
    Content,
    Comment,
    CommentLike,
    ContentLike,
    SponsorTier,
    SponsorTierContent,
    SponsorSubscription,
    Subscription
)


class UserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'password']


class MyUserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = MyUser
        fields = ['id', 'role']


class AdministratorSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Administrator
        fields = ['id', 'firstName', 'lastName']


class CustomerSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Customer
        fields = ['id', 'payment details']


class ModeratorSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Moderator
        fields = ['id', 'firstName', 'lastName']


class CreatorSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Creator
        fields = ['id', 'info', 'is validated', 'payment details']


class SubscriptionSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Subscription
        fields = ['id', 'creator', 'customer']


class SponsorTierSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = SponsorTier
        fields = ['id', 'creator', 'price', 'name']


class ContentSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Content
        fields = ['id', 'creator', 'content type', 'like count', 'is paid']


class ContentLikeSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = ContentLike
        fields = ['id', 'customer', 'content']


class CommentSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Comment
        fields = ['id', 'customer', 'text', 'like count', 'content']


class CommentLikeSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = CommentLike
        fields = ['id', 'customer', 'comment']


class SponsorSubscriptionSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = SponsorSubscription
        fields = ['id', 'customer', 'sponsor tier']


class SponsorTierContentSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = SponsorTierContent
        fields = ['id', 'content', 'sponsor tier']


class RegistrationSerializers(serializers.HyperlinkedModelSerializer):
    class Meta:
        fields = ['login', 'role', 'password']

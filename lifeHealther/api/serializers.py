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
    id = UserSerializer(required=True)
    class Meta:
        model = MyUser
        fields = ['id', 'role']

    def create(self, validated_data):
        user_data = validated_data.pop('id')
        id = UserSerializer.create(UserSerializer(), validated_data=user_data)
        my_user, created = MyUser.objects.update_or_create(id=id,
                                                                role=validated_data.pop('role'))
        return my_user
#

class AdministratorSerializer(serializers.HyperlinkedModelSerializer):
    id = MyUserSerializer(required=True)
    class Meta:
        model = Administrator
        fields = ['id', 'firstName', 'lastName']

    def create(self, validated_data):
        my_user_data = validated_data.pop('id')
        id = MyUserSerializer.create(MyUserSerializer(), validated_data=my_user_data)
        admin, created = Administrator.objects.update_or_create(id=id,
                                                                firstName=validated_data.pop('firstName'),
                                                                lastName=validated_data.pop('lastName'))
        return admin


class CustomerSerializer(serializers.HyperlinkedModelSerializer):
    id = MyUserSerializer(required=True)
    class Meta:
        model = Customer
        fields = ['id']

    def create(self, validated_data):
        my_user_data = validated_data.pop('id')
        id = MyUserSerializer.create(MyUserSerializer(), validated_data=my_user_data)
        customer, created = Customer.objects.update_or_create(id=id,
                                                                payment_details=" ")
        return customer


class ModeratorSerializer(serializers.HyperlinkedModelSerializer):
    id = UserSerializer(required=True)
    class Meta:
        model = Moderator
        fields = ['id', 'firstName', 'lastName']

    def create(self, validated_data):
        my_user_data = validated_data.pop('id')
        id = MyUserSerializer.create(MyUserSerializer(), validated_data=my_user_data)
        moder, created = Moderator.objects.update_or_create(id=id,
                                                                firstName=validated_data.pop('firstName'),
                                                                lastName=validated_data.pop('lastName'))
        return moder


class CreatorSerializer(serializers.HyperlinkedModelSerializer):
    id = MyUserSerializer(required=True)
    class Meta:
        model = Creator
        fields = ['id']

    def create(self, validated_data):
        my_user_data = validated_data.pop('id')
        id = MyUserSerializer.create(MyUserSerializer(), validated_data=my_user_data)
        creator, created = Creator.objects.update_or_create(id=id,
                                                            info=" ",
                                                            is_validated=False,
                                                            payment_details=" ")
        return creator


class SubscriptionSerializer(serializers.HyperlinkedModelSerializer):
    creator = serializers.RelatedField(read_only=True)
    customer = serializers.RelatedField(read_only=True)
    class Meta:
        model = Subscription
        fields = ['id', 'creator', 'customer']

    def create(self, validated_data):
        customer = Customer.objects.get(id=int(validated_data.pop('customer')))
        creator = Creator.objects.get(id=int(validated_data.pop('creator')))
        sub, created = Content.objects.update_or_create(customer=customer,
                                                            creator=creator)
        return sub

    def to_representation(self, instance):
        representation = {
            "id": instance.id,
            "customer": instance.customer.id_id,
            "creator": instance.creator.id_id,
        }
        return representation


class SponsorTierSerializer(serializers.HyperlinkedModelSerializer):
    creator = serializers.RelatedField(read_only=True)
    class Meta:
        model = SponsorTier
        fields = ['id', 'creator', 'price', 'name']

    def create(self, validated_data):
        creator = Creator.objects.get(id=int(validated_data.pop('creator')))
        sponsor_tier, created = SponsorTier.objects.update_or_create(creator=creator,
                                                            price=validated_data.pop('price'),
                                                            name=validated_data.pop("name"))
        return sponsor_tier

    def to_representation(self, instance):
        representation = {
            "id": instance.id,
            "creator": instance.creator.id_id,
            "price": instance.price,
            "name": instance.name
        }
        return representation


class ContentSerializer(serializers.HyperlinkedModelSerializer):
    creator = serializers.RelatedField(read_only=True)
    class Meta:
        model = Content
        fields = ['id', 'creator', 'content_type', 'like_count', 'is_paid']

    def create(self, validated_data):
        creator = Creator.objects.get(id=int(validated_data.pop('creator')))
        content, created = Content.objects.update_or_create(creator=creator,
                                                            content_type=validated_data.pop('content_type'),
                                                            like_count=validated_data.pop("like_count"),
                                                            is_paid=validated_data.pop('is_paid'))
        return content

    def to_representation(self, instance):
        representation = {
            "id": instance.id,
            "creator": instance.creator.id_id,
            "content_type": instance.content_type,
            "like_count": instance.like_count,
            "is_paid": instance.is_paid
        }
        return representation


class ContentLikeSerializer(serializers.HyperlinkedModelSerializer):
    customer_id = serializers.RelatedField(read_only=True)
    content_id = serializers.RelatedField(read_only=True)

    class Meta:
        model = ContentLike
        fields = ['id', 'customer_id', 'content_id']

    def create(self, validated_data):
        customer = Customer.objects.get(id=int(validated_data.pop('customer')))
        content = Content.objects.get(id=int(validated_data.pop('content')))
        like, created = Content.objects.update_or_create(customer=customer,
                                                            content=content)
        return like

    def to_representation(self, instance):
        representation = {
            "id": instance.id,
            "customer": instance.customer.id_id,
            "content": instance.content.id,
        }
        return representation


class CommentSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Comment
        fields = ['id', 'customer', 'text', 'like count', 'content']


class CommentLikeSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = CommentLike
        fields = ['id', 'customer', 'comment']


class SponsorSubscriptionSerializer(serializers.HyperlinkedModelSerializer):
    customer = serializers.RelatedField(read_only=True)
    sponsor_tier = serializers.RelatedField(read_only=True)
    class Meta:
        model = SponsorSubscription
        fields = ['id', 'customer', 'sponsor_tier']

    def create(self, validated_data):
        sponsor_tier = SponsorTier.objects.get(id=int(validated_data.pop('sponsor_tier')))
        customer = Customer.objects.get(id=int(validated_data.pop('customer')))
        sponsor_sub, created = Content.objects.update_or_create(sponsor_tier=sponsor_tier,
                                                            customer=customer)
        return sponsor_sub

    def to_representation(self, instance):
        representation = {
            "id": instance.id,
            "sponsor_tier": instance.sponsor_tier.id,
            "customer": instance.customer.id_id,
        }
        return representation


class SponsorTierContentSerializer(serializers.HyperlinkedModelSerializer):
    sponsor_tier = serializers.RelatedField(read_only=True)
    content = serializers.RelatedField(read_only=True)
    class Meta:
        model = SponsorTierContent
        fields = ['id', 'content', 'sponsor_tier']

    def create(self, validated_data):
        sponsor_tier = SponsorTier.objects.get(id=int(validated_data.pop('sponsor_tier')))
        content = Content.objects.get(id=int(validated_data.pop('content')))
        tier_cont, created = Content.objects.update_or_create(sponsor_tier=sponsor_tier,
                                                            content=content)
        return tier_cont

    def to_representation(self, instance):
        representation = {
            "id": instance.id,
            "sponsor_tier": instance.sponsor_tier.id,
            "content": instance.content.id,
        }
        return representation


class RegistrationSerializers(serializers.HyperlinkedModelSerializer):
    class Meta:
        fields = ['login', 'role', 'password']

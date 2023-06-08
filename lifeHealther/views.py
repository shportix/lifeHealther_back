from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
import pymongo
from bson.json_util import dumps
import requests
from lifeHealther.models import (
    MyUser,
    Administrator,
    Moderator, Customer,
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
from lifeHealther.api.serializers import (
    UserSerializer,
    MyUserSerializer,
    AdministratorSerializer,
    CustomerSerializer,
    ModeratorSerializer,
    CreatorSerializer,
    SubscriptionSerializer,
    SponsorTierSerializer,
    ContentSerializer,
    ContentLikeSerializer,
    CommentSerializer,
    CommentLikeSerializer,
    SponsorSubscriptionSerializer,
    SponsorTierContentSerializer,
    RegistrationSerializers
)


#test mongo
@api_view(['GET', ])
def api_create_test_mongo_view(request):
    client = pymongo.MongoClient('mongodb+srv://lifehealther:DmdIHgLhwpJDJ6Sg@lifehealthermongodb.vtllcje.mongodb.net/')
    dbname = client['lifehealthermongodb']
    collection_name = dbname["medicinedetails"]
    medicine_1 = {
        "medicine_id": 1,
        "common_name": "Paracetamol",
        "scientific_name": "",
        "available": ["Y", "p"],
        "category": "fever"
    }
    medicine_2 = {
        "medicine_id": "RR000342522",
        "common_name": "Metformin",
        "scientific_name": "",
        "available": "Y",
        "category": "type 2 diabetes"
    }
    # Insert the documents
    collection_name.insert_many([medicine_1, medicine_2])
    res = collection_name.find({})
    list_res = list(res)
    json_res = dumps(list_res)
    return  Response(json_res, status=status.HTTP_200_OK)


# //////user//////
@api_view(['POST', ])
def api_create_user_view(request):
    user = User()

    if request.method == "POST":
        serializer = UserSerializer(user, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', ])
def api_get_user_view(request, user_id):
    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if request.method == "GET":
        serializer = UserSerializer(user)
        return Response(serializer.data)


@api_view(['PUT', ])
def api_update_user_view(request, user_id):
    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if request.method == "PUT":
        serializer = UserSerializer(user, data=request.data)
        if serializer.is_valid():
            serializer.save()
            data = {
                "success": "update successful"
            }
            return Response(data=data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['DELETE', ])
def api_delete_user_view(request, user_id):
    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if request.method == "DELETE":
        operation = user.delete()
        data = {}
        if operation:
            data["success"] = "delete successful"
        else:
            data["failure"] = "delete failed"
        return Response(data=data)


# //////myUser//////
@api_view(['POST', ])
def api_create_my_user_view(request):
    my_user = MyUser()
    if request.method == "POST":
        serializer = MyUserSerializer(my_user, data=request.data)
        if serializer.is_valid():
            my_user = serializer.create(validated_data=request.data)
            my_user_data = {
                "id": my_user.id_id,
                "role": my_user.role
            }
            return Response(my_user_data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', ])
def api_get_my_user_view(request, my_user_id):
    try:
        my_user = MyUser.objects.get(id_id=my_user_id)
    except MyUser.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if request.method == "GET":
        user_data = {
            "id": my_user.id,
            "role": my_user.role
        }
        return Response(data=user_data)


@api_view(['PUT', ])
def api_update_my_user_view(request, my_user_id):
    try:
        my_user = MyUser.objects.get(id=my_user_id)
    except MyUser.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if request.method == "PUT":
        serializer = MyUserSerializer(my_user, data=request.data)
        if serializer.is_valid():
            serializer.save()
            data = {
                "success": "update successful"
            }
            return Response(data=data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['DELETE', ])
def api_delete_my_user_view(request, my_user_id):
    try:
        my_user = MyUser.objects.get(id=my_user_id)
    except MyUser.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if request.method == "DELETE":
        operation = my_user.delete()
        data = {}
        if operation:
            data["success"] = "delete successful"
        else:
            data["failure"] = "delete failed"
        return Response(data=data)


# //////creator//////
@api_view(['POST', ])
def api_create_creator_view(request):
    creator = Creator()
    if request.method == "POST":
        serializer = CreatorSerializer(creator, data=request.data)
        if serializer.is_valid():
            creator = serializer.create(validated_data=request.data)
            data = {
                "id": creator.id_id
            }
            return Response(data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', ])
def api_get_creator_view(request, creator_id):
    try:
        creator = Creator.objects.get(id=creator_id)
    except Creator.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if request.method == "GET":
        serializer = CreatorSerializer(creator)
        return Response(serializer.data)


@api_view(['PUT', ])
def api_update_creator_view(request, creator_id):
    try:
        creator = Creator.objects.get(id=creator_id)
    except Creator.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if request.method == "PUT":
        serializer = CreatorSerializer(creator, data=request.data)
        if serializer.is_valid():
            serializer.save()
            data = {
                "success": "update successful"
            }
            return Response(data=data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['DELETE', ])
def api_delete_creator_view(request, creator_id):
    try:
        creator = Creator.objects.get(id=creator_id)
    except Creator.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if request.method == "DELETE":
        operation = creator.delete()
        data = {}
        if operation:
            data["success"] = "delete successful"
        else:
            data["failure"] = "delete failed"
        return Response(data=data)


# //////customer//////
@api_view(['POST', ])
def api_create_customer_view(request):
    customer = Customer()
    if request.method == "POST":
        serializer = CustomerSerializer(customer, data=request.data)
        if serializer.is_valid():
            customer = serializer.create(validated_data=request.data)
            data = {
                "id": customer.id_id
            }
            return Response(data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', ])
def api_get_customer_view(request, customer_id):
    try:
        customer = Customer.objects.get(id=customer_id)
    except Customer.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if request.method == "GET":
        serializer = CustomerSerializer(customer)
        return Response(serializer.data)


@api_view(['PUT', ])
def api_update_customer_view(request, customer_id):
    try:
        customer = Customer.objects.get(id=customer_id)
    except Customer.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if request.method == "PUT":
        serializer = CustomerSerializer(customer, data=request.data)
        if serializer.is_valid():
            serializer.save()
            data = {
                "success": "update successful"
            }
            return Response(data=data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['DELETE', ])
def api_delete_customer_view(request, customer_id):
    try:
        customer = Customer.objects.get(id=customer_id)
    except Customer.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if request.method == "DELETE":
        operation = customer.delete()
        data = {}
        if operation:
            data["success"] = "delete successful"
        else:
            data["failure"] = "delete failed"
        return Response(data=data)


# //////administrator//////
@api_view(['POST', ])
def api_create_administrator_view(request):
    administrator = Administrator()

    if request.method == "POST":
        serializer = AdministratorSerializer(administrator, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', ])
def api_get_administrator_view(request, administrator_id):
    try:
        administrator = Administrator.objects.get(id=administrator_id)
    except Administrator.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if request.method == "GET":
        serializer = AdministratorSerializer(administrator)
        return Response(serializer.data)


@api_view(['PUT', ])
def api_update_administrator_view(request, administrator_id):
    try:
        administrator = Administrator.objects.get(id=administrator_id)
    except Administrator.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if request.method == "PUT":
        serializer = AdministratorSerializer(administrator, data=request.data)
        if serializer.is_valid():
            serializer.save()
            data = {
                "success": "update successful"
            }
            return Response(data=data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['DELETE', ])
def api_delete_administrator_view(request, administrator_id):
    try:
        administrator = Administrator.objects.get(id=administrator_id)
    except Administrator.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if request.method == "DELETE":
        operation = administrator.delete()
        data = {}
        if operation:
            data["success"] = "delete successful"
        else:
            data["failure"] = "delete failed"
        return Response(data=data)


# //////moderator//////
@api_view(['POST', ])
def api_create_moderator_view(request):
    moderator = Moderator()

    if request.method == "POST":
        serializer = ModeratorSerializer(moderator, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', ])
def api_get_moderator_view(request, moderator_id):
    try:
        moderator = Moderator.objects.get(id=moderator_id)
    except Moderator.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if request.method == "GET":
        serializer = ModeratorSerializer(moderator)
        return Response(serializer.data)


@api_view(['PUT', ])
def api_update_moderator_view(request, moderator_id):
    try:
        moderator = Moderator.objects.get(id=moderator_id)
    except Moderator.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if request.method == "PUT":
        serializer = ModeratorSerializer(moderator, data=request.data)
        if serializer.is_valid():
            serializer.save()
            data = {
                "success": "update successful"
            }
            return Response(data=data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['DELETE', ])
def api_delete_moderator_view(request, moderator_id):
    try:
        moderator = Moderator.objects.get(id=moderator_id)
    except Moderator.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if request.method == "DELETE":
        operation = moderator.delete()
        data = {}
        if operation:
            data["success"] = "delete successful"
        else:
            data["failure"] = "delete failed"
        return Response(data=data)


# //////content//////
@api_view(['POST', ])
def api_create_content_view(request):
    content = Content()

    if request.method == "POST":
        serializer = ContentSerializer(content, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', ])
def api_get_content_view(request, content_id):
    try:
        content = Content.objects.get(id=content_id)
    except Content.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if request.method == "GET":
        serializer = ContentSerializer(content)
        return Response(serializer.data)


@api_view(['PUT', ])
def api_update_content_view(request, content_id):
    try:
        content = Content.objects.get(id=content_id)
    except Content.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if request.method == "PUT":
        serializer = ContentSerializer(content, data=request.data)
        if serializer.is_valid():
            serializer.save()
            data = {
                "success": "update successful"
            }
            return Response(data=data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['DELETE', ])
def api_delete_content_view(request, content_id):
    try:
        content = Content.objects.get(id=content_id)
    except Content.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if request.method == "DELETE":
        operation = content.delete()
        data = {}
        if operation:
            data["success"] = "delete successful"
        else:
            data["failure"] = "delete failed"
        return Response(data=data)


# //////comment//////
@api_view(['POST', ])
def api_create_comment_view(request):
    comment = Comment()

    if request.method == "POST":
        serializer = CommentSerializer(comment, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', ])
def api_get_comment_view(request, comment_id):
    try:
        comment = Comment.objects.get(id=comment_id)
    except Comment.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if request.method == "GET":
        serializer = ContentSerializer(comment)
        return Response(serializer.data)


@api_view(['PUT', ])
def api_update_comment_view(request, comment_id):
    try:
        comment = Comment.objects.get(id=comment_id)
    except Comment.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if request.method == "PUT":
        serializer = CommentSerializer(comment, data=request.data)
        if serializer.is_valid():
            serializer.save()
            data = {
                "success": "update successful"
            }
            return Response(data=data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['DELETE', ])
def api_delete_comment_view(request, comment_id):
    try:
        comment = Comment.objects.get(id=comment_id)
    except Comment.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if request.method == "DELETE":
        operation = comment.delete()
        data = {}
        if operation:
            data["success"] = "delete successful"
        else:
            data["failure"] = "delete failed"
        return Response(data=data)


# //////comment_like//////
@api_view(['POST', ])
def api_create_comment_like_view(request):
    comment_like = CommentLike()

    if request.method == "POST":
        serializer = CommentLikeSerializer(comment_like, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', ])
def api_get_comment_like_view(request, comment_like_id):
    try:
        comment_like = CommentLike.objects.get(id=comment_like_id)
    except CommentLike.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if request.method == "GET":
        serializer = ContentLikeSerializer(comment_like)
        return Response(serializer.data)


@api_view(['PUT', ])
def api_update_comment_like_view(request, comment_like_id):
    try:
        comment_like = CommentLike.objects.get(id=comment_like_id)
    except CommentLike.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if request.method == "PUT":
        serializer = CommentLikeSerializer(comment_like, data=request.data)
        if serializer.is_valid():
            serializer.save()
            data = {
                "success": "update successful"
            }
            return Response(data=data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['DELETE', ])
def api_delete_comment_like_view(request, comment_like_id):
    try:
        comment_like = CommentLike.objects.get(id=comment_like_id)
    except CommentLike.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if request.method == "DELETE":
        operation = comment_like.delete()
        data = {}
        if operation:
            data["success"] = "delete successful"
        else:
            data["failure"] = "delete failed"
        return Response(data=data)


# //////content_like//////
@api_view(['POST', ])
def api_create_content_like_view(request):
    content_like = ContentLike()

    if request.method == "POST":
        serializer = ContentLikeSerializer(content_like, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', ])
def api_get_content_like_view(request, content_like_id):
    try:
        content_like = ContentLike.objects.get(id=content_like_id)
    except ContentLike.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if request.method == "GET":
        serializer = ContentLikeSerializer(content_like)
        return Response(serializer.data)


@api_view(['PUT', ])
def api_update_content_like_view(request, content_like_id):
    try:
        content_like = ContentLike.objects.get(id=content_like_id)
    except ContentLike.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if request.method == "PUT":
        serializer = ContentLikeSerializer(content_like, data=request.data)
        if serializer.is_valid():
            serializer.save()
            data = {
                "success": "update successful"
            }
            return Response(data=data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['DELETE', ])
def api_delete_content_like_view(request, content_like_id):
    try:
        content_like = ContentLike.objects.get(id=content_like_id)
    except ContentLike.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if request.method == "DELETE":
        operation = content_like.delete()
        data = {}
        if operation:
            data["success"] = "delete successful"
        else:
            data["failure"] = "delete failed"
        return Response(data=data)


# //////sponsor_tier//////
@api_view(['POST', ])
def api_create_sponsor_tier_view(request):
    sponsor_tier = SponsorTier()

    if request.method == "POST":
        serializer = SponsorTierSerializer(sponsor_tier, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', ])
def api_get_sponsor_tier_view(request, sponsor_tier_id):
    try:
        sponsor_tier = SponsorTier.objects.get(id=sponsor_tier_id)
    except SponsorTier.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if request.method == "GET":
        serializer = SponsorTierSerializer(sponsor_tier)
        return Response(serializer.data)


@api_view(['PUT', ])
def api_update_sponsor_tier_view(request, sponsor_tier_id):
    try:
        sponsor_tier = SponsorTier.objects.get(id=sponsor_tier_id)
    except SponsorTier.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if request.method == "PUT":
        serializer = SponsorTierSerializer(sponsor_tier, data=request.data)
        if serializer.is_valid():
            serializer.save()
            data = {
                "success": "update successful"
            }
            return Response(data=data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['DELETE', ])
def api_delete_sponsor_tier_view(request, sponsor_tier_id):
    try:
        sponsor_tier = SponsorTier.objects.get(id=sponsor_tier_id)
    except SponsorTier.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if request.method == "DELETE":
        operation = sponsor_tier.delete()
        data = {}
        if operation:
            data["success"] = "delete successful"
        else:
            data["failure"] = "delete failed"
        return Response(data=data)


# //////sponsor_tier_content//////
@api_view(['POST', ])
def api_create_sponsor_tier_content_view(request):
    sponsor_tier_content = SponsorTierContent()

    if request.method == "POST":
        serializer = SponsorTierContentSerializer(sponsor_tier_content, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', ])
def api_get_sponsor_tier_content_view(request, sponsor_tier_content_id):
    try:
        sponsor_tier_content = SponsorTierContent.objects.get(id=sponsor_tier_content_id)
    except SponsorTierContent.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if request.method == "GET":
        serializer = SponsorTierContentSerializer(sponsor_tier_content)
        return Response(serializer.data)


@api_view(['PUT', ])
def api_update_sponsor_tier_content_view(request, sponsor_tier_content_id):
    try:
        sponsor_tier_content = SponsorTierContent.objects.get(id=sponsor_tier_content_id)
    except SponsorTierContent.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if request.method == "PUT":
        serializer = SponsorTierContentSerializer(sponsor_tier_content, data=request.data)
        if serializer.is_valid():
            serializer.save()
            data = {
                "success": "update successful"
            }
            return Response(data=data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['DELETE', ])
def api_delete_sponsor_tier_content_view(request, sponsor_tier_content_id):
    try:
        sponsor_tier_content = SponsorTierContent.objects.get(id=sponsor_tier_content_id)
    except SponsorTierContent.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if request.method == "DELETE":
        operation = sponsor_tier_content.delete()
        data = {}
        if operation:
            data["success"] = "delete successful"
        else:
            data["failure"] = "delete failed"
        return Response(data=data)


# //////sponsor_subscription//////
@api_view(['POST', ])
def api_create_sponsor_subscription_view(request):
    sponsor_subscription = SponsorSubscription()

    if request.method == "POST":
        serializer = SponsorSubscriptionSerializer(sponsor_subscription, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', ])
def api_get_sponsor_subscription_view(request, sponsor_subscription_id):
    try:
        sponsor_subscription = SponsorSubscription.objects.get(id=sponsor_subscription_id)
    except SponsorSubscription.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if request.method == "GET":
        serializer = SponsorSubscriptionSerializer(sponsor_subscription)
        return Response(serializer.data)


@api_view(['PUT', ])
def api_update_sponsor_subscription_view(request, sponsor_subscription_id):
    try:
        sponsor_subscription = SponsorSubscription.objects.get(id=sponsor_subscription_id)
    except SponsorSubscription.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if request.method == "PUT":
        serializer = SponsorSubscriptionSerializer(sponsor_subscription, data=request.data)
        if serializer.is_valid():
            serializer.save()
            data = {
                "success": "update successful"
            }
            return Response(data=data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['DELETE', ])
def api_delete_sponsor_subscription_view(request, sponsor_subscription_id):
    try:
        sponsor_subscription = SponsorSubscription.objects.get(id=sponsor_subscription_id)
    except SponsorSubscription.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if request.method == "DELETE":
        operation = sponsor_subscription.delete()
        data = {}
        if operation:
            data["success"] = "delete successful"
        else:
            data["failure"] = "delete failed"
        return Response(data=data)


# //////subscription//////
@api_view(['POST', ])
def api_create_subscription_view(request):
    subscription = Subscription()

    if request.method == "POST":
        serializer = SubscriptionSerializer(subscription, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', ])
def api_get_subscription_view(request, subscription_id):
    try:
        subscription = Subscription.objects.get(id=subscription_id)
    except Subscription.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if request.method == "GET":
        serializer = SubscriptionSerializer(subscription)
        return Response(serializer.data)


@api_view(['PUT', ])
def api_update_subscription_view(request, subscription_id):
    try:
        subscription = Subscription.objects.get(id=subscription_id)
    except Subscription.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if request.method == "PUT":
        serializer = SubscriptionSerializer(subscription, data=request.data)
        if serializer.is_valid():
            serializer.save()
            data = {
                "success": "update successful"
            }
            return Response(data=data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['DELETE', ])
def api_delete_subscription_view(request, subscription_id):
    try:
        subscription = Subscription.objects.get(id=subscription_id)
    except Subscription.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if request.method == "DELETE":
        operation = subscription.delete()
        data = {}
        if operation:
            data["success"] = "delete successful"
        else:
            data["failure"] = "delete failed"
        return Response(data=data)



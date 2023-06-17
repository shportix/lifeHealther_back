from django.contrib.auth.models import User
from django.http import FileResponse
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
import json
import pymongo
import logging
from health_care_backend.settings import mongodb_client, mongodb_name, fs
from bson.json_util import dumps
import requests
from bson.binary import Binary
from bson.objectid import ObjectId
import base64
from django.core import serializers

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


@api_view(['GET', ])
def api_find_article_view(request, keyword):
    collection_name = mongodb_name["articles"]
        # Елемент для пошуку
    search_element = keyword

        # Складання запиту
    query = {
        'keywords': {
            '$elemMatch': {
                '$eq': search_element
             }
        }
    }

        # Виконання запиту та отримання документів
    articles = collection_name.find(query)
    data = {}
    k = 0
    for i in articles:
        content = Content.objects.get(id=i["content_id"])
        data[k] = {
            "creator": content.creator.id_id,
            "content_id": i["content_id"],
            "article_name": i["article_name"],
            "text": i["text"]
        }
        k += 1
    return Response(data=data, status=status.HTTP_200_OK)


@api_view(['GET', ])
def api_find_video_info_view(request, keyword):
    collection_name = mongodb_name["videos"]
        # Елемент для пошуку
    search_element = keyword

        # Складання запиту
    query = {
        'keywords': {
            '$elemMatch': {
                '$eq': search_element
             }
        }
    }

        # Виконання запиту та отримання документів
    videos = collection_name.find(query)
    data = {}
    k = 0
    for i in videos:
        content = Content.objects.get(id=int(i["content_id"]))
        preview_bytes = i['preview']
        # logging.debug(preview_bytes)

        # Перетворення фото у формат Base64
        encoded_preview = base64.b64encode(preview_bytes).decode('utf-8')
        data[k] = {
            "creator": content.creator.id_id,
            "content_id": i["content_id"],
            "video_name": i["video_name"],
            "preview": encoded_preview
        }
        k += 1
    return Response(data=data, status=status.HTTP_200_OK)


@api_view(['GET', ])
def api_login_view(request):
    try:
        user = User.objects.get(username=request.data["username"], password=requests.data["password"])
    except User.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)
    data = {
        "id" : user.id
    }
    my_user = MyUser.objects.get(id=data["id"])
    data["role"] = my_user.role
    return Response(data=data, status=status.HTTP_200_OK)


@api_view(['DELETE', ])
def api_delete_video_view(request, content_id):
    collection_name = mongodb_name["videos"]
    try:
        video_data = collection_name.find_one({"content_id": content_id})
        fs.delete(video_data["video_file_id"])
    except Exception:
        return Response(status=status.HTTP_404_NOT_FOUND)
    video = collection_name.delete_one({"content_id": content_id})
    data = {
        "success": "delete successful"
    }
    return Response(data=data)


@api_view(['DELETE', ])
def api_delete_article_view(request, content_id):
    collection_name = mongodb_name["articles"]
    try:
        atricle = collection_name.delete_one({"content_id": content_id})
    except Exception:
        return Response(status=status.HTTP_404_NOT_FOUND)
    data = {
        "success": "delete successful"
    }
    return Response(data=data)


@api_view(['POST', ])
def api_create_creator_mongo_view(request):
    collection_name = mongodb_name["creator"]
    try:

        creator = {
            "creator_id": request.data["creator_id"],
            "avatar": "NO",
            "keywords": [],
            "diplomas": []
        }

    except Exception:
        return Response(status=status.HTTP_400_BAD_REQUEST)
    collection_name.insert_one(creator)
    return  Response(status=status.HTTP_201_CREATED)


@api_view(['GET', ])
def api_get_creator_mongo_view(request, creator_id):

    collection_name = mongodb_name["creator"]
    try:
        creator_data = collection_name.find_one({"creator_id": creator_id})
        creator_data = {
            "creator_id": creator_data["creator_id"],
            "avatar": creator_data["avatar"],
            "keywords": creator_data["keywords"],
            "diplomas": creator_data["diplomas"]
        }
    except Exception:
        return Response(status=status.HTTP_404_NOT_FOUND)
    return  Response(data=creator_data, status=status.HTTP_200_OK)


@api_view(['POST', ])
def api_create_diploma_mongo_view(request):
    collection_name = mongodb_name["diploma"]
    diploma_file = request.FILES["diploma_file"]
    try:
        diploma_data = diploma_file.read()
        diploma_bson = Binary(diploma_data)
        diploma = {
            "is_valid": False,
            "diploma_file": diploma_bson
        }
        diploma_id = collection_name.insert_one(diploma).inserted_id
        diploma_id = str(diploma_id)
        collection_name =  mongodb_name["creator"]
        creator_data = collection_name.find_one({"creator_id": request.data["creator_id"]})
        diplomas = creator_data["diplomas"].append(diploma_id)
        collection_name.update_one({"creator_id": request.data["creator_id"]}, {'$set': {'diplomas': diplomas}})
    except Exception:
        return Response(status=status.HTTP_400_BAD_REQUEST)
    return  Response(status=status.HTTP_201_CREATED)


@api_view(['GET', ])
def api_get_creator_diplomas_mongo_view(request, creator_id):

    collection_diploma = mongodb_name["diploma"]
    collection_creator = mongodb_name["creator"]
    try:
        creator_data = collection_creator.find_one({"creator_id": creator_id})
        diplomas_ids = creator_data["diplomas"]
        diplomas = {}
        k = 0
        for i in diplomas_ids:
            diploma_data = collection_diploma.find_one({'_id': ObjectId(i)})
            preview_bytes = diploma_data["diploma_file"]
            # logging.debug(preview_bytes)

            # Перетворення фото у формат Base64
            encoded_preview = base64.b64encode(preview_bytes).decode('utf-8')
            diplomas[k] = {
                "file": encoded_preview,
                "id": i
            }
    except Exception:
        return Response(status=status.HTTP_404_NOT_FOUND)
    return  Response(data=diplomas, status=status.HTTP_200_OK)


#test mongo
@api_view(['POST', ])
def api_create_article_mongo_view(request):

    collection_name = mongodb_name["articles"]
    keywords = request.data["keywords"].split(",")
    keywords = [i.strip() for i in keywords]
    try:
        article = {
            "content_id": request.data["content_id"],
            "article_name": request.data["article_name"],
            "text": request.data["text"],
            "keywords": keywords,
        }
    except Exception:
        return Response(status=status.HTTP_400_BAD_REQUEST)
    collection_name.insert_one(article)
    return  Response(status=status.HTTP_201_CREATED)


@api_view(['POST', ])
def api_create_creator_mongo_view(request):

    collection_name = mongodb_name["creator_info"]
    try:
        creator = {
            "creator_id": request.data["id"],
            "avatar": "no",
            "diplomas": [],
            "keywords": [],
        }
    except Exception:
        return Response(status=status.HTTP_400_BAD_REQUEST)
    collection_name.insert_one(creator)
    return  Response(status=status.HTTP_201_CREATED)


@api_view(['POST', ])
def api_create_video_mongo_view(request):
    logging.basicConfig(level=logging.DEBUG)
    collection_name = mongodb_name["videos"]
    # logging.debug(f"data = {request.POST}")
    # logging.debug(f"files = {request.FILES}")
    video_file = request.FILES["video"]
    preview_file = request.FILES["preview"]
    keywords = request.data.get("keywords").split(",")
    keywords = [i.strip() for i in keywords]
    try:
        video_file_id = fs.put(video_file)
        preview_data = preview_file.read()
        preview_bson = Binary(preview_data)
        video = {
            "content_id": request.data["content_id"],
            "video_name": request.data["video_name"],
            "video_file_id": video_file_id,
            "preview": preview_bson,
            "keywords": keywords,
        }

    except Exception:
        return Response(status=status.HTTP_400_BAD_REQUEST)
    collection_name.insert_one(video)
    return  Response(status=status.HTTP_201_CREATED)


@api_view(['POST', ])
def api_create_shorts_mongo_view(request):
    logging.basicConfig(level=logging.DEBUG)
    collection_name = mongodb_name["shorts"]
    # logging.debug(f"data = {request.POST}")
    # logging.debug(f"files = {request.FILES}")
    video_file = request.FILES["video"]
    preview_file = request.FILES["preview"]
    keywords = request.data.get("keywords").split(",")
    keywords = [i.strip() for i in keywords]
    try:
        video_file_id = fs.put(video_file)
        preview_data = preview_file.read()
        preview_bson = Binary(preview_data)
        video = {
            "content_id": request.data["content_id"],
            "video_name": request.data["video_name"],
            "video_file_id": video_file_id,
            "preview": preview_bson,
            "keywords": keywords,
        }

    except Exception:
        return Response(status=status.HTTP_400_BAD_REQUEST)
    collection_name.insert_one(video)
    return  Response(status=status.HTTP_201_CREATED)


@api_view(['GET', ])
def api_get_video_info_mongo_view(request, content_id):
    logging.basicConfig(level=logging.DEBUG)

    collection_name = mongodb_name["videos"]
    try:
        video_data = collection_name.find_one({"content_id": content_id})
        preview_bytes = video_data['preview']
        # logging.debug(preview_bytes)

            # Перетворення фото у формат Base64
        encoded_preview = base64.b64encode(preview_bytes).decode('utf-8')
        video_data = {
            "content_id": video_data["content_id"],
            "video_name": video_data["video_name"],
            "preview": encoded_preview,
            "keywords": video_data["keywords"],
        }
    except Exception:
         return Response(status=status.HTTP_404_NOT_FOUND)
    return  Response(data=video_data, status=status.HTTP_200_OK)


@api_view(['PUT', ])
def api_update_video_mongo_view(request, content_id):
    logging.basicConfig(level=logging.DEBUG)

    collection_name = mongodb_name["videos"]
    try:
        keywords = request.data.get("keywords").split(",")
        keywords = [i.strip() for i in keywords]
        query = {"content_id": content_id}
        update = {'$set': {
            "video_name": request.data["video_name"],
            "keywords": keywords
        }}

        # Оновлення одного документа, який задовільняє умову
        result = collection_name.update_one(query, update)
    except Exception:
         return Response(status=status.HTTP_404_NOT_FOUND)
    return  Response(status=status.HTTP_201_CREATED)


@api_view(['PUT', ])
def api_update_article_mongo_view(request, content_id):
    logging.basicConfig(level=logging.DEBUG)

    collection_name = mongodb_name["articles"]
    try:
        keywords = request.data.get("keywords").split(",")
        keywords = [i.strip() for i in keywords]
        query = {"content_id": content_id}
        update = {'$set': {
            "article_name": request.data["article_name"],
            "keywords": keywords
        }}

        # Оновлення одного документа, який задовільняє умову
        result = collection_name.update_one(query, update)
    except Exception:
         return Response(status=status.HTTP_404_NOT_FOUND)
    return  Response(status=status.HTTP_201_CREATED)


@api_view(['GET', ])
def api_get_video_mongo_view(request, content_id):

    collection_name = mongodb_name["videos"]
    try:
        video_data = collection_name.find_one({"content_id": content_id})
        video_file = fs.get(video_data["video_file_id"])
        # mime_type = magic.from_buffer(video_file.read(), mime=True)
    except Exception:
        return Response(status=status.HTTP_404_NOT_FOUND)

    return  FileResponse(video_file)


@api_view(['GET', ])
def api_get_article_mongo_view(request, content_id):

    collection_name = mongodb_name["articles"]
    try:
        article_data = collection_name.find_one({"content_id": content_id})
        article_data = {
            "content_id": article_data["content_id"],
            "article_name": article_data["article_name"],
            "text": article_data["text"],
            "keywords": article_data["keywords"],
        }
    except Exception:
        return Response(status=status.HTTP_404_NOT_FOUND)
    return  Response(data=article_data, status=status.HTTP_200_OK)


# //////user//////
@api_view(['POST', ])
def api_create_user_view(request):
    user = User()

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
        creator = Creator.objects.get(id=request.data["creator"])
        if serializer.is_valid():
            content = Content.objects.create(creator=creator,
                                             content_type=request.data['content_type'],
                                             like_count=request.data["like_count"],
                                             is_paid=request.data['is_paid'])
            data = {
                "id": content.id
            }
            return Response(data, status=status.HTTP_201_CREATED)
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


@api_view(['GET', ])
def api_get_free_articles_content_view(request):
    try:
        articles = Content.objects.filter(content_type="article", is_paid=False)
    except Content.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)
    if request.method == "GET":
        data = {}
        k = 0
        for i in articles:
            data[k] = ContentSerializer(i).data
            k += 1
        return Response(data)


@api_view(['GET', ])
def api_get_creators_articles_content_view(request, creator_id):
    try:
        creator = Creator.objects.get(id=creator_id)
        articles = Content.objects.filter(content_type="article", creator=creator)
    except Content.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)
    if request.method == "GET":
        data = {}
        k = 0
        for i in articles:
            data[k] = ContentSerializer(i).data
            k += 1
        return Response(data)


@api_view(['GET', ])
def api_get_creators_videos_content_view(request, creator_id):
    try:
        creator = Creator.objects.get(id=creator_id)
        video = Content.objects.filter(content_type="video", creator=creator)
    except Content.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)
    if request.method == "GET":
        data = {}
        k = 0
        for i in video:
            data[k] = ContentSerializer(i).data
            k += 1
        return Response(data)


@api_view(['GET', ])
def api_get_free_videos_content_view(request):
    try:
        video = Content.objects.filter(content_type="video", is_paid=False)
    except Content.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)
    if request.method == "GET":
        data = {}
        k = 0
        for i in video:
            data[k] = ContentSerializer(i).data
            k += 1
        return Response(data)


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
        creator = Creator.objects.get(id=request.data["creator"])
        if serializer.is_valid():
            sponsor_tier = SponsorTier.objects.create(creator=creator,
                                                      price=request.data['price'],
                                                      name=request.data['name'])
            data = {
                "id": sponsor_tier.id
            }
            return Response(data, status=status.HTTP_201_CREATED)
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



from django.contrib.auth.models import User
from django.http import FileResponse
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
import json
import pymongo
from django.db.models import Q
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
def api_load_creator(request, creator_id, customer_id):
    data = {}
    videos_info = []
    shorts_info = []
    articles_info = []
    sponsor_tiers_info = []
    diplomas_info = []
    collection_creator = mongodb_name["creator_info"]
    creator_mongo = collection_creator.find_one({"creator_id": int(creator_id)})
    creator = Creator.objects.get(id=creator_id)
    user = User.objects.get(id=creator_id)
    customer = Customer.objects.get(id=customer_id)
    try:
        Subscription.objects.get(creator=creator, customer=customer)
        subscribed = True
    except Subscription.DoesNotExist:
        subscribed = False
    data["subscribed"] = subscribed
    data["username"] = user.username
    data["info"] = creator.info
    avatar = creator_mongo["avatar"]
    if avatar != "NO":
        avatar = base64.b64encode(avatar).decode('utf-8')
    data["avatar"] = avatar
    videos = Content.objects.filter(creator=creator, content_type="video")
    articles = Content.objects.filter(creator=creator, content_type="article")
    shorts = Content.objects.filter(creator=creator, content_type="short")
    sponsor_tiers = SponsorTier.objects.filter(creator=creator)
    collection_content = mongodb_name["videos"]
    customer_sponsor_subs = SponsorSubscription.objects.filter(customer=customer)
    customer_sponsor_tiers = []
    for i in customer_sponsor_subs:
        customer_sponsor_tiers.append(i.sponsor_tier)
    customer_sponsor_tier_cont = SponsorTierContent.objects.filter(sponsor_tier__in=customer_sponsor_tiers)
    customer_sponsor_cont = []
    for i in customer_sponsor_tier_cont:
        customer_sponsor_cont.append(i.content)
    for cont in videos:
        accessed = True
        if cont.is_paid and cont not in customer_sponsor_cont:
            accessed = False
        if accessed:
            content_data = {
                "content_id": cont.id,
                "is_paid": cont.is_paid,
                "like_count": cont.like_count
            }
            cont_mongo = collection_content.find_one({"content_id": str(cont.id)})
            preview = base64.b64encode(cont_mongo["preview"]).decode('utf-8')
            content_data["preview"] = preview
            content_data["title"] = cont_mongo["video_name"]
            videos_info.append(content_data)
    data["videos"] = videos_info
    collection_content = mongodb_name["shorts"]
    for cont in shorts:
        accessed = True
        if cont.is_paid and cont not in customer_sponsor_cont:
            accessed = False
        if accessed:
            content_data = {
                "content_id": cont.id,
                "is_paid": cont.is_paid,
                "like_count": cont.like_count
            }
            cont_mongo = collection_content.find_one({"content_id": str(cont.id)})
            preview = base64.b64encode(cont_mongo["preview"]).decode('utf-8')
            content_data["preview"] = preview
            content_data["title"] = cont_mongo["video_name"]
            shorts_info.append(content_data)
    data["shorts"] = shorts_info
    collection_content = mongodb_name["articles"]
    for cont in articles:
        accessed = True
        if cont.is_paid and cont not in customer_sponsor_cont:
            accessed = False
        if accessed:
            content_data = {
                "content_id": cont.id,
                "is_paid": cont.is_paid,
                "like_count": cont.like_count
            }
            cont_mongo = collection_content.find_one({"content_id": int(cont.id)})
            content_data["headline"] = cont_mongo["article_name"]
            content_data["text"] = cont_mongo["text"]
            articles_info.append(content_data)
    data["articles"] = articles_info
    collection_tier = mongodb_name["sponsor_tier"]
    for sp_t in sponsor_tiers:
        sp_mongo = collection_tier.find_one({"sponsor_tier_id": sp_t.id})
        subbed = sp_t in customer_sponsor_tiers
        sp_data = {
            "sponsor_tier_id": sp_t.id,
            "name": sp_t.name,
            "price": sp_t.price,
            "info": sp_mongo["info"],
            "subbed": subbed
        }
        sponsor_tiers_info.append(sp_data)
    data["sponsor_tiers"] = sponsor_tiers_info
    collection_diploma = mongodb_name["diploma"]
    diplomas = creator_mongo["diplomas"]
    for diploma_id in diplomas:
        diploma = collection_diploma.find_one({'_id': ObjectId(diploma_id)})
        preview_bytes = diploma["diploma_file"]
        encoded_preview = base64.b64encode(preview_bytes).decode('utf-8')
        diploma_data = {
            "file": encoded_preview,
        }
        diplomas_info.append(diploma_data)
    data["diplomas"] = diplomas_info
    return Response(data)




@api_view(['GET', ])
def api_get_sponsor_tier_creator_content(request, sponsor_tier_id):
    sponsor_tier = SponsorTier.objects.get(id=sponsor_tier_id)
    sponsor_tier_contents = SponsorTierContent.objects.filter(sponsor_tier=sponsor_tier)
    contents = []
    for sp_t_con in sponsor_tier_contents:
        contents.append(sp_t_con.content)
    data = {}
    k = 0
    for cont in contents:
        content_type = cont.content_type
        if content_type == "article":
            collection_name = mongodb_name["articles"]
            article = collection_name.find_one({"content_id": int(cont.id)})
            content_name = article["article_name"]
        elif content_type == "video":
            collection_name = mongodb_name["videos"]
            article = collection_name.find_one({"content_id": str(cont.id)})
            content_name = article["video_name"]
        else:
            collection_name = mongodb_name["shorts"]
            article = collection_name.find_one({"content_id": str(cont.id)})
            content_name = article["video_name"]

        buf = {
            "content_id": cont.id,
            "content_type": content_type,
            "content_name": content_name
        }
        data[k] = buf
        k += 1
    return Response(data=data, status=status.HTTP_200_OK)


@api_view(['GET', ])
def api_get_sponsor_tier_creator_no_content(request, sponsor_tier_id):
    sponsor_tier = SponsorTier.objects.get(id=sponsor_tier_id)
    creator = sponsor_tier.creator
    sponsor_tier_contents = SponsorTierContent.objects.filter(sponsor_tier=sponsor_tier)
    contents = []
    for sp_t_con in sponsor_tier_contents:
        contents.append(sp_t_con.content)
    creator_contents = Content.objects.filter(creator=creator)
    data = {}
    k = 0
    for cont in creator_contents:
        if cont not in contents:
            content_type = cont.content_type
            if content_type == "article":
                collection_name = mongodb_name["articles"]
                article = collection_name.find_one({"content_id": int(cont.id)})
                content_name = article["article_name"]
            elif content_type == "video":
                collection_name = mongodb_name["videos"]
                article = collection_name.find_one({"content_id": str(cont.id)})
                content_name = article["video_name"]
            else:
                collection_name = mongodb_name["shorts"]
                article = collection_name.find_one({"content_id": str(cont.id)})
                content_name = article["video_name"]

            buf = {
                "content_id": cont.id,
                "content_type": content_type,
                "content_name": content_name
            }
            data[k] = buf
            k += 1
    return Response(data=data, status=status.HTTP_200_OK)


@api_view(['GET', ])
def api_login_view(request):
    username = request.GET["username"]
    password = request.GET["password"]
    try:
        user = User.objects.get(username=username)
    except User.DoesNotExist:
        return Response(data={"error":"user not found"}, status=status.HTTP_404_NOT_FOUND)
    if user.password != password:
        return Response(data={"error": "password incorrect"}, status=status.HTTP_404_NOT_FOUND)
    my_user = MyUser.objects.get(id_id=user.id)
    data = {
        "id": user.id,
        "role": my_user.role
    }
    return Response(data=data, status=status.HTTP_200_OK)


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
def api_find_short_info_view(request, keyword):
    collection_name = mongodb_name["shorts"]
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
def api_delete_sponsor_tier_view(request, sponsor_tier_id):
    collection_name = mongodb_name["sponsor_tier"]
    try:
        sponsor_tier_data = collection_name.find_one({"sponsor_tier_id": sponsor_tier_id})
    except Exception:
        return Response(status=status.HTTP_404_NOT_FOUND)
    sponsor_tier = collection_name.delete_one({"sponsor_tier_id": sponsor_tier_id})
    data = {
        "success": "delete successful"
    }
    return Response(data=data)


@api_view(['DELETE', ])
def api_delete_short_view(request, content_id):
    collection_name = mongodb_name["shorts"]
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
    collection_name = mongodb_name["creator_info"]
    try:

        creator = {
            "creator_id": request.data["creator_id"],
            "avatar": "NO",
            "diplomas": []
        }

    except Exception:
        return Response(status=status.HTTP_400_BAD_REQUEST)
    collection_name.insert_one(creator)
    return  Response(status=status.HTTP_201_CREATED)

@api_view(['POST', ])
def api_create_sponsor_tier_mongo_view(request):
    collection_name = mongodb_name["sponsor_tier"]
    creator = {
        "sponsor_tier_id": request.data["sponsor_tier_id"],
        "info": request.data["info"]
    }
    collection_name.insert_one(creator)
    return  Response(status=status.HTTP_201_CREATED)

@api_view(['POST', ])
def api_create_customer_mongo_view(request):
    collection_name = mongodb_name["customer_info"]
    try:

        creator = {
            "customer_id": request.data["creator_id"],
            "keywords": {},
            "viewed": []
        }

    except Exception:
        return Response(status=status.HTTP_400_BAD_REQUEST)
    collection_name.insert_one(creator)
    return  Response(status=status.HTTP_201_CREATED)


@api_view(['PUT', ])
def api_update_creator_avatar_mongo_view(request, creator_id):
    collection_name = mongodb_name["creator_info"]
    try:
        avatar_file = request.FILES["avatar"]
        avatar_data = avatar_file.read()
        avatar_bson = Binary(avatar_data)

        query = {"creator_id": creator_id}
        update = {'$set': {
            "avatar": avatar_bson
        }}

        # Оновлення одного документа, який задовільняє умову
        result = collection_name.update_one(query, update)
    except Exception:
        return Response(status=status.HTTP_400_BAD_REQUEST)
    return  Response(status=status.HTTP_201_CREATED)


@api_view(['PUT', ])
def api_customer_viewed_mongo_view(request, customer_id):
    collection_name = mongodb_name["customer_info"]
    try:
        content_id = request.data["content_id"]
        customer_mongo = collection_name.find_one({"customer_id": customer_id})
        viewed = customer_mongo["viewed"]
        if content_id not in viewed:
            viewed.append(content_id)
        query = {"customer_id": customer_id}
        update = {'$set': {
            "viewed": viewed
        }}

        # Оновлення одного документа, який задовільняє умову
        result = collection_name.update_one(query, update)
    except Exception:
        return Response(status=status.HTTP_400_BAD_REQUEST)
    return  Response(status=status.HTTP_201_CREATED)

@api_view(['PUT', ])
def api_update_sponsor_tier_mongo_view(request, sponsor_tier_id):
    collection_name = mongodb_name["sponsor_tier"]
    try:
        customer_mongo = collection_name.find_one({"sponsor_tier_id": sponsor_tier_id})
        query = {"sponsor_tier_id": sponsor_tier_id}
        update = {'$set': {
            "info": request.data["info"]
        }}

        # Оновлення одного документа, який задовільняє умову
        result = collection_name.update_one(query, update)
    except Exception:
        return Response(status=status.HTTP_400_BAD_REQUEST)
    return  Response(status=status.HTTP_201_CREATED)

@api_view(['GET', ])
def api_get_creator_mongo_view(request, creator_id):

    collection_name = mongodb_name["creator_info"]
    # try:
    creator_data = collection_name.find_one({"creator_id": int(creator_id)})
    avatar = creator_data["avatar"]
    if avatar != "NO":
        avatar = base64.b64encode(avatar).decode('utf-8')
    creator_data = {
        "creator_id": creator_data["creator_id"],
        "avatar": avatar,
        "diplomas": creator_data["diplomas"]
    }
    # except Exception:
    #     return Response(status=status.HTTP_404_NOT_FOUND)
    return  Response(data=creator_data, status=status.HTTP_200_OK)

@api_view(['GET', ])
def api_get_sponsor_tier_mongo_view(request, sponsor_tier_id):

    collection_name = mongodb_name["sponsor_tier"]
    # try:
    creator_data = collection_name.find_one({"sponsor_tier_id": int(sponsor_tier_id)})
    creator_data = {
        "sponsor_tier_id": creator_data["sponsor_tier_id"],
        "info": creator_data["info"]
    }
    # except Exception:
    #     return Response(status=status.HTTP_404_NOT_FOUND)
    return  Response(data=creator_data, status=status.HTTP_200_OK)


@api_view(['GET', ])
def api_get_customer_mongo_view(request, customer_id):

    collection_name = mongodb_name["customer_info"]
    # try:
    creator_data = collection_name.find_one({"customer_id": int(customer_id)})
    creator_data = {
        "customer_id": creator_data["customer_id"],
        "keywords": creator_data["keywords"],
        "viewed": creator_data["viewed"]
    }
    # except Exception:
    #     return Response(status=status.HTTP_404_NOT_FOUND)
    return  Response(data=creator_data, status=status.HTTP_200_OK)


@api_view(['POST', ])
def api_create_diploma_mongo_view(request):
    logging.basicConfig(level=logging.DEBUG)
    collection_name = mongodb_name["diploma"]
    collection_creator = mongodb_name["creator_info"]
    diploma_file = request.FILES["diploma_file"]
    # try:
    diploma_data = diploma_file.read()
    diploma_bson = Binary(diploma_data)
    diploma = {
        "is_valid": False,
        "diploma_file": diploma_bson
    }
    diploma_id = collection_name.insert_one(diploma).inserted_id
    diploma_id = str(diploma_id)
    creator_data = collection_creator.find_one({"creator_id": int(request.data["creator_id"])})
    diplomas = creator_data["diplomas"]
    new_diplomas = []
    for i in diplomas:
        new_diplomas.append(i)
    new_diplomas.append(diploma_id)
    collection_creator.update_one({"creator_id": int(request.data["creator_id"])}, {'$set': {'diplomas': new_diplomas}})
    # except Exception:
    #     return Response(status=status.HTTP_400_BAD_REQUEST)
    return  Response(status=status.HTTP_201_CREATED)


@api_view(['GET', ])
def api_get_creator_diplomas_mongo_view(request, creator_id):

    collection_diploma = mongodb_name["diploma"]
    collection_creator = mongodb_name["creator_info"]
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
            k += 1
    except Exception:
        return Response(status=status.HTTP_404_NOT_FOUND)
    return  Response(data=diplomas, status=status.HTTP_200_OK)


@api_view(['GET', ])
def api_get_diploma_mongo_view(request, diploma_id):

    collection_diploma = mongodb_name["diploma"]
    try:
        diploma_data = collection_diploma.find_one({'_id': ObjectId(diploma_id)})
        preview_bytes = diploma_data["diploma_file"]
        # logging.debug(preview_bytes)

        # Перетворення фото у формат Base64
        encoded_preview = base64.b64encode(preview_bytes).decode('utf-8')
        diplomas = {
            "file": encoded_preview,
            "id": diploma_id
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


@api_view(['GET', ])
def api_get_short_info_mongo_view(request, content_id):
    logging.basicConfig(level=logging.DEBUG)

    collection_name = mongodb_name["shorts"]
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
def api_update_short_mongo_view(request, content_id):
    logging.basicConfig(level=logging.DEBUG)

    collection_name = mongodb_name["shorts"]
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
def api_get_short_mongo_view(request, content_id):

    collection_name = mongodb_name["shorts"]
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


@api_view(['GET', ])
def api_get_creator_info_view(request, creator_id):
    try:
        creator = Creator.objects.get(id=creator_id)
    except Creator.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if request.method == "GET":
        data = {
            "info": creator.info
        }
        return Response(data)


@api_view(['PUT', ])
def api_update_creator_view(request, creator_id):
    try:
        creator = Creator.objects.get(id=creator_id)
    except Creator.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if request.method == "PUT":
        info = request.data["info"]
        creator.info = info
        creator.save()
        return Response(status=status.HTTP_201_CREATED)


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
def api_get_customer_content_view(request, content_type, customer_id):
    collection_name = mongodb_name["customer_info"]
    if content_type == "article":
        collection_content = mongodb_name["articles"]
    elif content_type == "video":
        collection_content = mongodb_name["videos"]
    else:
        collection_content = mongodb_name["shorts"]
    customer_mongo = collection_name.find_one({"customer_id": int(customer_id)})
    customer_sql = Customer.objects.get(id=customer_id)
    viewed = customer_mongo["viewed"]
    customer_sponsor_sub = SponsorSubscription.objects.filter(customer=customer_sql)
    customer_sponsor_tiers = []
    for sub in customer_sponsor_sub:
        customer_sponsor_tiers.append(sub.sponsor_tier)
    customer_sponsor_tier_contents = SponsorTierContent.objects.filter(sponsor_tier__in=customer_sponsor_tiers)
    customer_sponsor_contents = []
    for sponsor_tier_content in customer_sponsor_tier_contents:
        content = sponsor_tier_content.content
        if content.content_type == content_type and content.id not in viewed:
            customer_sponsor_contents.append(content)
    free_content = Content.objects.filter(content_type=content_type, is_paid=False)
    customer_free_content = []
    for content in free_content:
        if content.id not in viewed:
            customer_free_content.append(content)
    if customer_mongo["keywords"] != {}:
        customer_keywords = customer_mongo["keywords"]
        customer_sponsor_contents_rate = []
        for i in customer_sponsor_contents:
            content = [i]
            if content_type == "article":
                content_mongo = collection_content.find_one({"content_id": i.id})
            else:
                content_mongo = collection_content.find_one({"content_id": str(i.id)})
            content_keywords = content_mongo["keywords"]
            rate = 0
            for word in content_keywords:
                if word in customer_keywords.keys():
                    rate += customer_keywords["word"]
            content.append(rate)
            content.append(i.like_count)
            customer_sponsor_contents_rate.append(content)
        customer_sponsor_contents_rate = sorted(customer_sponsor_contents_rate, key=lambda x: (x[1], x[2]), reverse=True)
        customer_sponsor_contents = []
        for i in customer_sponsor_contents_rate:
            customer_sponsor_contents.append(i[0])
        customer_free_contents_rate = []
        for i in customer_free_content:
            content = [i]
            if content_type == "video" or content_type == "short":
                content_mongo = collection_content.find_one({"content_id": str(i.id)})
            else:
                content_mongo = collection_content.find_one({"content_id": i.id})
            content_keywords = content_mongo["keywords"]
            rate = 0
            for word in content_keywords:
                if word in customer_keywords.keys():
                    rate += customer_keywords[word]
            content.append(rate)
            content.append(i.like_count)
            customer_free_contents_rate.append(content)
        customer_free_contents_rate = sorted(customer_free_contents_rate, key=lambda x: (x[1], x[2]), reverse=True)
        customer_free_content = []
        for i in customer_free_contents_rate:
            customer_free_content.append(i[0])
    else:
        customer_sponsor_contents_rate = []
        for i in customer_sponsor_contents:
            content = [i, i.like_count]
            customer_sponsor_contents_rate.append(content)
        customer_sponsor_contents_rate = sorted(customer_sponsor_contents_rate, key=lambda x: (x[1]), reverse=True)
        customer_sponsor_contents = []
        for i in customer_sponsor_contents_rate:
            customer_sponsor_contents.append(i[0])
        customer_free_contents_rate = []
        for i in customer_free_content:
            content = [i, i.like_count]
            customer_free_contents_rate.append(content)
        customer_free_contents_rate = sorted(customer_free_contents_rate, key=lambda x: (x[1]), reverse=True)
        customer_free_content = []
        for i in customer_free_contents_rate:
            customer_free_content.append(i[0])
    customer_content = customer_sponsor_contents + customer_free_content
    final_list = []
    collection_creator = mongodb_name["creator_info"]
    if content_type == "article":
        for cont in customer_content:
            cont_mongo = collection_content.find_one({"content_id": cont.id})
            creator_mongo = collection_creator.find_one({"creator_id": cont.creator.id_id})
            creator = Creator.objects.get(id=cont.creator.id_id)
            user = User.objects.get(id=creator.id_id)
            avatar = creator_mongo["avatar"]
            if avatar != "NO":
                avatar = base64.b64encode(avatar).decode('utf-8')
            content = {
                "content_id": cont.id,
                "article_name": cont_mongo["article_name"],
                "text": cont_mongo["text"],
                "creator_id": creator.id_id,
                "username": user.username,
                "avatar": avatar,
                "like_count": cont.like_count

            }
            final_list.append(content)
    elif content_type == "video":
        for cont in customer_content:
            cont_mongo = collection_content.find_one({"content_id": str(cont.id)})
            creator_mongo = collection_creator.find_one({"creator_id": cont.creator.id_id})
            creator = Creator.objects.get(id=cont.creator.id_id)
            user = User.objects.get(id=creator.id_id)
            avatar = creator_mongo["avatar"]
            if avatar != "NO":
                avatar = base64.b64encode(avatar).decode('utf-8')
            preview_bytes = cont_mongo['preview']
            encoded_preview = base64.b64encode(preview_bytes).decode('utf-8')

            content = {
                "content_id": cont.id,
                "video_name": cont_mongo["video_name"],
                "preview": encoded_preview,
                "creator_id": creator.id_id,
                "username": user.username,
                "avatar": avatar,
                "like_count": cont.like_count

            }
            final_list.append(content)
    else:
        for cont in customer_content:
            cont_mongo = collection_content.find_one({"content_id": str(cont.id)})
            creator_mongo = collection_creator.find_one({"creator_id": cont.creator.id_id})
            creator = Creator.objects.get(id=cont.creator.id_id)
            avatar = creator_mongo["avatar"]
            if avatar != "NO":
                avatar = base64.b64encode(avatar).decode('utf-8')
            content = {
                "content_id": cont.id,
                "video_name": cont_mongo["video_name"],
                "creator_id": creator.id_id,
                "avatar": avatar,
                "like_count": cont.like_count

            }
            final_list.append(content)

    data = {
        "contents": final_list
    }
    return Response(data)


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
def api_get_customer_subs_view(request, customer_id):
    customer = Customer.objects.get(id=customer_id)
    customer_subs = Subscription.objects.filter(customer=customer)
    creators = []
    collection_name = mongodb_name["creator_info"]
    for i in customer_subs:
        creator_id = i.creator.id_id
        creator_mongo = collection_name.find_one({"creator_id": int(creator_id)})
        user = User.objects.get(id=creator_id)
        avatar = creator_mongo["avatar"]
        if avatar != "NO":
            avatar = base64.b64encode(avatar).decode('utf-8')
        creator_data = {
            "id": creator_id,
            "avatar": avatar,
            "username": user.username

        }
        creators.append(creator_data)
    data = {
        "creators": creators
    }
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
def api_get_creators_sponsor_tiers_view(request, creator_id):
    try:
        creator = Creator.objects.get(id=creator_id)
        sponsor_tiers = SponsorTier.objects.filter(creator=creator)
    except Creator.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)
    if request.method == "GET":
        data = {}
        k = 0
        for i in sponsor_tiers:
            data[k] = SponsorTierSerializer(i).data
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
def api_get_creators_shorts_content_view(request, creator_id):
    try:
        creator = Creator.objects.get(id=creator_id)
        video = Content.objects.filter(content_type="short", creator=creator)
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


@api_view(['GET', ])
def api_get_free_shorts_content_view(request):
    try:
        video = Content.objects.filter(content_type="short", is_paid=False)
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
        customer = Customer.objects.get(id=request.data["customer"])
        text = request.data["text"]
        like_count = request.data["like_count"]
        content = Content.objects.get(id=request.data["content"])
        if serializer.is_valid():
            comment = Comment.objects.create(customer=customer,
                                            content=content,
                                            text=text,
                                            like_count=like_count)
            data = {
                "id": comment.id
            }
            return Response(data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', ])
def api_get_comment_view(request, content_id):
    try:
        content = Content.objects.get(id=content_id)
        comments = Comment.objects.filter(content=content_id)
    except Comment.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if request.method == "GET":
        data = []
        for i in comments:
            author = User.objects.get(id=i.customer.id_id)
            comm = {
                "username": author.username,
                "text": i.text
            }
            data.append(comm)
        return Response(data)


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
    logging.basicConfig(level=logging.DEBUG)
    content_like = ContentLike()

    if request.method == "POST":
        collection_customer = mongodb_name["customer_info"]
        customer_id = request.data["customer_id"]
        content_id = request.data["content_id"]
        serializer = ContentLikeSerializer(content_like, data=request.data)
        customer = Customer.objects.get(id=customer_id)
        content = Content.objects.get(id=content_id)
        if serializer.is_valid():
            content_like = ContentLike.objects.create(customer=customer,
                                                      content=content)
            if content.content_type == "article":
                collection_content = mongodb_name["articles"]
                logging.debug("article")
            elif content.content_type == "video":
                collection_content = mongodb_name["videos"]
                logging.debug("video")
            else:
                logging.debug("short")
                collection_content = mongodb_name["shorts"]
            logging.debug(content_id)
            if content.content_type == "article":
                content_mongo = collection_content.find_one({"content_id": int(content_id)})
            else:
                content_mongo = collection_content.find_one({"content_id": str(content_id)})
            content_keywords = content_mongo["keywords"]
            customer_mongo = collection_customer.find_one({"customer_id": customer_id})
            customer_keywords = customer_mongo["keywords"]
            for i in content_keywords:
                if i in customer_keywords.keys():
                    customer_keywords[i] += 1
                else:
                    customer_keywords[i] = 1
            content.like_count += 1
            content.save()
            collection_customer.update_one({"customer_id": customer_id}, {'$set': {"keywords": customer_keywords}})
            data = {
                "id": content_like.id,
                "like_count": content.like_count
            }
            return Response(data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', ])
def api_get_content_like_view(request, content_id, customer_id):
    try:
        content = Content.objects.get(id=content_id)
        customer = Customer.objects.get(id=customer_id)

        content_like = ContentLike.objects.get(content=content,customer=customer)
    except ContentLike.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if request.method == "GET":
        serializer = ContentLikeSerializer(content_like)
        return Response(serializer.data, status=status.HTTP_200_OK)


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
def api_delete_content_like_view(request, content_id, customer_id):
    try:
        content = Content.objects.get(id=content_id)
        customer = Customer.objects.get(id=customer_id)
        content_like = ContentLike.objects.get(content=content,customer=customer)
    except ContentLike.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)
    collection_customer = mongodb_name["customer_info"]
    customer_id = customer.id_id
    content_id = content.id
    if content.content_type == "article":
        collection_content = mongodb_name["articles"]
        logging.debug("article")
    elif content.content_type == "video":
        collection_content = mongodb_name["videos"]
        logging.debug("video")
    else:
        logging.debug("short")
        collection_content = mongodb_name["shorts"]
    logging.debug(content_id)
    if content.content_type == "article":
        content_mongo = collection_content.find_one({"content_id": int(content_id)})
    else:
        content_mongo = collection_content.find_one({"content_id": str(content_id)})
    content_keywords = content_mongo["keywords"]
    customer_mongo = collection_customer.find_one({"customer_id": customer_id})
    customer_keywords = customer_mongo["keywords"]
    for i in content_keywords:
        if i in customer_keywords.keys():
            customer_keywords[i] -= 1
    collection_customer.update_one({"customer_id": customer_id}, {'$set': {"keywords": customer_keywords}})
    operation = content_like.delete()
    content.like_count -= 1
    content.save()
    data = {}
    if operation:
        data["like_count"] = content.like_count
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
        content = Content.objects.get(id=request.data["content"])
        sponsor_tier = SponsorTier.objects.get(id=request.data["sponsor_tier"])
        if serializer.is_valid():
            sponsor_tier_content = SponsorTierContent.objects.create(content=content,
                                                                     sponsor_tier=sponsor_tier)
            content.is_paid = True
            content.save()
            data = {
                "id": sponsor_tier_content.id
            }
            return Response(data, status=status.HTTP_201_CREATED)
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
def api_delete_sponsor_tier_content_view(request, content_id, sponsor_tier_id):
    try:
        content = Content.objects.get(id=content_id)
        sponsor_tier = SponsorTier.objects.get(id=sponsor_tier_id)
        sponsor_tier_content = SponsorTierContent.objects.get(content=content,sponsor_tier=sponsor_tier)
    except SponsorTierContent.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if request.method == "DELETE":
        operation = sponsor_tier_content.delete()
        sponsor_tier_contents = SponsorTierContent.objects.filter(content=content)
        if not sponsor_tier_contents.exists():
            content.is_paid = False
            content.save()
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
        customer = Customer.objects.get(id=request.data["customer"])
        sponsor_tier = SponsorTier.objects.get(id=request.data["sponsor_tier"])
        if serializer.is_valid():
            sponsor_sub = SponsorSubscription.objects.create(customer=customer,
                                                             sponsor_tier=sponsor_tier)
            data = {
                "id": sponsor_sub.id
            }
            return Response(data, status=status.HTTP_201_CREATED)
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
def api_delete_sponsor_subscription_view(request, sponsor_tier_id, customer_id):
    try:
        sponsor_tier = SponsorTier.objects.get(id=sponsor_tier_id)
        customer = Customer.objects.get(id=customer_id)
        sponsor_subscription = SponsorSubscription.objects.get(customer=customer, sponsor_tier=sponsor_tier)
    except SponsorSubscription.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if request.method == "DELETE":
        operation = sponsor_subscription.delete()
        data = {}
        if operation:
            data["success"] = "delete successful"
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        return Response(data=data)


# //////subscription//////
@api_view(['POST', ])
def api_create_subscription_view(request):
    subscription = Subscription()
    customer_id = request.data["customer"]
    creator_id = request.data["creator"]
    customer = Customer.objects.get(id=customer_id)
    creator = Creator.objects.get(id=creator_id)
    if request.method == "POST":
        serializer = SubscriptionSerializer(subscription, data=request.data)
        if serializer.is_valid():
            subscription = Subscription.objects.create(customer=customer,
                                                       creator=creator)
            data = {
                "id": subscription.id
            }
            return Response(data, status=status.HTTP_201_CREATED)
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
def api_delete_subscription_view(request, creator_id, customer_id):
    try:
        creator = Creator.objects.get(id=creator_id)
        customer = Customer.objects.get(id=customer_id)
        subscription = Subscription.objects.get(creator=creator,customer=customer)
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



"""
URL configuration for health_care_backend project.
"""
from django.contrib import admin
from django.urls import path
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from lifeHealther.views import (
    api_create_user_view,
    api_get_user_view,
    api_update_user_view,
    api_delete_user_view,
    api_create_creator_view,
    api_create_my_user_view,
    api_get_my_user_view,
    api_update_my_user_view,
    api_delete_my_user_view,
    api_get_creator_view,
    api_update_creator_view,
    api_delete_creator_view,
    api_create_customer_view,
    api_get_customer_view,
    api_update_customer_view,
    api_delete_customer_view,
    api_create_administrator_view,
    api_get_administrator_view,
    api_update_administrator_view,
    api_delete_administrator_view,
    api_create_moderator_view,
    api_get_moderator_view,
    api_update_moderator_view,
    api_delete_moderator_view,
    api_create_content_view,
    api_get_content_view,
    api_update_content_view,
    api_delete_content_view,
    api_create_comment_view,
    api_get_comment_view,
    api_update_comment_view,
    api_delete_comment_view,
    api_create_comment_like_view,
    api_get_comment_like_view,
    api_update_comment_like_view,
    api_delete_comment_like_view,
    api_create_content_like_view,
    api_get_content_like_view,
    api_update_content_like_view,
    api_delete_content_like_view,
    api_create_sponsor_tier_view,
    api_get_sponsor_tier_view,
    api_update_sponsor_tier_view,
    api_delete_sponsor_tier_view,
    api_create_sponsor_tier_content_view,
    api_get_sponsor_tier_content_view,
    api_update_sponsor_tier_content_view,
    api_delete_sponsor_tier_content_view,
    api_create_sponsor_subscription_view,
    api_get_sponsor_subscription_view,
    api_update_sponsor_subscription_view,
    api_delete_sponsor_subscription_view,
    api_create_subscription_view,
    api_get_subscription_view,
    api_update_subscription_view,
    api_delete_subscription_view,
    # api_create_test_mongo_view,
    api_login_view,
    api_create_article_mongo_view,
    api_create_video_mongo_view,
    api_get_article_mongo_view,
    api_create_creator_mongo_view,
    api_get_free_articles_content_view,
    api_get_free_videos_content_view,
    api_get_video_info_mongo_view,
    api_get_creators_articles_content_view,
    api_get_creators_videos_content_view,
    api_get_video_mongo_view,
    api_delete_video_view,
    api_delete_article_view,
    api_find_article_view,
    api_find_video_info_view,
    api_create_shorts_mongo_view,
    api_update_video_mongo_view,
    api_update_article_mongo_view,
    api_get_creator_diplomas_mongo_view,
    api_create_diploma_mongo_view,
    api_get_diploma_mongo_view,
    api_get_creator_info_view,
    api_get_creator_mongo_view,
    api_update_creator_avatar_mongo_view,
    api_login_view,
    api_create_customer_mongo_view,
    api_get_customer_mongo_view,
    api_get_customer_subs_view,
    api_customer_viewed_mongo_view,
    api_get_customer_content_view,api_get_free_shorts_content_view,
    api_get_short_info_mongo_view,
    api_get_creators_shorts_content_view,
    api_get_short_mongo_view,
    api_delete_short_view,
    api_find_short_info_view,
    api_update_short_mongo_view,
    api_create_sponsor_tier_mongo_view,
    api_get_sponsor_tier_mongo_view,
    api_update_sponsor_tier_mongo_view,
    api_get_sponsor_tier_creator_content,
    api_get_sponsor_tier_creator_no_content,
    api_get_creators_sponsor_tiers_view,
    api_delete_sponsor_tier_view,
    api_load_creator,
    api_fined_view,
    api_get_moder_diplomas,
    api_delete_diploma,
    api_update_diploma
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('user/create', api_create_user_view),
    path('user/<int:user_id>', api_get_user_view),
    path('user/<int:user_id>/delete', api_delete_user_view),
    path('user/<int:user_id>/update', api_update_user_view),
    path('creator/create', api_create_creator_view),
    path('creator/<int:creator_id>', api_get_creator_view),
    path('creator/<int:creator_id>/delete', api_delete_creator_view),
    path('creator/<int:creator_id>/update', api_update_creator_view),
    path('my_user/create', api_create_my_user_view),
    path('my_user/<int:my_user_id>', api_get_my_user_view),
    path('my_user/<int:my_user_id>/delete', api_delete_my_user_view),
    path('my_user/<int:my_user_id>/update', api_update_my_user_view),
    path('administrator/create', api_create_administrator_view),
    path('administrator/<int:administrator_id>', api_get_administrator_view),
    path('administrator/<int:administrator_id>/delete', api_delete_administrator_view),
    path('administrator/<int:administrator_id>/update', api_update_administrator_view),
    path('moderator/create', api_create_moderator_view),
    path('moderator/<int:moderator_id>', api_get_moderator_view),
    path('moderator/<int:moderator_id>/delete', api_delete_moderator_view),
    path('moderator/<int:moderator_id>/update', api_update_moderator_view),
    path('customer/create', api_create_customer_view),
    path('customer/<int:customer_id>', api_get_customer_view),
    path('customer/<int:customer_id>/delete', api_delete_customer_view),
    path('customer/<int:customer_id>/update', api_update_customer_view),
    path('content/create', api_create_content_view),
    path('content/<int:content_id>', api_get_content_view),
    path('content/<int:content_id>/delete', api_delete_content_view),
    path('content/<int:content_id>/update', api_update_content_view),
    path('comment/create', api_create_comment_view),
    path('comment/<int:content_id>', api_get_comment_view),
    path('comment/<int:comment_id>/delete', api_delete_comment_view),
    path('comment/<int:comment_id>/update', api_update_comment_view),
    path('comment_like/create', api_create_comment_like_view),
    path('comment_like/<int:comment_like_id>', api_get_comment_like_view),
    path('comment_like/<int:comment_like_id>/delete', api_delete_comment_like_view),
    path('comment_like/<int:comment_like_id>/update', api_update_comment_like_view),

    path('content_like/create', api_create_content_like_view),
    path('content_like/<int:content_id>/<int:customer_id>', api_get_content_like_view),
    path('content_like/delete/<int:content_id>/<int:customer_id>', api_delete_content_like_view),
    path('content_like/<int:content_like_id>/update', api_update_content_like_view),

    path('sponsor_tier/create', api_create_sponsor_tier_view),
    path('sponsor_tier/<int:sponsor_tier_id>', api_get_sponsor_tier_view),
    path('sponsor_tier/<int:sponsor_tier_id>/delete', api_delete_sponsor_tier_view),
    path('sponsor_tier/<int:sponsor_tier_id>/update', api_update_sponsor_tier_view),
    path('sponsor_tier_content/create', api_create_sponsor_tier_content_view),
    path('sponsor_tier_content/<int:sponsor_tier_content_id>', api_get_sponsor_tier_content_view),
    path('sponsor_tier_content/delete/<int:sponsor_tier_id>/<int:content_id>', api_delete_sponsor_tier_content_view),
    path('sponsor_tier_content/<int:sponsor_tier_content_id>/update', api_update_sponsor_tier_content_view),
    path('sponsor_subscription/create', api_create_sponsor_subscription_view),
    path('sponsor_subscription/<int:sponsor_subscription_id>', api_get_sponsor_subscription_view),
    path('sponsor_subscription/delete/<int:sponsor_tier_id>/<int:customer_id>', api_delete_sponsor_subscription_view),
    path('sponsor_subscription/<int:sponsor_subscription_id>/update', api_update_sponsor_subscription_view),
    path('subscription/create', api_create_subscription_view),
    path('subscription/<int:subscription_id>', api_get_subscription_view),
    path('subscription/delete/<int:creator_id>/<int:customer_id>', api_delete_subscription_view),
    path('subscription/<int:subscription_id>/update', api_update_subscription_view),
    # path('test_mongo',api_create_test_mongo_view),
    path('article/create', api_create_article_mongo_view),
    path('login', api_login_view),
    path('article/<int:content_id>', api_get_article_mongo_view),
    path('creator_mongo/create', api_create_creator_mongo_view),
    path('article/free', api_get_free_articles_content_view),
    # video
    path("video/create", api_create_video_mongo_view),
    path('video/free', api_get_free_videos_content_view),
    path('video/info/<str:content_id>', api_get_video_info_mongo_view),
    path("video/creator/<int:creator_id>", api_get_creators_videos_content_view),
    path('video/<str:content_id>', api_get_video_mongo_view),
    path("video/delete/<str:content_id>", api_delete_video_view),
    path("video/find/<str:keyword>", api_find_video_info_view),
    path('video/update/<str:content_id>', api_update_video_mongo_view),
    # short
    path('short/create', api_create_shorts_mongo_view),
    path('short/free', api_get_free_shorts_content_view),
    path('short/info/<str:content_id>', api_get_short_info_mongo_view),
    path("short/creator/<int:creator_id>", api_get_creators_shorts_content_view),
    path('short/<str:content_id>', api_get_short_mongo_view),
    path("short/delete/<str:content_id>", api_delete_short_view),
    path("short/find/<str:keyword>", api_find_short_info_view),
    path('short/update/<str:content_id>', api_update_short_mongo_view),

    path('article/delete/<int:content_id>', api_delete_article_view),
    path('article/find/<str:keyword>', api_find_article_view),
    path("article/creator/<int:creator_id>", api_get_creators_articles_content_view),
    path('article/update/<int:content_id>', api_update_article_mongo_view),
    path('diploma/creator/get/<int:creator_id>', api_get_creator_diplomas_mongo_view),
    path('diploma/create', api_create_diploma_mongo_view),
    path('diploma/<str:diploma_id>', api_get_diploma_mongo_view),
    path('creator/info/<int:creator_id>', api_get_creator_info_view),
    path('creator/mongo/<int:creator_id>', api_get_creator_mongo_view),
    path('creator/update/avatar/<int:creator_id>', api_update_creator_avatar_mongo_view),
    path('login', api_login_view),
    path('customer_mongo/create', api_create_customer_mongo_view),
    path('customer/mongo/<int:customer_id>', api_get_customer_mongo_view),
    path('customer/subs/<int:customer_id>', api_get_customer_subs_view),
    path('customer/viewed/<int:customer_id>', api_customer_viewed_mongo_view),
    path('recomendetion/<str:content_type>/<int:customer_id>', api_get_customer_content_view),
#     sponsor tier mongo
    path('sponsor_tier/mongo/create', api_create_sponsor_tier_mongo_view),
    path('sponsor_tier/mongo/<int:sponsor_tier_id>', api_get_sponsor_tier_mongo_view),
    path('sponsor_tier/mongo/update/<int:sponsor_tier_id>', api_update_sponsor_tier_mongo_view),
    path('sponsor_tier/mongo/delete/<int:sponsor_tier_id>', api_delete_sponsor_tier_view),
#     sponsor_tier_else
    path('sponsor_tier/creator/content/<int:sponsor_tier_id>', api_get_sponsor_tier_creator_content),
    path('sponsor_tier/creator/content/no/<int:sponsor_tier_id>', api_get_sponsor_tier_creator_no_content),
    path('sponsor_tier/creator/<int:creator_id>', api_get_creators_sponsor_tiers_view),

    path('load_creator/<int:creator_id>/<int:customer_id>', api_load_creator),

    path("fined/<int:customer_id>/<str:keyword>", api_fined_view),
    path("moder/diplomas", api_get_moder_diplomas),
    path("diploma/delete", api_delete_diploma),
    path("diploma/update", api_update_diploma)
]

urlpatterns += staticfiles_urlpatterns()

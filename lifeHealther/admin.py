from django.contrib import admin
from .models import (
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


admin.site.register(MyUser)
admin.site.register(Administrator)
admin.site.register(Moderator)
admin.site.register(Customer)
admin.site.register(Creator)
admin.site.register(Content)
admin.site.register(Comment)
admin.site.register(CommentLike)
admin.site.register(ContentLike)
admin.site.register(SponsorTier)
admin.site.register(SponsorSubscription)
admin.site.register(SponsorTierContent)
admin.site.register(Subscription)
# Register your models here.

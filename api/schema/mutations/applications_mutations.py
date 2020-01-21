from django.core.exceptions import ValidationError

from api.applications.models import ShowApplication, TimeSlotRequest, ShowApplicationSettings
from api.shows.models import ShowCategory

import graphene
import os.path

__all__ = ['SendApplicationMutation']

class TimeSlotInput(graphene.InputObjectType):
    day = graphene.Int(required=True)
    hour = graphene.Int(required=True)

class SendApplicationMutation(graphene.Mutation):
    class Arguments:
        name = graphene.String(required=True)
        short_description = graphene.String(required=True)
        long_description = graphene.String(required=True)
        biweekly = graphene.Boolean()
        new = graphene.Boolean()

        host_name = graphene.String(required=True)
        contact_email = graphene.String(required=True)
        contact_phone = graphene.String(required=True)
        producer_name = graphene.String()

        cover_filename = graphene.String()
        banner_filename = graphene.String()

        category = graphene.String(required=True)
        brand_color = graphene.String(required=True)
        emoji_description = graphene.String(required=True)

        first_slot = TimeSlotInput(required=True)
        second_slot = TimeSlotInput(required=True)
        third_slot = TimeSlotInput(required=True)

        social_facebook_url = graphene.String()
        social_twitter_handle = graphene.String()
        social_mixcloud_handle = graphene.String()
        social_snapchat_handle = graphene.String()
        social_instagram_handle = graphene.String()
        social_youtube_url = graphene.String()

    success = graphene.Boolean()
    problems = graphene.List(graphene.String)

    @staticmethod
    def mutate(
        root, info,
        name, short_description, long_description, biweekly, new,
        host_name, contact_email, contact_phone, producer_name,
        category, brand_color, emoji_description,
        first_slot, second_slot, third_slot,
        social_facebook_url=None, social_twitter_handle=None, social_mixcloud_handle=None, social_snapchat_handle=None,
        social_instagram_handle=None, social_yotube_url=None,
        cover_filename="", banner_filename=""
    ):
        settings = ShowApplicationSettings.get_solo()

        if not settings.applications_open:
            return SendApplicationMutation(success=False, problems=["Show applications are not open, try again later"])

        show_category = ShowCategory.objects.get(slug=category)
        brand_color = brand_color.lstrip('#')

        first, _ = TimeSlotRequest.objects.get_or_create(day=first_slot.day, hour=first_slot.hour)
        second, _ = TimeSlotRequest.objects.get_or_create(day=second_slot.day, hour=second_slot.hour)
        third, _ = TimeSlotRequest.objects.get_or_create(day=third_slot.day, hour=third_slot.hour)

        cover = None
        if cover_filename.strip():
            cover = os.path.join("content/shows/covers", os.path.basename(cover_filename))

        banner = None
        if banner_filename.strip():
            banner = os.path.join("content/shows/banners", os.path.basename(banner_filename))

        application = ShowApplication(
            name=name, short_description=short_description, long_description=long_description,
            category=show_category, brand_color=brand_color, emoji_description=emoji_description,
            biweekly=biweekly, new_show=new, host_name=host_name, contact_phone=contact_phone,
            contact_email=contact_email, producer_name=producer_name,
            first_slot_choice=first, second_slot_choice=second, third_slot_choice=third,
            social_facebook_url=social_facebook_url, social_twitter_handle=social_twitter_handle,
            social_mixcloud_handle=social_mixcloud_handle, social_snapchat_handle=social_snapchat_handle,
            social_instagram_handle=social_instagram_handle, social_youtube_url=social_yotube_url,
            cover=cover, banner=banner
        )

        try:
            application.full_clean()
        except ValidationError as err:
            return SendApplicationMutation(success=False, problems=err.messages)

        application.save()
        return SendApplicationMutation(success=True)

from graphene_django import DjangoObjectType
import graphene
from api.shows.models import Show, ShowSlot, ScheduleSlate, ShowEpisode, ShowSeries, EpisodeCredit
from api.users.models import User


class ShowSlotType(DjangoObjectType):
    class Meta:
        model = ShowSlot


class ScheduleSlateType(DjangoObjectType):
    class Meta:
        model = ScheduleSlate


class EpisodeCreditType(DjangoObjectType):
    class Meta:
        model = EpisodeCredit

    member = graphene.Field(lambda: MembersType)

    def resolve_member(self, args, context, info):
        return self.user


class ShowEpisodeType(DjangoObjectType):
    class Meta:
        model = ShowEpisode

    credits = graphene.List(EpisodeCreditType)

    def resolve_credits(self, args, context, info):
        return EpisodeCredit.objects.filter(episode=self)

#
# class ShowSeriesType(DjangoObjectType):
#     class Meta:
#         model = ShowSeries


class MembersType(DjangoObjectType):
    class Meta:
        model = User
        only_fields = ('username', 'name', )


class ShowType(DjangoObjectType):
    slots = graphene.List(ShowSlotType)
    #series = graphene.List(ShowSeriesType)
    episodes = graphene.List(ShowEpisodeType)

    def resolve_slots(self, args, context, info):
        return self.slots.filter(slate=get_current_slate())

    # def resolve_series(self, args, context, info):
    #     return self.series.all()

    def resolve_episodes(self, args, context, info):
        return self.episodes.all()

    class Meta:
        model = Show


class Query(graphene.ObjectType):
    all_shows = graphene.List(ShowType, )
    all_slots = graphene.List(ShowSlotType, )
    all_slates = graphene.List(ScheduleSlateType, )
    all_episodes = graphene.List(ShowEpisodeType, )
    all_members = graphene.List(MembersType, )
    show = graphene.Field(ShowType, slug=graphene.String())

    def resolve_show(self, args, context, info):
        slug = args.get('slug')
        return Show.objects.get(slug=slug)

    def resolve_all_shows(self, args, context, info):
        return Show.objects.all()

    def resolve_all_members(self, args, context, info):
        return User.objects.all()

    def resolve_all_slates(self, args, context, info):
        return ScheduleSlate.objects.all()

    def resolve_all_episodes(self, args, context, info):
        return ShowEpisode.objects.all()

    def resolve_all_slots(self, args, context, info):
        return ShowSlot.objects.all()

schema = graphene.Schema(query=Query)

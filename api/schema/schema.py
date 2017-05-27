from django.contrib.auth import authenticate
from graphene import ObjectType, Node
from graphene_django import DjangoObjectType, DjangoConnectionField
from rest_framework.authtoken.models import Token
import graphene
from api.shows import models as show_models
from api.users import models as user_models



def connection_for_type(_type):
    class Connection(graphene.Connection):
        total_count = graphene.Int()

        class Meta:
            name = _type._meta.name + 'Connection'
            node = _type

        def resolve_total_count(self, args, context, info):
            return self.length

    return Connection

class EmbeddedImage(ObjectType):
    width = graphene.Int()
    height = graphene.Int()
    resource = graphene.String()


class BaseUser(graphene.Interface):
    username = graphene.String()
    name = graphene.String()
    cover = graphene.Field(EmbeddedImage)



def get_embedded_image(model, name):
    if getattr(model, name) is None:
        return None

    return EmbeddedImage(
        resource=getattr(model, name),
        width=getattr(model, '{}_width'.format(name)),
        height=getattr(model, '{}_height'.format(name)),
    )

class ShowSlot(DjangoObjectType):
    class Meta:
        model = show_models.ShowSlot
        interfaces = (Node, )

    day = graphene.Field(graphene.Int)

    def resolve_day(self, args, context, info):
        return self.day


class EpisodeCredit(DjangoObjectType):
    class Meta:
        model = show_models.EpisodeCredit
        interfaces = (Node, )

    member = graphene.Field(lambda: User)

    def resolve_member(self, args, context, info):
        return self.user


class ShowEpisode(DjangoObjectType):
    class Meta:
        model = show_models.ShowEpisode
        interfaces = (Node, )

    credits = graphene.List(EpisodeCredit)
    cover = graphene.Field(EmbeddedImage)

    def resolve_credits(self, args, context, info):
        return show_models.EpisodeCredit.objects.filter(episode=self)

    def resolve_cover(self, args, context, info):
        return get_embedded_image(self, 'cover')


class ShowSeries(DjangoObjectType):
    class Meta:
        model = show_models.ShowSeries


class User(DjangoObjectType):
    class Meta:
        model = user_models.User
        interfaces = (Node, BaseUser)
        only_fields = ('username', 'name', )


class Show(DjangoObjectType):
    class Meta:
        model = show_models.Show
        interfaces = (Node, )

    slots = graphene.List(ShowSlot)
    #series = graphene.List(ShowSeriesType)
    episodes = graphene.List(ShowEpisode)
    cover = graphene.Field(EmbeddedImage)

    def resolve_slots(self, args, context, info):
        return self.slots.filter(slate=show_models.ShowsConfiguration.objects.get().current_slate)

    # def resolve_series(self, args, context, info):
    #     return self.series.all()

    def resolve_episodes(self, args, context, info):
        return self.episodes.all()

    def resolve_cover(self, args, context, info):
        return get_embedded_image(self, 'cover')


Show.Connection = connection_for_type(Show)


class ScheduleSlate(DjangoObjectType):
    class Meta:
        model = show_models.ScheduleSlate
        interfaces = (Node, )

    slots = graphene.List(ShowSlot)
    shows = graphene.List(Show)

    def resolve_shows(self, args, context, info):
        return self.get_shows()


class Login(graphene.Mutation):
    class Input:
        username = graphene.String()
        password = graphene.String()

    token = graphene.String()
    success = graphene.Boolean()

    @staticmethod
    def mutate(root, args, context, info):
        user = authenticate(username=args.get('username'), password=args.get('password'))

        if user is None:
            return Login(success=False)

        token, created = Token.objects.get_or_create(user=user)

        return Login(token=token, success=True)


class Query(graphene.ObjectType):
    all_shows = DjangoConnectionField(Show, )
    current_slate = graphene.Field(ScheduleSlate, )
    all_slots = graphene.List(ShowSlot, )
    all_slates = graphene.List(ScheduleSlate, )
    all_episodes = graphene.List(ShowEpisode, )
    show = graphene.Field(Show, slug=graphene.String())
    automation_show = graphene.Field(Show, description='Show used when nothing is scheduled')

    # Members
    all_members = graphene.List(User, )
    viewer = graphene.Field(User, description='The current user')


    def resolve_show(self, args, context, info):
        slug = args.get('slug')
        return show_models.Show.objects.get(slug=slug)

    def resolve_automation_show(self, args, context, info):
        return show_models.ShowsConfiguration.objects.get().automation_show

    def resolve_current_slate(self, args, context, info):
        return show_models.ShowsConfiguration.objects.get().current_slate

    def resolve_all_shows(self, args, context, info):
        return show_models.Show.objects.all()

    def resolve_all_members(self, args, context, info):
        return user_models.User.objects.all()

    def resolve_all_slates(self, args, context, info):
        return show_models.ScheduleSlate.objects.all()

    def resolve_all_episodes(self, args, context, info):
        return show_models.ShowEpisode.objects.all()

    def resolve_all_slots(self, args, context, info):
        return show_models.ShowSlot.objects.filter(slate=show_models.ShowsConfiguration.objects.get().current_slate)

    def resolve_viewer(self, args, context, info):
        return context.user if context.user.is_authenticated else None


class Mutations(graphene.ObjectType):
        login = Login.Field()


schema = graphene.Schema(query=Query, mutation=Mutations)

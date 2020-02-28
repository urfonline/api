from django.utils import timezone
from django.contrib.auth import authenticate
from graphene import ObjectType, Node
from graphene_django import DjangoObjectType, DjangoConnectionField
from graphene_django.converter import convert_django_field
from rest_framework.authtoken.models import Token
import graphene
from taggit.managers import TaggableManager
from wagtail.wagtailcore.rich_text import expand_db_html

from api.shows import models as show_models
from api.applications import models as application_models
from api.users import models as user_models
from api.articles import models as article_models
from api.events import models as events_models
from api.core import models as core_models
from api.home import models as home_models
from api.streams import models as stream_models
from api.podcasts import models as podcast_models

from .mutations.applications_mutations import *

def connection_for_type(_type):
    class Connection(graphene.Connection):
        total_count = graphene.Int()

        class Meta:
            name = _type._meta.name + 'Connection'
            node = _type

        def resolve_total_count(self, info):
            return self.length

    return Connection


@convert_django_field.register(TaggableManager)
def convert_taggable(field, registry):
    return []


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

    def resolve_day(self, info):
        return self.day


class EpisodeCredit(DjangoObjectType):
    class Meta:
        model = show_models.EpisodeCredit
        interfaces = (Node, )

    member = graphene.Field(lambda: User)

    def resolve_member(self, info):
        return self.user


class ShowCategory(DjangoObjectType):
    class Meta:
        model = show_models.ShowCategory

    shows = graphene.List(lambda: Show)

    def resolve_shows(self, info):
        return self.shows.all()


class ShowEpisode(DjangoObjectType):
    class Meta:
        model = show_models.ShowEpisode
        interfaces = (Node, )

    credits = graphene.List(EpisodeCredit)
    cover = graphene.Field(EmbeddedImage)

    def resolve_credits(self, info):
        return show_models.EpisodeCredit.objects.filter(episode=self)

    def resolve_cover(self, info):
        return get_embedded_image(self, 'cover')


class ShowSeries(DjangoObjectType):
    class Meta:
        model = show_models.ShowSeries


class StreamConfiguration(DjangoObjectType):
    class Meta:
        model = stream_models.StreamConfiguration
        interfaces = (Node, )


class User(DjangoObjectType):
    class Meta:
        model = user_models.User
        interfaces = (Node, BaseUser)
        only_fields = ('username', 'name', )

class ShowAppplicationSettings(DjangoObjectType):
    class Meta:
        model = application_models.ShowApplicationSettings
        interfaces = (Node, )

class Show(DjangoObjectType):
    class Meta:
        model = show_models.Show
        interfaces = (Node, )

    slots = graphene.List(ShowSlot)
    #series = graphene.List(ShowSeriesType)
    category = graphene.Field(ShowCategory)
    episodes = graphene.List(ShowEpisode)
    cover = graphene.Field(EmbeddedImage)

    def resolve_slots(self, info):
        return self.slots.filter(slate=show_models.ShowsConfiguration.objects.get().current_slate)

    # def resolve_series(self, args, context, info):
    #     return self.series.all()

    def resolve_episodes(self, info):
        return self.episodes.all()

    def resolve_cover(self, info):
        return get_embedded_image(self, 'cover')


Show.Connection = connection_for_type(Show)


class ScheduleSlate(DjangoObjectType):
    class Meta:
        model = show_models.ScheduleSlate
        interfaces = (Node, )

    slots = graphene.List(ShowSlot)
    shows = graphene.List(Show)

    def resolve_shows(self, info):
        return self.get_shows()

    def resolve_slots(self, info):
        return self.slots.select_related('show', 'show__category').all()


class Image(DjangoObjectType):
    resource = graphene.String()
    media_id = graphene.Int()

    def resolve_resource(self, info):
        return self.file.name

    def resolve_media_id(self, info):
        return self.pk

    class Meta:
        model = core_models.UrfImage
        interfaces = (graphene.relay.Node, )
        only_fields = ('resource', 'media_id')


class Article(DjangoObjectType):
    class Meta:
        model = article_models.Article
        interfaces = (Node, )

    article_id = graphene.Int()
    associated_show = graphene.Field(Show)
    authors = graphene.List(User)
    featured_image = graphene.Field(Image)
    body_html = graphene.String()

    def resolve_article_id(self, info):
        return self.pk

    def resolve_associated_show(self, info):
        return self.associated_show

    def resolve_authors(self, info):
        return self.authors.all()

    def resolve_featured_image(self, info):
        return self.featured_image

    def resolve_body_html(self, info):
        return expand_db_html(self.content)

Article.Connection = connection_for_type(Article)


class Event(DjangoObjectType):
    class Meta:
        model = events_models.Event
        interfaces = (Node, )

    event_id = graphene.Int()
    # associated_show = graphene.Field(Show)
    # authors = graphene.List(User)
    featured_image = graphene.Field(Image)
    description_html = graphene.String()

    def resolve_event_id(self, info):
        return self.pk

    def resolve_associated_show(self, info):
        return self.associated_show

    def resolve_authors(self, info):
        return self.authors.all()

    def resolve_featured_image(self, info):
        return self.featured_image

    def resolve_description_html(self, info):
        return expand_db_html(self.description)

Event.Connection = connection_for_type(Event)


class HomepageBlockObjectUnion(graphene.Union):
    class Meta:
        types = (Show, Event, Article)


class HomepageBlock(DjangoObjectType):
    class Meta:
        model = home_models.HomepageBlock

    object = graphene.Field(HomepageBlockObjectUnion)

    def resolve_object(self, info):
        return self.content_object


class StaticSitePayload(graphene.ObjectType):
    shows = graphene.List(Show)
    events = graphene.List(Event)
    articles = graphene.List(Article)

    def resolve_shows(self, info):
        return show_models.Show.objects.all()

    def resolve_events(self, info):
        return events_models.Event.objects.select_related('featured_image').all()

    def resolve_articles(self, info):
        return article_models.Article.objects.select_related('featured_image').all()

class PodcastEpisode(graphene.ObjectType):
    title = graphene.String()
    description = graphene.String()
    created_at = graphene.DateTime()
    media_url = graphene.String()
    cover_url = graphene.String()
    duration = graphene.String()
    is_explicit = graphene.Boolean()

class Podcast(graphene.ObjectType):
    title = graphene.String()
    description = graphene.String()
    cover_url = graphene.String()
    episodes = graphene.List(PodcastEpisode,)

class Login(graphene.Mutation):
    class Arguments:
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
    homepage = graphene.List(HomepageBlock, )
    all_shows = DjangoConnectionField(Show, )
    current_slate = graphene.Field(ScheduleSlate, )
    all_slots = graphene.List(ShowSlot, )
    all_slates = graphene.List(ScheduleSlate, )
    all_episodes = graphene.List(ShowEpisode, )
    all_streams = graphene.List(StreamConfiguration, )
    all_categories = graphene.List(ShowCategory, )
    all_podcasts = graphene.List(Podcast, )
    show = graphene.Field(Show, slug=graphene.String())
    stream = graphene.Field(StreamConfiguration, slug=graphene.String())
    automation_show = graphene.Field(Show, description='Show used when nothing is scheduled')
    application_settings = graphene.Field(ShowAppplicationSettings, )

    static_site_payload = graphene.Field(StaticSitePayload)

    # articles
    all_articles = DjangoConnectionField(Article, )
    article = graphene.Field(Article, article_id=graphene.Int())

    # events
    all_events = DjangoConnectionField(Event, )
    event = graphene.Field(Event, event_id=graphene.Int())

    # Members
    all_members = graphene.List(User, )
    viewer = graphene.Field(User, description='The current user')

    def resolve_homepage(self, info):
        return home_models.HomepageBlock.objects.order_by('position', '-published_at')\
            .distinct('position')

    def resolve_show(self, info, slug):
        return show_models.Show.objects.get(slug__iexact=slug)

    def resolve_stream(self, info, slug):
        return stream_models.StreamConfiguration.objects.get(slug__iexact=slug)

    def resolve_automation_show(self, info):
        return show_models.ShowsConfiguration.objects.get().automation_show

    def resolve_current_slate(self, info):
        return show_models.ShowsConfiguration.objects.get().current_slate

    def resolve_all_shows(self, info):
        return show_models.Show.objects.all()

    def resolve_all_members(self, info):
        return user_models.User.objects.all()

    def resolve_all_slates(self, info):
        return show_models.ScheduleSlate.objects.all()

    def resolve_all_episodes(self, info):
        return show_models.ShowEpisode.objects.all()

    def resolve_all_slots(self, info):
        return show_models.ShowSlot.objects.filter(slate=show_models.ShowsConfiguration.objects.get().current_slate)

    def resolve_all_streams(self, info):
        return stream_models.StreamConfiguration.objects\
            .select_related('slate')\
            .prefetch_related('slate__slots', 'slate__slots__show')\
            .all()

    def resolve_all_categories(self, info):
        return show_models.ShowCategory.objects.all()

    def resolve_all_podcasts(self, info):
        for podcast in podcast_models.Podcast.objects.all():
            yield podcast.fetch_details()

    def resolve_static_site_payload(self, info):
        return True

    def resolve_all_articles(self, info):
        return article_models.Article.objects\
            .filter(published_at__lte=timezone.now())\
            .order_by('-published_at')

    def resolve_article(self, info, article_id):
        return article_models.Article.objects.get(pk=article_id)

    def resolve_all_events(self, info):
        return events_models.Event.objects\
            .order_by('start_date')

    def resolve_event(self, info, event_id):
        return events_models.Event.objects.get(pk=event_id)

    def resolve_application_settings(self, info):
        return application_models.ShowApplicationSettings.objects.get()

    def resolve_viewer(self, info):
        return info.context.user if info.context.user.is_authenticated else None


class Mutations(graphene.ObjectType):
        login = Login.Field()
        apply = SendApplicationMutation.Field()

schema = graphene.Schema(query=Query, mutation=Mutations)

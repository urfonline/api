from xml.etree import ElementTree as ET
from datetime import datetime
import requests

from api.podcasts.remote.interface import PodcastDetails, PodcastEpisode
from api import __version__

HEADERS = {
    "User-Agent": "URF-API/{version}".format(version=__version__),
}

namespaces = {
    'itunes': 'http://www.itunes.com/dtds/podcast-1.0.dtd',
    'atom': 'http://www.w3.org/2005/Atom',
}

def _parse_xml(xmlstr: str) -> PodcastDetails:
    root = ET.fromstring(xmlstr)
    channel = root.find('channel')

    title = channel.find('title').text
    desc = channel.find('description').text
    cover = channel.find('itunes:image', namespaces).attrib['href']
    feed_url = channel.find('atom:link', namespaces).attrib['href']

    episodes = []

    for item in channel.findall('item'):
        ep_title = item.find('title').text
        ep_desc = item.find('description').text
        media_url = item.find('enclosure').attrib['url']
        ep_created = datetime.strptime(item.find('pubDate').text, "%a, %d %b %Y %H:%M:%S %z")
        ep_cover = item.find('itunes:image', namespaces).attrib['href']
        ep_duration = item.find('itunes:duration', namespaces).text
        explicit = item.find('itunes:explicit', namespaces).text == "yes"

        ep = PodcastEpisode(title=ep_title, description=ep_desc, media_url=media_url, cover_url=ep_cover,
                            created_at=ep_created, duration=ep_duration, explicit=explicit)
        episodes.insert(0, ep)

    return PodcastDetails(title=title, description=desc, cover_url=cover, episodes=episodes,
                          external_urls=dict(rss=feed_url))

def fetch_podcast_details(provider, podcast) -> PodcastDetails:
    query = {
        "platform": "radioplayer",
        "client_id": provider.client_id,
        "key": provider.api_key,
        "pod_id": podcast.podcast_id,
        "playlist_id": podcast.playlist_id,
    }

    r = requests.get("http://platform.sharp-stream.com/xmlfeed.php", params=query, headers=HEADERS)
    r.raise_for_status()

    return _parse_xml(r.text)

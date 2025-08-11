from os.path import join, dirname
from typing import Iterable, Union
import requests
import json
import re

from ovos_utils import classproperty
from ovos_utils.ocp import MediaType, PlaybackType, Playlist, MediaEntry
from ovos_utils.parse import fuzzy_match, MatchStrategy
from ovos_utils.process_utils import RuntimeRequirements
from ovos_workshop.decorators import ocp_search
from ovos_workshop.skills.common_play import OVOSCommonPlaybackSkill


class InvidiousSkill(OVOSCommonPlaybackSkill):
    def __init__(self, *args, **kwargs):
        super().__init__(supported_media=[MediaType.MUSIC, MediaType.VIDEO, MediaType.GENERIC],
                         skill_icon=join(dirname(__file__), "res", "invidious.png"),
                         skill_voc_filename="invidious_skill",
                         *args, **kwargs)
        
        # Load configuration
        self.config = self.load_config()
        
        # Invidious instances configuration
        self.invidious_instances = self.get_invidious_instances()
        self.current_instance = 0
        self.search_settings = self.config.get('search_settings', {})
        self.featured_queries = self.config.get('featured_queries', [])

    def load_config(self):
        """Load skill configuration"""
        config_path = join(dirname(__file__), "config.json")
        try:
            with open(config_path, 'r') as f:
                return json.load(f)
        except Exception as e:
            self.log.warning(f"Could not load config.json: {e}")
            return {}

    def get_invidious_instances(self):
        """Get available Invidious instances from redirect.invidious.io and custom config"""
        instances = []
        
        # First, try to get instances from redirect.invidious.io
        try:
            response = requests.get("https://redirect.invidious.io/", timeout=10)
            if response.status_code == 200:
                # Parse the HTML to extract instance URLs
                discovered_instances = self.parse_invidious_redirect(response.text)
                if discovered_instances:
                    instances.extend(discovered_instances)
                    self.log.info(f"Found {len(discovered_instances)} instances from redirect.invidious.io")
        except Exception as e:
            self.log.warning(f"Could not fetch instances from redirect.invidious.io: {e}")
        
        # Add custom instances from configuration
        custom_instances = self.config.get('instance_management', {}).get('custom_instances', [])
        if custom_instances:
            instances.extend(custom_instances)
            self.log.info(f"Added {len(custom_instances)} custom instances from configuration")
        
        # Add fallback instances if we don't have enough
        if len(instances) < 3:
            fallback_instances = self.config.get('invidious_instances', [
                "https://invidious.projectsegfau.org",
                "https://invidious.slipfox.xyz",
                "https://invidious.prvcy.projectsegfau.org",
                "https://inv.nadeko.net"
            ])
            instances.extend(fallback_instances)
            self.log.info(f"Added {len(fallback_instances)} fallback instances")
        
        # Remove duplicates and limit total instances
        unique_instances = []
        seen = set()
        max_instances = self.config.get('instance_management', {}).get('max_instances', 15)
        
        for instance in instances:
            if instance not in seen and len(unique_instances) < max_instances:
                unique_instances.append(instance)
                seen.add(instance)
        
        self.log.info(f"Total instances available: {len(unique_instances)}")
        return unique_instances

    def parse_invidious_redirect(self, html_content):
        """Parse HTML content from redirect.invidious.io to extract instance URLs"""
        instances = []
        try:
            # Look for instance URLs in the HTML
            # The site might have a list of instances or redirect links
            url_pattern = r'https?://[^\s<>"\']+\.(?:com|org|net|io|xyz)'
            found_urls = re.findall(url_pattern, html_content)
            
            # Filter for likely Invidious instances
            for url in found_urls:
                if 'invidious' in url.lower() or 'inv.' in url.lower():
                    # Clean the URL
                    clean_url = url.split('"')[0].split("'")[0].split('>')[0].split('<')[0]
                    if clean_url not in instances:
                        instances.append(clean_url)
            
            # If no instances found, try alternative parsing
            if not instances:
                # Look for specific patterns that might indicate Invidious instances
                invidious_pattern = r'https?://[^\s<>"\']*invidious[^\s<>"\']*'
                invidious_urls = re.findall(invidious_pattern, html_content)
                instances.extend(invidious_urls)
                
                # Also look for short domain patterns like inv.nadeko.net
                short_pattern = r'https?://inv\.[^\s<>"\']*'
                short_urls = re.findall(short_pattern, html_content)
                instances.extend(short_urls)
            
            # Remove duplicates and clean URLs
            unique_instances = []
            for instance in instances:
                clean_instance = instance.strip()
                if clean_instance and clean_instance not in unique_instances:
                    unique_instances.append(clean_instance)
            
            return unique_instances[:10]  # Limit to 10 instances
            
        except Exception as e:
            self.log.error(f"Error parsing Invidious instances: {e}")
            return []

    @classproperty
    def runtime_requirements(self):
        return RuntimeRequirements(internet_before_load=True,
                                   network_before_load=True,
                                   gui_before_load=False,
                                   requires_internet=True,
                                   requires_network=True,
                                   requires_gui=False,
                                   no_internet_fallback=False,
                                   no_network_fallback=False,
                                   no_gui_fallback=True)

    def get_invidious_instance(self):
        """Get available Invidious instance"""
        for i in range(len(self.invidious_instances)):
            instance = self.invidious_instances[(self.current_instance + i) % len(self.invidious_instances)]
            try:
                response = requests.get(f"{instance}/api/v1/stats", timeout=5)
                if response.status_code == 200:
                    self.current_instance = (self.current_instance + i) % len(self.invidious_instances)
                    return instance
            except Exception as e:
                self.log.debug(f"Instance {instance} not available: {e}")
                continue
        return self.invidious_instances[0]  # Fallback to first instance

    def search_invidious(self, phrase):
        """Search videos on Invidious"""
        instance = self.get_invidious_instance()
        try:
            # Search videos
            search_url = f"{instance}/api/v1/search"
            params = {
                'q': phrase,
                'type': self.search_settings.get('default_type', 'video'),
                'sort_by': self.search_settings.get('default_sort', 'relevance'),
                'date': 'all',
                'duration': self.search_settings.get('default_duration', 'all'),
                'features': 'hd,subtitles,creative_commons,3d,360,location,hdr,vr180',
                'region': self.search_settings.get('default_region', 'US')
            }
            
            response = requests.get(search_url, params=params, timeout=10)
            if response.status_code == 200:
                results = response.json()
                return self.parse_invidious_results(results)
            else:
                self.log.warning(f"Error in Invidious search: {response.status_code}")
                return []
        except Exception as e:
            self.log.error(f"Error searching on Invidious: {e}")
            return []

    def parse_invidious_results(self, results):
        """Parse Invidious results to compatible objects"""
        parsed_results = []
        max_results = self.search_settings.get('max_results', 20)
        
        for item in results[:max_results]:
            if item.get('type') == 'video':
                # Create object similar to MusicVideo but for Invidious
                video = InvidiousVideo(
                    video_id=item.get('videoId'),
                    title=item.get('title', ''),
                    artist=item.get('author', ''),
                    length=item.get('lengthSeconds', 0),
                    thumbnail_url=item.get('videoThumbnails', [{}])[0].get('url', ''),
                    watch_url=f"https://www.youtube.com/watch?v={item.get('videoId')}",
                    view_count=item.get('viewCount', 0),
                    published=item.get('published', 0)
                )
                parsed_results.append(video)
        
        return parsed_results

    def calc_score(self, phrase, match, idx=0, base_score=0,
                   media_type=MediaType.GENERIC) -> int:
        # idx represents result order
        score = base_score - idx * 5  # - 5% as we go down the list

        if match.artist:
            score += 80 * fuzzy_match(phrase.lower(), match.artist.lower(),
                                      strategy=MatchStrategy.TOKEN_SET_RATIO)
        if match.title:
            score += 80 * fuzzy_match(phrase.lower(), match.title.lower(),
                                      strategy=MatchStrategy.DAMERAU_LEVENSHTEIN_SIMILARITY)

        if media_type == MediaType.GENERIC:
            score -= 10
        return min(100, score)

    @ocp_search()
    def search_invidious_videos(self, phrase, media_type) -> Iterable[Union[MediaEntry, Playlist]]:
        # match requested media type
        base_score = 0
        if media_type == MediaType.MUSIC:
            base_score += 10
        elif media_type == MediaType.VIDEO:
            base_score += 15

        if self.voc_match(phrase, "invidious"):
            # explicitly requested invidious
            base_score += 50
            phrase = self.remove_voc(phrase, "invidious")

        idx = 0
        for v in self.search_invidious(phrase):
            score = self.calc_score(phrase, v, idx,
                                    base_score=base_score,
                                    media_type=media_type)
            
            # return as video entry
            entry = MediaEntry(
                uri=v.watch_url,
                match_confidence=score,
                playback=PlaybackType.AUDIO if media_type == MediaType.MUSIC else PlaybackType.VIDEO,
                media_type=media_type,
                length=v.length * 1000 if v.length else 0,
                image=v.thumbnail_url,
                title=v.title,
                artist=v.artist,
                skill_id=self.skill_id,
                skill_icon=self.skill_icon
            )
            yield entry
            idx += 1


class InvidiousVideo:
    """Class to represent Invidious videos"""
    def __init__(self, video_id, title, artist, length, thumbnail_url, watch_url, view_count, published):
        self.video_id = video_id
        self.title = title
        self.artist = artist
        self.length = length
        self.thumbnail_url = thumbnail_url
        self.watch_url = watch_url
        self.view_count = view_count
        self.published = published


if __name__ == "__main__":
    from ovos_utils.messagebus import FakeBus

    s = InvidiousSkill(bus=FakeBus(), skill_id="t.fake")

    # Test the skill
    for r in s.search_invidious_videos("zz top", MediaType.MUSIC):
        pass  # Silent test

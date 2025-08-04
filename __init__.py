from os.path import join, dirname
import requests
import json
from urllib.parse import quote_plus

from ovos_utils import classproperty
from ovos_utils.ocp import MediaType, PlaybackType, Playlist, MediaEntry
from ovos_utils.parse import fuzzy_match, MatchStrategy
from ovos_utils.process_utils import RuntimeRequirements
from ovos_workshop.decorators import ocp_search
from ovos_workshop.skills.common_play import OVOSCommonPlaybackSkill


class SimpleInvidiousSkill(OVOSCommonPlaybackSkill):
    def __init__(self, *args, **kwargs):
        super().__init__(supported_media=[MediaType.GENERIC, MediaType.VIDEO],
                         skill_icon=join(dirname(__file__), "res", "ytube.jpg"),
                         skill_voc_filename="youtube_skill",
                         *args, **kwargs)

    @classproperty
    def runtime_requirements(self):
        return RuntimeRequirements(internet_before_load=True,
                                   network_before_load=True,
                                   gui_before_load=True,
                                   requires_internet=True,
                                   requires_network=True,
                                   requires_gui=True,
                                   no_internet_fallback=False,
                                   no_network_fallback=False,
                                   no_gui_fallback=False)

    def initialize(self):
        if "fallback_mode" not in self.settings:
            self.settings["fallback_mode"] = False
        if "invidious_instance" not in self.settings:
            self.settings["invidious_instance"] = "https://inv.nadeko.net"
        if "max_results" not in self.settings:
            self.settings["max_results"] = 50

    def _search_invidious(self, query, max_results=50):
        """Search videos using Invidious API"""
        try:
            instance = self.settings["invidious_instance"]
            search_url = f"{instance}/api/v1/search"
            params = {
                'q': query,
                'type': 'video',
                'sort_by': 'relevance',
                'date': 'all',
                'duration': 'all',
                'features': 'hd,subtitles,creative_commons,3d,360,live,hdr',
                'region': 'US'
            }
            
            response = requests.get(search_url, params=params, timeout=10)
            response.raise_for_status()
            
            results = response.json()
            return results[:max_results]
        except Exception as e:
            self.log.error(f"Error searching Invidious: {e}")
            return []

    def _get_video_info(self, video_id):
        """Get detailed video information from Invidious"""
        try:
            instance = self.settings["invidious_instance"]
            video_url = f"{instance}/api/v1/videos/{video_id}"
            
            response = requests.get(video_url, timeout=10)
            response.raise_for_status()
            
            return response.json()
        except Exception as e:
            self.log.error(f"Error getting video info: {e}")
            return None

    def _get_channel_videos(self, channel_id, max_videos=5):
        """Get videos from a channel"""
        try:
            instance = self.settings["invidious_instance"]
            channel_url = f"{instance}/api/v1/channels/{channel_id}/videos"
            
            response = requests.get(channel_url, timeout=10)
            response.raise_for_status()
            
            videos = response.json()
            return videos[:max_videos]
        except Exception as e:
            self.log.error(f"Error getting channel videos: {e}")
            return []

    # score
    def calc_score(self, phrase, video, idx=0, explicit_request=False,
                   base_score=0):

        # shared logic
        score = self.calc_video_score(phrase, video, idx,
                                        explicit_request, base_score)

        # the title says its official!
        if self.voc_match(video.get('title', ''), "official"):
            score += 5

        return min(100, score)

    def calc_video_score(self, phrase, video, idx=0, explicit_request=False,
                           base_score=0):
        # idx represents the order from invidious
        score = base_score - idx  # - 1% as we go down the results list

        title = video.get('title', '')
        score += 100 * fuzzy_match(phrase.lower(), title.lower(),
                                   strategy=MatchStrategy.TOKEN_SET_RATIO)

        # invidious gives pretty high scores in general, so we allow it
        # to run as fallback mode, which assigns lower scores and gives
        # preference to matches from other skills
        if self.settings["fallback_mode"]:
            if not explicit_request:
                score -= 25
        return min(100, score)

    # common play
    @ocp_search()
    def search_invidious(self, phrase, media_type):
        # match the request media_type
        base_score = 0
        if media_type == MediaType.VIDEO:
            base_score += 25
        else:
            base_score -= 50

        explicit_request = False
        if self.voc_match(phrase, "youtube") or self.voc_match(phrase, "invidious"):
            # explicitly requested youtube/invidious
            base_score += 50
            phrase = self.remove_voc(phrase, "youtube")
            phrase = self.remove_voc(phrase, "invidious")
            explicit_request = True

        # Search for videos
        videos = self._search_invidious(phrase, self.settings["max_results"])
        
        idx = 0
        for video in videos:
            if video.get('type') == 'video':
                score = self.calc_score(phrase, video, idx,
                                        base_score=base_score,
                                        explicit_request=explicit_request)
                
                # Convert duration from seconds to milliseconds
                length = video.get('lengthSeconds', 0) * 1000
                
                # Get video URL from Invidious instance
                instance = self.settings["invidious_instance"]
                video_url = f"{instance}/watch?v={video.get('videoId')}"
                
                # return as a video result (single track dict)
                yield MediaEntry(
                    uri=video_url,
                    match_confidence=score,
                    playback=PlaybackType.VIDEO,
                    media_type=MediaType.VIDEO,
                    length=length,
                    image=video.get('videoThumbnails', [{}])[0].get('url', ''),
                    title=video.get('title', ''),
                    skill_id=self.skill_id,
                    skill_icon=self.skill_icon
                )
                idx += 1
            elif video.get('type') == 'channel':
                # Handle channel results if needed
                score = self.calc_video_score(phrase, video, idx,
                                            base_score=base_score,
                                            explicit_request=explicit_request)
                
                # Get channel videos
                channel_videos = self._get_channel_videos(video.get('authorId', ''))
                
                if channel_videos:
                    # create playlist (list of track dicts)
                    max_vids = 5
                    pl = Playlist(
                        match_confidence=score,
                        playback=PlaybackType.VIDEO,
                        media_type=MediaType.VIDEO,
                        image=video.get('authorThumbnails', [{}])[0].get('url', ''),
                        title=video.get('author', '') + " (Invidious Channel)",
                        skill_id=self.skill_id,
                        skill_icon=self.skill_icon
                    )
                    
                    for vidx, v in enumerate(channel_videos):
                        if "patreon" in v.get('title', '').lower():  # TODO blacklist.voc
                            continue
                        
                        instance = self.settings["invidious_instance"]
                        video_url = f"{instance}/watch?v={v.get('videoId')}"
                        
                        pl.append(MediaEntry(
                            uri=video_url,
                            match_confidence=self.calc_score(phrase, v, idx=vidx),
                            playback=PlaybackType.VIDEO,
                            media_type=MediaType.VIDEO,
                            length=v.get('lengthSeconds', 0) * 1000,
                            image=v.get('videoThumbnails', [{}])[0].get('url', ''),
                            title=v.get('title', ''),
                            skill_id=self.skill_id,
                            skill_icon=self.skill_icon
                        ))
                        if vidx >= max_vids:
                            break

                    yield pl


if __name__ == "__main__":
    from ovos_utils.messagebus import FakeBus

    s = SimpleInvidiousSkill(bus=FakeBus(), skill_id="t.fake")

    for r in s.search_invidious("zz top", MediaType.MUSIC):
        print(r)
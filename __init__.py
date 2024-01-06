import random
from os.path import join, dirname

import requests
from json_database import JsonStorageXDG

from ovos_utils.ocp import MediaType, PlaybackType
from ovos_workshop.decorators.ocp import ocp_search, ocp_featured_media
from ovos_workshop.skills.common_play import OVOSCommonPlaybackSkill


class SovietWaveSkill(OVOSCommonPlaybackSkill):

    def __init__(self, *args, **kwargs):
        self.skill_icon = join(dirname(__file__), "ui", "sovietwave_icon.png")
        self.default_bg = join(dirname(__file__), "ui", "sovietwave_logo.png")
        self.supported_media = [MediaType.RADIO, MediaType.MUSIC]
        self.archive = JsonStorageXDG("SovietWave", subfolder="OCP")
        super().__init__(*args, **kwargs)

    def initialize(self):
        self._sync_db()
        self.load_ocp_keywords()

    def load_ocp_keywords(self):
        albums = []
        artists = ["NewSovietWave"]
        playlist = ["Sovietwave Mix",
                    "Sovietwave radio",
                    "synthwave radio"]
        genre = ["sovietwave",
                 "sovietwave mix",
                 "synthwave",
                 "synthwave mix",
                 "chillwave",
                 "retrowave",
                 "ussr",
                 "mixtape",
                 "russian synthwave",
                 "newsovietwave",
                 "dreamwave"]

        for url, data in self.archive.items():
            t = data["title"].split("(")[0]
            title = t.split("-")[0].strip()
            albums.append(title)

        self.register_ocp_keyword(MediaType.MUSIC,
                                  "artist_name", artists)
        self.register_ocp_keyword(MediaType.MUSIC,
                                  "album_name", albums)
        self.register_ocp_keyword(MediaType.MUSIC,
                                  "music_genre", genre)
        self.register_ocp_keyword(MediaType.MUSIC,
                                  "playlist_name", playlist)
        self.register_ocp_keyword(MediaType.MUSIC,
                                  "music_streaming_provider",
                                  ["SovietWave", "Soviet Wave"])

    def _sync_db(self):
        bootstrap = f"https://github.com/JarbasSkills/skill-sovietwave/raw/dev/bootstrap.json"
        data = requests.get(bootstrap).json()
        self.archive.merge(data)
        self.schedule_event(self._sync_db, random.randint(3600, 24 * 3600))

    @ocp_search()
    def ocp_sovietwave_radio(self, phrase, media_type):
        base_score = 15 if media_type == MediaType.MUSIC else 0
        entities = self.ocp_voc_match(phrase)
        score = len(entities) * 30 + base_score
        if len(entities):
            return self.featured_media(min(score, 100))

    @ocp_featured_media()
    def featured_media(self, score=100):
        return [
            {
                "match_confidence": score,
                "media_type": MediaType.MUSIC,
                "uri": "youtube//" + entry["url"],
                "playback": PlaybackType.AUDIO,
                "image": entry["thumbnail"],
                "length": entry.get("duration", 0) * 1000,
                "bg_image": self.default_bg,
                "skill_icon": self.skill_icon,
                "title": entry["title"]
            } for entry in self.archive.values()
        ]


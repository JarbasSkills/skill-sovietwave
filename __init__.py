from os.path import join, dirname, basename

from mycroft.skills.core import intent_file_handler
from ovos_plugin_common_play.ocp import MediaType, PlaybackType
from ovos_workshop.skills.common_play import ocp_search
from ovos_workshop.skills.video_collection import VideoCollectionSkill
from pyvod import Collection


class SovietWaveSkill(VideoCollectionSkill):

    def __init__(self):
        super().__init__("SovietWave")
        self.message_namespace = basename(dirname(__file__)) + ".jarbasskills"
        self.skill_icon = join(dirname(__file__), "ui", "sovietwave_icon.png")
        self.default_bg = join(dirname(__file__), "ui", "sovietwave_logo.png")
        self.supported_media = [MediaType.GENERIC,
                                MediaType.VIDEO,
                                MediaType.RADIO,
                                MediaType.MUSIC]
        self.settings["max_duration"] = -1
        path = join(dirname(__file__), "res", "NewSovietWave.jsondb")
        # load video catalog
        self.media_collection = Collection("NewSovietWave",
                                           logo=self.skill_icon,
                                           db_path=path)

    @intent_file_handler('home.intent')
    def handle_homescreen_utterance(self, message):
        # VideoCollectionSkill method, reads self.media_collection
        self.handle_homescreen(message)

    @ocp_search()
    def ocp_sovietwave_radio(self, phrase, media_type):
        if self.voc_match(phrase, "sovietwave"):
            score = 80
            if media_type == MediaType.RADIO or \
                    self.voc_match(phrase, "radio"):
                score = 100
            pl = [
                {
                    "match_confidence": score,
                    "media_type": MediaType.MUSIC,
                    "uri": "youtube//" + entry["url"],
                    "playback": PlaybackType.AUDIO,
                    "image": entry["logo"],
                    "length": entry.get("duration", 0) * 1000,
                    "bg_image": self.default_bg,
                    "skill_icon": self.skill_icon,
                    "title": entry["title"]
                } for entry in self.videos  # VideoCollectionSkill property
            ]
            if pl:
                yield {
                    "match_confidence": score,
                    "media_type": MediaType.MUSIC,
                    "playlist": pl,
                    "playback": PlaybackType.AUDIO,
                    "skill_icon": self.skill_icon,
                    "image": self.default_bg,
                    "bg_image": self.default_bg,
                    "title": "SovietWave Radio"
                }


def create_skill():
    return SovietWaveSkill()

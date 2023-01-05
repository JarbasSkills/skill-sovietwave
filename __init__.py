from os.path import join, dirname

from ovos_plugin_common_play.ocp import MediaType, PlaybackType
from ovos_utils.log import LOG
from ovos_workshop.skills.common_play import OVOSCommonPlaybackSkill, \
    ocp_search, ocp_featured_media
from youtube_archivist import YoutubeMonitor


class SovietWaveSkill(OVOSCommonPlaybackSkill):

    def __init__(self):
        super().__init__("SovietWave")
        self.skill_icon = join(dirname(__file__), "ui", "sovietwave_icon.png")
        self.default_bg = join(dirname(__file__), "ui", "sovietwave_logo.png")
        self.supported_media = [MediaType.GENERIC,
                                MediaType.RADIO,
                                MediaType.MUSIC]
        self.archive = YoutubeMonitor(db_name="SovietWave", logger=LOG)

    def initialize(self):
        url = "https://www.youtube.com/c/NewSovietWave"
        self.archive.monitor(url)
        self.archive.setDaemon(True)
        self.archive.start()

    @ocp_search()
    def ocp_sovietwave_radio(self, phrase, media_type):
        if self.voc_match(phrase, "sovietwave"):
            return self.featured_media()

    @ocp_featured_media()
    def featured_media(self):
        return [
            {
                "match_confidence": 100,
                "media_type": MediaType.MUSIC,
                "uri": "youtube//" + entry["url"],
                "playback": PlaybackType.AUDIO,
                "image": entry["thumbnail"],
                "length": entry.get("duration", 0) * 1000,
                "bg_image": self.default_bg,
                "skill_icon": self.skill_icon,
                "title": entry["title"]
            } for entry in self.archive.sorted_entries()
        ]


def create_skill():
    return SovietWaveSkill()

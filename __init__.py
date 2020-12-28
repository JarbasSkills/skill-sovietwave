from ovos_utils.waiting_for_mycroft.common_play import CPSMatchType, CPSMatchLevel
from ovos_utils.skills.templates.media_collection import MediaCollectionSkill
from mycroft.skills.core import intent_file_handler
from mycroft.util.parse import fuzzy_match, match_one
from pyvod import Collection, Media
from os.path import join, dirname, basename
import random
from json_database import JsonStorageXDG
import datetime


class SovietWaveSkill(MediaCollectionSkill):

    def __init__(self):

        super().__init__("SovietWave")
        self.message_namespace = basename(dirname(__file__)) + ".jarbasskills"
        self.supported_media = [CPSMatchType.GENERIC,
                                CPSMatchType.VIDEO,
                                CPSMatchType.RADIO,
                                CPSMatchType.MUSIC]
        self.settings["max_duration"] = -1
        path = join(dirname(__file__), "res", "NewSovietWave.jsondb")
        logo = join(dirname(__file__), "res", "sovietwave_logo.png")
        # load video catalog
        self.media_collection = Collection("NewSovietWave", logo=logo,
                                           db_path=path)

    @property
    def live_stream(self):
        return "https://listen5.myradio24.com/sovietwave"

    def get_intro_message(self):
        self.speak_dialog("intro")

    @intent_file_handler('home.intent')
    def handle_homescreen_utterance(self, message):
        self.handle_homescreen(message)

    # common play
    def play_video(self, video_data):
        if self.gui.connected:
            super().play_video(video_data)
        else:
            self.audioservice.play(self.live_stream)

    def match_media_type(self, phrase, media_type):
        match = None
        score = 0

        if self.voc_match(phrase,
                          "video") or media_type == CPSMatchType.VIDEO:
            score += 0.05
            match = CPSMatchLevel.GENERIC

        if self.voc_match(phrase,
                          "radio") or media_type == CPSMatchType.RADIO:
            score += 0.1
            match = CPSMatchLevel.CATEGORY

        if self.voc_match(phrase,
                          "music") or media_type == CPSMatchType.MUSIC:
            score += 0.1
            match = CPSMatchLevel.CATEGORY

        if self.voc_match(phrase, "sovietwave"):
            score += 0.3
            match = CPSMatchLevel.TITLE

        return match, score

    def calc_final_score(self, phrase, base_score, match_level):
        score = base_score

        if self.voc_match(phrase, "sovietwave"):
            score = 1.0

        return score, CPSMatchLevel.EXACT


def create_skill():
    return SovietWaveSkill()

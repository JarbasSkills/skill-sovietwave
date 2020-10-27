from mycroft.skills.common_play_skill import CommonPlaySkill, \
    CPSMatchLevel, CPSTrackStatus, CPSMatchType
from mycroft.skills.core import intent_file_handler
from mycroft.util.parse import fuzzy_match, match_one
from pyvod import Collection, Media
from os.path import join, dirname
import random
from json_database import JsonStorageXDG
import datetime


def datestr2ts(datestr):
    y = int(datestr[:4])
    m = int(datestr[4:6])
    d = int(datestr[-2:])
    dt = datetime.datetime(y, m, d)
    return dt.timestamp()


class SovietWaveSkill(CommonPlaySkill):

    def __init__(self):
        super().__init__("SovietWave")
        self.supported_media = [CPSMatchType.GENERIC,
                                CPSMatchType.VIDEO,
                                CPSMatchType.RADIO,
                                CPSMatchType.MUSIC]

        path = join(dirname(__file__), "res", "NewSovietWave.jsondb")
        # load video catalog
        videos = Collection("NewSovietWave",
                            logo=join(dirname(__file__), "res",
                                      "sovietwave_logo.png"),
                            db_path=path)
        self.videos = [ch.as_json() for ch in videos.entries]
        self.sort_videos()

    @property
    def live_stream(self):
        live_audio = dict(self.videos[0])
        live_audio["url"] = "https://listen5.myradio24.com/sovietwave"
        return live_audio

    def sort_videos(self):
        # this will filter private and live videos
        videos = [v for v in self.videos
                  if v.get("upload_date") and not v.get("is_live")]
        # sort by upload date
        videos = sorted(videos,
                             key=lambda kv: datestr2ts(kv["upload_date"]),
                             reverse=True)
        # live streams before videos
        self.videos =  [v for v in self.videos if v.get("is_live")] + videos

    def initialize(self):
        self.add_event('skill-sovietwave.jarbasskills.home',
                       self.handle_homescreen)
        self.gui.register_handler("skill-sovietwave.jarbasskills.play_event",
                                  self.play_video_event)
        self.gui.register_handler(
            "skill-sovietwave.jarbasskills.clear_history",
            self.handle_clear_history)

    def get_intro_message(self):
        self.speak_dialog("intro")

    @intent_file_handler('sovietwavehome.intent')
    def handle_homescreen_utterance(self, message):
        self.handle_homescreen(message)

    # homescreen
    def handle_homescreen(self, message):
        self.gui.clear()
        self.gui["mytvtogoHomeModel"] = self.videos
        self.gui["historyModel"] = JsonStorageXDG("sovietwave-history").get(
            "model", [])
        self.gui.show_page("Homescreen.qml", override_idle=True)

    # play via GUI event
    def play_video_event(self, message):
        video_data = message.data["modelData"]
        self.play_sovietwave(video_data)

    # clear history GUI event
    def handle_clear_history(self, message):
        historyDB = JsonStorageXDG("sovietwave-history")
        historyDB["model"] = []
        historyDB.store()

    # common play
    def play_sovietwave(self, video_data):
        if self.gui.connected:

            # add to playback history

            # History
            historyDB = JsonStorageXDG("sovietwave-history")
            if "model" not in historyDB:
                historyDB["model"] = []
            historyDB["model"].append(video_data)
            historyDB.store()

            self.gui["historyModel"] = historyDB["model"]
            # play video
            video = Media.from_json(video_data)
            url = str(video.streams[0])
            self.gui.play_video(url, video.name)
        else:
            self.audioservice.play(video_data["url"])

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

    def CPS_match_query_phrase(self, phrase, media_type):
        leftover_text = phrase
        best_score = 0

        # see if media type is in query, base_score will depend if "scifi"
        # or "video" is in query
        match, base_score = self.match_media_type(phrase, media_type)

        videos = list(self.videos)

        best_video = random.choice(videos)

        # score video data
        for ch in videos:
            score = 0
            # score tags
            tags = list(set(ch.get("tags", [])))
            if tags:
                # tag match bonus
                for tag in tags:
                    tag = tag.lower().strip()
                    if tag in phrase:
                        match = CPSMatchLevel.CATEGORY
                        score += 0.1
                        leftover_text = leftover_text.replace(tag, "")

            # score description
            words = ch.get("description", "").split(" ")
            for word in words:
                if len(word) > 4 and word in leftover_text:
                    score += 0.05

            if score > best_score:
                best_video = ch
                best_score = score

        # match video name
        for ch in videos:
            title = ch["title"]

            score = fuzzy_match(leftover_text, title)
            if score >= best_score:
                # TODO handle ties
                match = CPSMatchLevel.TITLE
                best_video = ch
                best_score = score
                leftover_text = title

        if not best_video:
            self.log.debug("No SovietWave matches")
            return None

        if self.voc_match(phrase, "radio") or media_type == CPSMatchType.RADIO:
            best_video = self.videos[0]
        elif best_score < 0.6:
            self.log.debug("Low score, randomizing results")
            best_video = random.choice(videos)

        score = base_score + best_score

        if self.voc_match(phrase, "sovietwave"):
            score += 0.15

        if not self.gui.connected:
            best_video = self.live_stream

        if score >= 0.85:
            match = CPSMatchLevel.EXACT
        elif score >= 0.7:
            match = CPSMatchLevel.MULTI_KEY
        elif score >= 0.5:
            match = CPSMatchLevel.TITLE

        self.log.debug("Best SovietWave video: " + best_video["title"])

        if match is not None:
            return (leftover_text, match, best_video)
        return None

    def CPS_start(self, phrase, data):
        self.play_sovietwave(data)


def create_skill():
    return SovietWaveSkill()

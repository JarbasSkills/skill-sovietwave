from youtube_archivist import YoutubeMonitor
import shutil
import json
from os.path import dirname, isfile

url = "https://www.youtube.com/c/NewSovietWave"

archive = YoutubeMonitor("SovietWave")

# load previous cache
cache_file = f"{dirname(dirname(__file__))}/bootstrap.json"
if isfile(cache_file):
    try:
        with open(cache_file) as f:
            data = json.load(f)
            archive.db.update(data)
            archive.db.store()
    except:
        pass  # corrupted for some reason

    shutil.rmtree(cache_file, ignore_errors=True)

# parse new vids
archive.parse_videos(url)

# save bootstrap cache
shutil.copy(archive.db.path, cache_file)

print(archive.sorted_entries()[0])
"""Run MatchAnalysis_PlayStyle_2025.py with its live WhoScored scraping block (`ws = sd.WhoScored(` through
`df_schedule = ws.read_schedule()`) replaced by offline equivalents: soccerdata's OptaLoader over the local event
cache and df_schedule.xlsx. The live fixtures request currently fails (JSON wrapped in <html>)."""
import os
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
SRC = REPO / "MatchAnalysis_PlayStyle_2025.py"
START = "ws = sd.WhoScored("
END = "df_schedule = ws.read_schedule()\n"
OFFLINE = (
    "from socceraction.data.opta import OptaLoader as _OL\n"
    "loader = _OL(root=str(Path.home() / 'soccerdata' / 'data' / 'WhoScored'), parser='whoscored',\n"
    "             feeds={'whoscored': str(Path('events/{competition_id}_{season_id}/{game_id}.json'))})\n"
    "df_schedule = pd.read_excel('df_schedule.xlsx')\n"
)

text = SRC.read_text(encoding="utf-8")
assert text.count(START) == 1 and text.count(END) == 1, "scraping block markers not found exactly once"
i, j = text.index(START), text.index(END) + len(END)
code = "from pathlib import Path\n" + text[:i] + OFFLINE + text[j:]
os.chdir(REPO)
sys.path.insert(0, str(REPO))
sys.argv = [str(SRC)]
exec(compile(code, str(SRC), "exec"), {"__name__": "__main__", "__file__": str(SRC)})

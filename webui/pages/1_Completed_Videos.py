import glob
import os
import sys
from datetime import datetime

import streamlit as st

# Allow importing project modules when this page is run standalone by Streamlit.
root_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
if root_dir not in sys.path:
    sys.path.append(root_dir)

from app.utils import utils  # noqa: E402

st.set_page_config(page_title="Completed Videos", page_icon="🎬", layout="wide")
st.title("🎬 Completed Videos")
st.caption("All videos that finished rendering, newest first. Scanned from disk so the "
           "list survives restarts.")

PER_ROW = 3
# Cap how many players we embed at once — each st.video loads the file, so a huge
# library would otherwise be slow/heavy. Older videos stay on disk regardless.
MAX_SHOWN = 30


def _list_final_videos():
    tasks_root = utils.task_dir()
    # Both the standard and math_explainer flows write final-<n>.mp4 into the task dir.
    pattern = os.path.join(tasks_root, "*", "final-*.mp4")
    files = [
        f for f in glob.glob(pattern)
        if os.path.isfile(f) and os.path.getsize(f) > 0
    ]
    files.sort(key=os.path.getmtime, reverse=True)
    return tasks_root, files


tasks_root, files = _list_final_videos()

top = st.columns([4, 1])
top[0].markdown(f"**{len(files)}** completed video(s) in `{tasks_root}`")
if top[1].button("🔄 Refresh", use_container_width=True):
    st.rerun()

if not files:
    st.info("No completed videos yet. Generate one from the main page.")
    st.stop()

shown = files[:MAX_SHOWN]
if len(files) > MAX_SHOWN:
    st.warning(f"Showing the {MAX_SHOWN} most recent of {len(files)} videos.")

for i in range(0, len(shown), PER_ROW):
    cols = st.columns(PER_ROW)
    for col, path in zip(cols, shown[i:i + PER_ROW]):
        with col:
            task_id = os.path.basename(os.path.dirname(path))
            name = os.path.basename(path)
            size_mb = os.path.getsize(path) / (1024 * 1024)
            mtime = datetime.fromtimestamp(os.path.getmtime(path)).strftime(
                "%Y-%m-%d %H:%M"
            )
            st.video(path)
            st.caption(f"**{name}** · {size_mb:.1f} MB · {mtime}")
            st.caption(f"Task: `{task_id}`")
            with open(path, "rb") as fh:
                st.download_button(
                    "⬇ Download",
                    data=fh,
                    file_name=f"{task_id}_{name}",
                    mime="video/mp4",
                    key=path,
                    use_container_width=True,
                )

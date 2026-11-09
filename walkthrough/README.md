# Code walkthrough

A line-by-line reading guide for the MATLAB code in `代码_matlab/` (which lives
with the study data, outside this repository).

- `index.html` — the generated page: a pipeline map on top, one section per file
  below, each section showing the source with line numbers and an explanation of
  what every block does and why it is written that way. Aimed at a reader who
  knows R but has never written MATLAB.
- Rebuild: `python3 tools/build_walkthrough.py` (reads `../tools/walkthrough_content.py`
  for the text, and `../../代码_matlab/` for the source; set `WALK_CODE` to point
  somewhere else).

The generated page is committed so it can be read without running anything.

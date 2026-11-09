# YMTC: `.trk` → CSV, and the event-marker table

Two layers that turn the MRC eye-tracker logs of the YMTC task into something you can
join with pupil data:

1. **`trk2csv`** — one `.trk` text log → one CSV per participant, one row per sample.
   Anything unexpected is *recorded*, never repaired.
2. **`ymtcEventTable`** — the software events in the trk plus the task's `TrialOrder` files
   → a table with one row per marker, in the order the task presents them:
   `Onset<cond> → PredictableTime…/UnpredictableTime… → Outcome<cond> → WhiteNoise → Rating`.

Requires MATLAB R2019b or newer. **No toolboxes** are needed for anything in this folder.

## Code map and reading order

Two layers, and two entry points per layer:

```
trk2csv.m                    entry: one .trk
  +- private/readTrk.m       parse the text into header / samples / events
  +- private/labelSamples.m  attach events to samples, carry run / trial / phase forward
  +- private/checkTrk.m      compare with what the task should have produced (record only)
trk2csv_batch.m              loop over a folder, collect qc summary and issues
exportEvents.m                entry: the event timeline, one row per SoftwareEvent
  +- private/readTrk.m       same parser, but the event times are used as they are

ymtcEventTable.m             entry: one subject's marker table
  +- reads 03_events/<sub>_events.csv   (written by exportEvents.m)
  +- readOrder() (subfunction at the end of the file) reads TrialOrder-HK/*.xlsx
  +- picks the trial order by matching countdown lengths, then writes the table in marker order
ymtcEventTableBatch.m        loop over subjects, plus a summary and a combined table
ymtcRunCheck.m               standalone check: 21 trials per run, counted from BurnInStart

ymtcTimingCheck.m            reads the marker table, reports diff_s per subject and marker
ymtcTrialWide.m              reads the marker table, writes one row per trial
```

Suggested reading order if you want the fast path:

1. `ymtcEventTable.m` - the one people ask about: how markers line up, where
   the condition comes from, what `diff_s` is, why `run = ceil(trial/21)` holds.
2. Follow the call chain `trk2csv.m` -> `private/readTrk.m` ->
   `private/labelSamples.m` -> `private/checkTrk.m`. After that you know how one
   csv row is produced.
3. `exportEvents.m` - twenty lines of real work: why the event table is not just the
   `event` column of the per-sample csv (that one is snapped to the next sample).
4. `ymtcEventTableBatch.m` and `ymtcRunCheck.m` are wrappers; skim the structure.
5. `ymtcTimingCheck.m` and `ymtcTrialWide.m` consume the table the wrappers
   produce; both are read-only until the last line, so they are safe to try.
6. The pupil-metric layer (not in this folder) lives in `code/dataModels` of this repository.

Every `.m` opens with a three-line purpose header (EN / KO / ZH) - scan those three lines
first, then decide whether the body is worth reading.

## Files

```
trk2csv.m              one .trk file  -> one csv (next to the .trk, or -OutFolder)
trk2csv_batch.m        a folder of .trk -> <folder>/csv, plus qc summary and issues tables
exportEvents.m         a .trk or a folder -> 03_事件/<sub>_events.csv (one row per event)
private/               reader, event attachment, checks (not called directly)
tests/                 simulated .trk files, runtests('tests')

ymtcEventTable.m       one subject -> 05_markers/05_<sub>_markers.csv
ymtcEventTableBatch.m  every subject in one go, plus a summary and a combined table
ymtcRunCheck.m         is every run really 21 trials? (uses BurnInStart, not START)

ymtcTimingCheck.m      per subject and marker: n / mean / SD / min / max of diff_s
ymtcTrialWide.m        long table -> one row per trial, one column per marker
ymtcConfig.m           where the folders are (no path is hard-coded)
checkDocs.m            expected columns (kept in the .m) vs the real table headers
```

## Use

Convert one file:

```matlab
[T, report] = trk2csv('sub001_YMTC_0001.trk');
```

Convert a folder (writes `csv/` inside it, plus `02_all_qc_summary.csv` and
`02_all_issues.csv`):

```matlab
results = trk2csv_batch('/path/to/raw_trk');
```

Build the event timeline `ymtcEventTable` reads (one row per event, exact event time):

```matlab
E = exportEvents('01_原始trk');                     % -> 03_事件/<sub>_events.csv
E = exportEvents('01_原始trk', 'Subjects', ["sub119" "sub149"]);
```

Build the marker table for one subject:

```matlab
T = ymtcEventTable('sub001');                       % picks the trial order automatically
T = ymtcEventTable('sub001', 'Order', 4);           % force an order
T = ymtcEventTable('sub001', 'NoiseParts', false);  % 4-5 rows per trial, no WhiteNoise parts
```

All subjects, then the cheap checks:

```matlab
S = ymtcEventTableBatch;
S = ymtcEventTableBatch('NoiseParts', false);       % 5-step version, *_5step.csv
R = ymtcRunCheck;
```

Two derived tables, both read the marker table and write one file each:

```matlab
T = ymtcTimingCheck;    % -> 05_all_timing_check.csv: diff_s per subject and marker
W = ymtcTrialWide;      % -> 05_all_trials_wide.csv: one row per trial
```

`ymtcTimingCheck` reports `diff_s = measured - designed` for the five markers, so a
systematic offset (for example a cue that runs short) shows up as a consistent sign;
`ymtcTrialWide` turns the long table into one row per trial with `onset_s`,
`countdown_s`, `outcome_s`, `whitenoise_s`, `rating_s` and `has_rating`.

## Paths: nothing absolute lives in this repository

`trk2csv` is standalone and only touches the file or folder you hand it. The `ymtc*`
functions ask `ymtcConfig.m` where the project folders are; its defaults are resolved
relative to that file, so a clone runs as-is when the layout below is present.

If your data live somewhere else, copy `ymtc_config.template.m` to `ymtc_config.m`,
edit the fields, and `ymtcConfig` applies it on top of the defaults. `ymtc_config.m`
is git-ignored, so machine paths never enter the repository.

| field | default | holds |
|---|---|---|
| `eventDir` | `03_events/` | `<sub>_events.csv`, `participant,time_ms,event` (one row per event), written by `exportEvents` |
| `orderDir` | `TrialOrder-HK/` | `TrialOrder<order>Run<run>.xlsx`, names / onsets / durations |
| `outDir` | `05_markers/` | output folder, created if missing |
| `qcDir` | `07_checks/` | `ymtcRunCheck` output |

```matlab
C = ymtcConfig()                       % see what is being used
edit ymtc_config.template.m            % then save it as ymtc_config.m
```

## Conventions worth knowing

- **No repair.** A missing marker gets an empty time, not an interpolated one. Run numbers
  in the trk CSV are counted from `START` only, so a file missing its first `START` gets
  `run 0` for the first run; that is reported, not fixed.
- **Event attachment.** Each event is attached to the first sample at or after its
  timestamp, so times carry up to one sample interval (~17 ms at 60 Hz).
- **Condition names are not in the trk.** They come from the `TrialOrder` workbooks; the
  order is chosen by matching each trial's countdown length against the five order files.
  The match margin is printed so a weak match is visible.
- **Marker ↔ step mapping:** `CueStart` = Onset (1 s cue), `CueFinish` = countdown start,
  `StimuliStart` = Outcome, `WhitenoiseStart1` = WhiteNoise (parts 2-4 are further marks of
  the same noise), `RatingStart` = Rating (only on some trials).

## Output columns (`05_<sub>_markers.csv`)

| column | meaning |
|---|---|
| `ymtc_marker`, `trk_event` | the task's marker name, and the trk event it was matched to |
| `time_ms`, `t_from_onset_s` | raw timestamp, and seconds from that trial's Onset |
| `expected_from_onset_s`, `diff_s`, `expected_duration_s` | design values and `measured - designed` |
| `step` | 1 Onset, 2 countdown start, 3 Outcome, 4 WhiteNoise, 5 Rating |
| `condition` | `PTCT` / `PTCS` / `PTUO` / `UTCT` / `UTCS` / `UTUO`, read off `Onset<cond>` |
| `timing`, `certainty`, `outcome` | `P`/`U`, `C`/`U`, and `T`/`S`/`O` (`O` = only revealed at the Outcome) |

`ymtcEventTableBatch` also writes `05_all_markers_summary.csv` (one row per subject: ok /
skipped_no_file / skipped_no_events / error) and a combined table. `ymtcRunCheck` writes
`07_all_run_check.csv` with the trials-per-run string and a `runAssignmentOK` flag, which is what
guards the `run = ceil(trial / 21)` assumption inside `ymtcEventTable`.

## Tests

```matlab
cd('code/ymtc'); runtests('tests')
```

The suite builds synthetic `.trk` files: normal logs, irregular spacing, missing `START`,
no events at all, bad lines, a wrong cue duration, the overwrite switch, batch handling
of an unreadable file, and `exportEvents` (exact event times, header-only output for a
log without events, the overwrite switch).

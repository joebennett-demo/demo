# Campus ticket reporter

A small Python utility for a university IT team's weekly service review. All 80 tickets describe a fictional North River University. They are synthetic teaching examples, not JHU operational data.

## Start here

`main` contains the original text-reporting utility and ten baseline tests. The workshop task is to add useful JSON output while preserving the existing behavior.

| File | Purpose |
| --- | --- |
| `ticket_report.py` | Starter reporting utility |
| `test_ticket_report.py` | Baseline tests |
| `campus_tickets.csv` | 80 fictional tickets |
| `data_dictionary.md` | Field meanings and metric definitions |
| `developer_brief.md` | Requested improvement and acceptance criteria |

## Run the starter

Python 3 is required. No third-party packages or network access are needed by the utility.

```sh
python3 -m unittest -v
python3 ticket_report.py campus_tickets.csv
python3 ticket_report.py campus_tickets.csv --service VPN
```

The starter intentionally has no `--format json` option. Read the developer brief before making changes.

## Keep demonstrations repeatable

Start every demonstration from `main`. Use `jhu-ticket-reporter-pre-run` for rehearsal and `jhu-ticket-reporter-live` for the live session. Keep improvements on the selected working branch and do not merge them into `main`.

The reporting period is October 26 to November 1, 2026. The demonstration is November 6, 2026. See the data dictionary for the snapshot and calculation rules.

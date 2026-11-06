# Campus ticket reporter

Python 3 standard-library utility for 80 fictional North River University tickets. This is teaching data, not JHU operational data. The reporting snapshot is November 1, 2026; see `data_dictionary.md` for the metric definitions and `developer_brief.md` for acceptance criteria.

## Run

From the repository root:

```sh
python3 -m unittest -v
python3 ticket_report.py campus_tickets.csv
python3 ticket_report.py campus_tickets.csv --format json
python3 ticket_report.py campus_tickets.csv --service VPN
python3 ticket_report.py campus_tickets.csv --service VPN --format json
```

`--format text` is the default. `--service` accepts Accounts, Classroom AV, LMS, Network, Research Computing, or VPN. JSON contains `overall` and `per_service` metrics; each has `tickets`, `open`, `aged`, `sla_met`, `sla_pct` (percentage), and `median_hours`. Unavailable rates and medians are `null` in JSON and `N/A` in text. A header-only file has zero totals, null rate and median, and an empty per-service object. Invalid input exits nonzero without printing a partial report.

## Validation results

Executed locally after the final code change:

| Command | Exit | Observed result |
| --- | ---: | --- |
| `python3 -m unittest -v` | 0 | 17 tests passed |
| `python3 ticket_report.py campus_tickets.csv` | 0 | All: 80 tickets, 20 Open, 8 aged, 87.5% response SLA, 5 h median |
| `python3 ticket_report.py campus_tickets.csv --format json` | 0 | Valid JSON; overall 80/20/8, 70 SLA successes, 87.5%, 5 h; six services |
| `python3 ticket_report.py campus_tickets.csv --service VPN` | 0 | All and VPN: 24 tickets, 6 Open, 4 aged, 87.5%, 5.5 h |
| `python3 ticket_report.py campus_tickets.csv --service VPN --format json` | 0 | Valid JSON; overall and VPN agree at 24/6/4, 21 SLA successes, 87.5%, 5.5 h |

The tests cover the seven-day Open boundary, header-only and empty files, a filtered selection with no Closed tickets, invalid fields and duplicate IDs, service filtering, JSON parsing, and rejection of a bad later row (even outside the filter) with no partial stdout. The sample CSV remains unchanged. No third-party packages or network calls are used by the utility.

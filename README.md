# Campus ticket reporter

Python 3, standard library only. This is a fictional North River University teaching example, not JHU operational data. The 80-ticket sample covers October 26–November 1, 2026; the snapshot is November 1 at end of day. See [data_dictionary.md](data_dictionary.md) for definitions and [developer_brief.md](developer_brief.md) for acceptance criteria.

```sh
python3 -m unittest -v
python3 ticket_report.py campus_tickets.csv
python3 ticket_report.py campus_tickets.csv --format json
python3 ticket_report.py campus_tickets.csv --service VPN
python3 ticket_report.py campus_tickets.csv --service VPN --format json
```

The default `--format text` retains the original table. JSON contains `overall` metrics and a `services` object keyed by observed service name. `--service` restricts both to that service; a valid service with no tickets yields zero counts, `null` for unavailable rate and median, and an empty `services` object. Each metrics object has `tickets`, `open`, `aged`, `sla_met`, `sla_pct` (numeric percent), and `median_hours`. JSON uses `null` for unavailable rate or median; text uses `N/A`. The first-response rate uses all selected tickets as its denominator, and the median uses Closed tickets only. Invalid input exits nonzero with a row-specific error and no report; the CSV is read only.

## Verified results

After the final changes, all five commands above exited 0. `python3 -m unittest -v` ran **17 tests, OK**. Checks cover the seven-day boundary (Open versus Closed), empty and header-only files, missing or duplicate IDs with row numbers, invalid fields and late rows, filtering and validation outside the filter, unmatched services, no-Closed selections, JSON structure, and no partial CLI output. The four report commands returned:

| Selection | Format | Tickets | Open | Aged open | SLA met / tickets | First-response SLA | Closed median (h) |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Full data | text | 80 | 20 | 8 | 70 / 80 | 87.5% | 5 |
| Full data | JSON | 80 | 20 | 8 | 70 / 80 | 87.5 | 5.0 |
| VPN | text | 24 | 6 | 4 | 21 / 24 | 87.5% | 5.5 |
| VPN | JSON | 24 | 6 | 4 | 21 / 24 | 87.5 | 5.5 |

The full JSON breakdown has six services; the VPN JSON breakdown has only VPN. No third-party packages, network calls, or writes to the sample data are needed to run the utility.

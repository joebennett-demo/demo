# Ticket reporter: add machine-readable output

Fictional North River University workshop project. Version 1.0 source. The starter files are on the main branch of joebennett-demo/demo in GitHub so they can be retrieved live. They are not production JHU code or data.

The existing Python 3 utility produces overall and per-service console metrics and supports --service. Improve it by adding --format json, preserving the default text behavior. In JSON include the overall metrics and the per-service breakdown, and use null for unavailable rates or medians. Keep the standard-library-only implementation and clear nonzero exits for invalid input.

Read the CSV without changing it. Validate required columns, unique nonempty ticket IDs, known service names, Open/Closed statuses, true/false first-response flags, nonnegative numeric fields and status/resolution consistency. Compute all results before output so an invalid later row produces no partial report. The utility itself makes no network calls.

Metrics: total tickets; Open backlog; aged Open backlog with age_days >= 7; first-response SLA successes divided by all selected tickets; median resolution hours among Closed tickets only. Support empty/header-only and no-Closed selections explicitly. The reporting snapshot is October 26-November 1, 2026.

Retrieve this source project through the connected GitHub tools. Start from main and save improvements on the branch named in the prompt. Keep main as the unchanged starter for future demonstrations. Retain runnable internal filenames. Execute the full tests and both full-data and VPN CLI examples after the final code changes. Commit the improvements to the named working branch. Do not merge into main or deploy the utility.

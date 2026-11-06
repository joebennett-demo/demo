# North River University IT: fictional practice data

This file and all associated records are synthetic teaching examples. They are not JHU operational data. Reporting period: October 26-November 1, 2026. Snapshot: November 1 at end of day. Each row is one ticket; IDs are unique.

| Field | Meaning |
|---|---|
| ticket_id | Fictional ticket identifier |
| service | One of VPN, LMS, Classroom AV, Accounts, Network, Research Computing |
| category | Broad support category |
| priority | P2 or P3 in this sample; not a real institution's priority policy |
| status | Open or Closed at the snapshot |
| age_days | Whole days since creation at the snapshot |
| response_met_sla | true/false: whether the first response met its target; populated for every ticket |
| resolution_hours | Hours to resolution for closed tickets; blank for open tickets |

Definitions: backlog = Open tickets; aged backlog = Open tickets with age_days >= 7. First-response SLA rate = true rows / all rows in the selected set. Median resolution = median of resolution_hours for Closed tickets only. A zero denominator means N/A, not 0%. Do not call this a resolution SLA measure or a previous-week trend. There is one week of data, no comparison period, and no causal evidence.

Useful deliverable: a concise weekly service review for campus IT leaders, with top demand, backlog, first-response performance, and proposed actions. Actions are recommendations, not assigned work or approved changes.

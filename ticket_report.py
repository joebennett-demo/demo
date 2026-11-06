"""Fictional campus IT teaching example."""
import argparse
import csv
import json
import statistics
import sys
from pathlib import Path

REQUIRED={'ticket_id','service','category','priority','status','age_days','response_met_sla','resolution_hours'}
SERVICES={'VPN','LMS','Classroom AV','Accounts','Network','Research Computing'}

def read_tickets(path):
    with Path(path).open(newline='',encoding='utf-8-sig') as f:
        reader=csv.DictReader(f)
        if not reader.fieldnames or not REQUIRED.issubset(reader.fieldnames):
            raise ValueError('Missing header or required columns: '+', '.join(sorted(REQUIRED-set(reader.fieldnames or []))))
        rows=[]; seen=set()
        for line,r in enumerate(reader,2):
            def fail(message):
                raise ValueError(f'Row {line}: {message}')
            if None in r or any(v is None for v in r.values()): fail('wrong number of fields')
            r={k:v.strip() for k,v in r.items()}
            if not r['ticket_id'] or r['ticket_id'] in seen: fail('missing or duplicate ticket_id')
            seen.add(r['ticket_id'])
            if r['service'] not in SERVICES: fail('unknown service')
            if r['status'] not in {'Open','Closed'}: fail('status must be Open or Closed')
            if r['response_met_sla'] not in {'true','false'}: fail('response_met_sla must be true or false')
            try: age=int(r['age_days'])
            except ValueError: fail('age_days must be a nonnegative integer')
            if age<0: fail('age_days must be a nonnegative integer')
            r['age_days']=age
            if r['status']=='Closed':
                try: hours=float(r['resolution_hours'])
                except ValueError: fail('closed ticket needs numeric resolution_hours')
                if not 0<=hours<float('inf'): fail('resolution_hours must be finite and nonnegative')
                r['resolution_hours']=hours
            elif r['resolution_hours']!='': fail('open ticket must leave resolution_hours blank')
            rows.append(r)
        return rows

def summarize(rows):
    closed=[r['resolution_hours'] for r in rows if r['status']=='Closed']
    return {'tickets':len(rows),'open':sum(r['status']=='Open' for r in rows),
            'aged':sum(r['status']=='Open' and r['age_days']>=7 for r in rows),
            'sla_met':sum(r['response_met_sla']=='true' for r in rows),
            'sla_pct':100*sum(r['response_met_sla']=='true' for r in rows)/len(rows) if rows else None,
            'median_hours':statistics.median(closed) if closed else None}

def report(rows):
    lines=['Fictional campus IT data','| Service | Tickets | Open | Aged open | Response SLA | Median resolution (h) |',
           '|---|---:|---:|---:|---:|---:|']
    for name,a in [('All',rows)]+[(s,[r for r in rows if r['service']==s]) for s in sorted({r['service'] for r in rows})]:
        v=summarize(a); rate='N/A' if v['sla_pct'] is None else f"{v['sla_pct']:.1f}%"
        median='N/A' if v['median_hours'] is None else f"{v['median_hours']:g}"
        lines.append(f"| {name} | {v['tickets']} | {v['open']} | {v['aged']} | {rate} | {median} |")
    return '\n'.join(lines)

def json_report(rows):
    """Return the selected set's metrics and its observed service breakdown."""
    result = {
        'overall': summarize(rows),
        'services': {
            service: summarize([r for r in rows if r['service'] == service])
            for service in sorted({r['service'] for r in rows})
        },
    }
    return json.dumps(result, indent=2, allow_nan=False)

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('csv_path')
    p.add_argument('--service',choices=sorted(SERVICES))
    p.add_argument('--format',choices=('text','json'),default='text')
    a=p.parse_args()
    try:
        rows=read_tickets(a.csv_path)
        if a.service: rows=[r for r in rows if r['service']==a.service]
        result=json_report(rows) if a.format=='json' else report(rows)
    except (OSError,ValueError) as e:
        print(str(e),file=sys.stderr);return 2
    print(result);return 0
if __name__=='__main__': sys.exit(main())

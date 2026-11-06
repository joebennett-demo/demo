import csv, json, pathlib, subprocess, tempfile, unittest, sys
sys.path.insert(0,str(pathlib.Path(__file__).parent))
from ticket_report import read_tickets,summarize,report

BASE=dict(ticket_id='T1',service='VPN',category='Access',priority='P2',status='Open',age_days='7',response_met_sla='true',resolution_hours='')
class TicketReportTests(unittest.TestCase):
 def load(self,rows,fields=None):
  with tempfile.TemporaryDirectory() as d:
   p=pathlib.Path(d)/'data.csv'
   with p.open('w',newline='') as f:
    w=csv.DictWriter(f,fieldnames=fields or list(BASE),extrasaction='ignore');w.writeheader();w.writerows(rows)
   return read_tickets(p)
 def test_sample_totals(self):
  rows=read_tickets(pathlib.Path(__file__).with_name('campus_tickets.csv'));s=summarize(rows)
  self.assertEqual((s['tickets'],s['open'],s['aged'],s['sla_met'],s['median_hours']),(80,20,8,70,5))
 def test_filter(self):
  rows=read_tickets(pathlib.Path(__file__).with_name('campus_tickets.csv'));s=summarize([r for r in rows if r['service']=='VPN']);self.assertEqual((s['tickets'],s['open'],s['aged']),(24,6,4))
 def test_header_only(self): self.assertEqual(summarize(self.load([]))['tickets'],0);self.assertIn('N/A',report([]))
 def test_missing_header(self):
  with tempfile.TemporaryDirectory() as d:
   p=pathlib.Path(d)/'empty.csv';p.write_text('')
   with self.assertRaises(ValueError):read_tickets(p)
 def test_missing_column(self):
  with self.assertRaises(ValueError):self.load([BASE],[k for k in BASE if k!='age_days'])
 def test_bad_rows(self):
  for changes in [{'status':'Waiting'},{'response_met_sla':'yes'},{'age_days':'-1'},{'age_days':'x'},{'service':'Unknown'},{'status':'Closed'},{'resolution_hours':'5'}]:
   with self.subTest(changes=changes),self.assertRaisesRegex(ValueError,'Row 2'):self.load([dict(BASE,**changes)])
 def test_bad_resolution(self):
  for v in ['nan','inf','-1','x']:
   with self.subTest(v=v),self.assertRaises(ValueError):self.load([dict(BASE,status='Closed',resolution_hours=v)])
 def test_duplicate(self):
  with self.assertRaises(ValueError):self.load([BASE,BASE])
 def test_no_closed(self):self.assertIsNone(summarize(self.load([BASE]))['median_hours'])
 def test_aged_boundary(self):self.assertEqual(summarize(self.load([BASE,dict(BASE,ticket_id='T2',age_days='6')]))['aged'],1)

class JsonCliTests(unittest.TestCase):
 def run_cli(self, path, *args):
  return subprocess.run([sys.executable, str(pathlib.Path(__file__).with_name('ticket_report.py')),
                         str(path), *args], capture_output=True, text=True)

 def test_full_data_json_and_default_text(self):
  path=pathlib.Path(__file__).with_name('campus_tickets.csv')
  output=self.run_cli(path, '--format', 'json')
  self.assertEqual(output.returncode, 0, output.stderr)
  self.assertEqual(output.stderr, '')
  result=json.loads(output.stdout)
  self.assertEqual((result['overall']['tickets'], result['overall']['open'],
                    result['overall']['aged'], result['overall']['sla_met'],
                    result['overall']['sla_pct'], result['overall']['median_hours']),
                   (80,20,8,70,87.5,5))
  self.assertEqual(sum(v['tickets'] for v in result['per_service'].values()), 80)
  self.assertEqual(set(result['per_service']), {'VPN','LMS','Classroom AV','Accounts','Network','Research Computing'})
  self.assertIn('| All | 80 | 20 | 8 | 87.5% | 5 |', self.run_cli(path).stdout)
  self.assertEqual(self.run_cli(path).stdout, self.run_cli(path, '--format', 'text').stdout)

 def test_vpn_filter_in_json_and_text(self):
  path=pathlib.Path(__file__).with_name('campus_tickets.csv')
  output=self.run_cli(path, '--service', 'VPN', '--format', 'json')
  self.assertEqual(output.returncode, 0, output.stderr)
  result=json.loads(output.stdout)
  self.assertEqual(list(result['per_service']), ['VPN'])
  self.assertEqual(result['overall'], result['per_service']['VPN'])
  self.assertEqual((result['overall']['tickets'], result['overall']['open'], result['overall']['aged']), (24,6,4))
  text=self.run_cli(path, '--service', 'VPN')
  self.assertEqual(text.returncode, 0, text.stderr)
  self.assertIn('| VPN | 24 | 6 | 4 |', text.stdout)
  self.assertNotIn('| LMS |', text.stdout)

 def test_empty_and_no_closed_json(self):
  with tempfile.TemporaryDirectory() as d:
   path=pathlib.Path(d)/'data.csv'
   with path.open('w', newline='') as f:
    writer=csv.DictWriter(f, fieldnames=list(BASE));writer.writeheader()
   empty=json.loads(self.run_cli(path, '--format', 'json').stdout)
   self.assertEqual(empty['overall']['tickets'], 0)
   self.assertIsNone(empty['overall']['sla_pct'])
   self.assertIsNone(empty['overall']['median_hours'])
   self.assertEqual(empty['per_service'], {})
   with path.open('a', newline='') as f:csv.DictWriter(f, fieldnames=list(BASE)).writerow(BASE)
   no_closed=json.loads(self.run_cli(path, '--format', 'json').stdout)
   self.assertEqual(no_closed['overall']['aged'], 1)
   self.assertIsNone(no_closed['per_service']['VPN']['median_hours'])

 def test_invalid_later_row_has_no_partial_report(self):
  with tempfile.TemporaryDirectory() as d:
   path=pathlib.Path(d)/'data.csv'
   with path.open('w', newline='') as f:
    writer=csv.DictWriter(f, fieldnames=list(BASE));writer.writeheader()
    writer.writerows([BASE, dict(BASE, ticket_id='T2', response_met_sla='maybe')])
   for format_args in [(), ('--format', 'json')]:
    with self.subTest(format_args=format_args):
     result=self.run_cli(path, *format_args)
     self.assertNotEqual(result.returncode, 0)
     self.assertEqual(result.stdout, '')
     self.assertIn('Row 3:', result.stderr)
if __name__=='__main__':unittest.main()

import csv, json, pathlib, subprocess, tempfile, unittest, sys
sys.path.insert(0,str(pathlib.Path(__file__).parent))
from ticket_report import read_tickets,summarize,report,json_report

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

 def test_aged_boundary_excludes_closed_tickets(self):
  rows=self.load([dict(BASE,age_days='6'),
                  dict(BASE,ticket_id='T2',age_days='7'),
                  dict(BASE,ticket_id='T3',status='Closed',age_days='7',resolution_hours='2')])
  self.assertEqual((summarize(rows)['open'],summarize(rows)['aged']),(2,1))

 def test_missing_and_duplicate_ids_have_row_numbers(self):
  for rows,expected in [([dict(BASE,ticket_id='')],'Row 2:'),
                        ([BASE,dict(BASE,ticket_id='T1')],'Row 3:')]:
   with self.subTest(rows=rows),self.assertRaisesRegex(ValueError,expected):
    self.load(rows)

 def test_json_sample_and_filter(self):
  rows=read_tickets(pathlib.Path(__file__).with_name('campus_tickets.csv'))
  full=json.loads(json_report(rows))
  self.assertEqual(full['overall']['tickets'],80)
  self.assertEqual(full['overall']['sla_met'],70)
  self.assertEqual(full['overall']['sla_pct'],87.5)
  self.assertEqual(sum(v['tickets'] for v in full['services'].values()),80)
  vpn=json.loads(json_report([r for r in rows if r['service']=='VPN']))
  self.assertEqual(list(vpn['services']),['VPN'])
  self.assertEqual(vpn['overall'],vpn['services']['VPN'])
  self.assertEqual((vpn['overall']['tickets'],vpn['overall']['open'],vpn['overall']['aged']),(24,6,4))

 def test_json_unavailable_metrics(self):
  self.assertEqual(json.loads(json_report([])),{
   'overall':dict(tickets=0,open=0,aged=0,sla_met=0,sla_pct=None,median_hours=None),
   'services':{}})
  one=json.loads(json_report(self.load([BASE])))
  self.assertIsNone(one['overall']['median_hours'])
  self.assertEqual(one['overall']['sla_pct'],100.0)

 def test_cli_formats_and_no_partial_output(self):
  script=pathlib.Path(__file__).with_name('ticket_report.py')
  source=pathlib.Path(__file__).with_name('campus_tickets.csv')
  def run(path,*args):
   return subprocess.run([sys.executable,str(script),str(path),*args],capture_output=True,text=True)
  default=run(source)
  explicit=run(source,'--format','text')
  self.assertEqual(default.returncode,0)
  self.assertEqual(default.stdout,explicit.stdout)
  vpn=run(source,'--service','VPN','--format','json')
  self.assertEqual(vpn.returncode,0)
  self.assertEqual(json.loads(vpn.stdout)['overall']['tickets'],24)
  with tempfile.TemporaryDirectory() as d:
   path=pathlib.Path(d)/'invalid.csv'
   with path.open('w',newline='') as f:
    writer=csv.DictWriter(f,fieldnames=list(BASE))
    writer.writeheader()
    writer.writerows([BASE,dict(BASE,ticket_id='T2',status='Invalid')])
   for format_name in ('text','json'):
    with self.subTest(format=format_name):
     result=run(path,'--format',format_name,'--service','VPN')
     self.assertNotEqual(result.returncode,0)
     self.assertEqual(result.stdout,'')
     self.assertIn('Row 3:',result.stderr)

 def test_cli_empty_file_header_only_and_no_closed_selection(self):
  script=pathlib.Path(__file__).with_name('ticket_report.py')
  with tempfile.TemporaryDirectory() as d:
   path=pathlib.Path(d)/'data.csv'
   for format_name in ('text','json'):
    with self.subTest(format=format_name,case='empty file'):
     path.write_text('')
     result=subprocess.run([sys.executable,str(script),str(path),'--format',format_name],capture_output=True,text=True)
     self.assertEqual(result.returncode,2)
     self.assertEqual(result.stdout,'')
     self.assertIn('Missing header',result.stderr)
    with path.open('w',newline='') as f:
     writer=csv.DictWriter(f,fieldnames=list(BASE));writer.writeheader()
    with self.subTest(format=format_name,case='header only'):
     result=subprocess.run([sys.executable,str(script),str(path),'--format',format_name],capture_output=True,text=True)
     self.assertEqual(result.returncode,0)
     if format_name=='json':
      self.assertEqual(json.loads(result.stdout)['overall']['sla_pct'],None)
      self.assertEqual(json.loads(result.stdout)['services'],{})
     else:self.assertIn('N/A',result.stdout)
    with path.open('a',newline='') as f:
     writer=csv.DictWriter(f,fieldnames=list(BASE));writer.writerow(BASE)
    with self.subTest(format=format_name,case='no Closed'):
     result=subprocess.run([sys.executable,str(script),str(path),'--service','VPN','--format',format_name],capture_output=True,text=True)
     self.assertEqual(result.returncode,0)
     if format_name=='json':self.assertIsNone(json.loads(result.stdout)['overall']['median_hours'])
     else:self.assertIn('| VPN | 1 | 1 | 1 | 100.0% | N/A |',result.stdout)
    with self.subTest(format=format_name,case='unmatched service'):
     result=subprocess.run([sys.executable,str(script),str(path),'--service','LMS','--format',format_name],capture_output=True,text=True)
     self.assertEqual(result.returncode,0)
     if format_name=='json':
      data=json.loads(result.stdout)
      self.assertEqual(data['overall']['tickets'],0)
      self.assertIsNone(data['overall']['sla_pct'])
      self.assertEqual(data['services'],{})
     else:self.assertIn('| All | 0 | 0 | 0 | N/A | N/A |',result.stdout)

 def test_cli_validates_rows_outside_filter(self):
  script=pathlib.Path(__file__).with_name('ticket_report.py')
  with tempfile.TemporaryDirectory() as d:
   path=pathlib.Path(d)/'data.csv'
   with path.open('w',newline='') as f:
    writer=csv.DictWriter(f,fieldnames=list(BASE))
    writer.writeheader()
    writer.writerows([BASE,dict(BASE,ticket_id='T2',service='LMS',age_days='-1')])
   for format_name in ('text','json'):
    with self.subTest(format=format_name):
     result=subprocess.run([sys.executable,str(script),str(path),'--service','VPN','--format',format_name],capture_output=True,text=True)
     self.assertEqual(result.returncode,2)
     self.assertIn('Row 3:',result.stderr)
     self.assertEqual(result.stdout,'')
if __name__=='__main__':unittest.main()

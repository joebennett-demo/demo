import csv, pathlib,tempfile,unittest,sys
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
if __name__=='__main__':unittest.main()

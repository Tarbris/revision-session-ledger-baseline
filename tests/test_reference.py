"""Existing full-reference behavior; no optimized data structure or solution."""
import json
from pathlib import Path
import subprocess
import sys
import unittest
from baseline.run_reference import Reference

def config():return {'sources':['north','south'],'gap':10,'lateness':40}
def put(identifier,t,value,revision=1):return {'op':'put','source':'north','id':identifier,'revision':revision,'key':'a','time':t,'value':value}

class ExistingReferenceTests(unittest.TestCase):
    def test_empty_checkpoint(self):
        self.assertEqual(Reference(config()).step({'op':'checkpoint','id':'x'},1),{'seq':1,'checkpoint':'x','watermark':0,'retract':[],'upsert':[]})
    def test_source_minimum(self):
        engine=Reference(config())
        self.assertEqual(engine.step({'op':'watermark','source':'north','time':50},1)['watermark'],0)
        self.assertEqual(engine.step({'op':'watermark','source':'south','time':40},2)['watermark'],40)
    def test_tombstone_prevents_old_replay(self):
        engine=Reference(config())
        engine.step({'op':'delete','source':'north','id':'x','revision':5},1)
        self.assertEqual(engine.step(put('x',10,1,4),2)['status'],'stale')
        self.assertEqual(engine.step(put('x',10,1,6),3)['status'],'accepted')
    def test_bridge_delete(self):
        engine=Reference(config())
        for seq,command in enumerate([put('left',10,-5),put('bridge',20,-2),put('right',30,-9),{'op':'watermark','source':'north','time':50},{'op':'watermark','source':'south','time':50}],1):engine.step(command,seq)
        first=engine.step({'op':'checkpoint','id':'one'},6)
        self.assertEqual(first['upsert'],[['a',10,30,3,-16,-2]])
        engine.step({'op':'delete','source':'north','id':'bridge','revision':2},7)
        second=engine.step({'op':'checkpoint','id':'two'},8)
        self.assertEqual(second['retract'],first['upsert'])
        self.assertEqual(second['upsert'],[['a',10,10,1,-5,-5],['a',30,30,1,-9,-9]])
    def test_cli_shape(self):
        rows=[dict(config(),op='config'),{'op':'checkpoint','id':'last'}]
        process=subprocess.run([sys.executable,str(Path(__file__).resolve().parents[1]/'baseline/run_reference.py')],input=''.join(json.dumps(x)+'\n' for x in rows),capture_output=True,text=True,check=True)
        self.assertEqual(json.loads(process.stdout),{'seq':1,'checkpoint':'last','watermark':0,'retract':[],'upsert':[]})

if __name__=='__main__':unittest.main()

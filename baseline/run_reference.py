"""Independent standard-library baseline: sort and rescan all active records."""
import json, sys

class Reference:
    def __init__(self, config):
        self.gap=config['gap']; self.late=config['lateness']
        self.wm={s:0 for s in config['sources']}; self.records={}
        self.events=set(); self.previous=set()

    def step(self, cmd, seq):
        op=cmd['op']; w=min(self.wm.values())
        if op=='watermark':
            self.wm[cmd['source']]=cmd['time']
            return {'seq':seq,'status':'accepted','watermark':min(self.wm.values())}
        if op in ('put','delete'):
            identity=(cmd['source'],cmd['id']); old=self.records.get(identity)
            if old is not None and cmd['revision']<=old[0]: status='stale'
            elif ((old is not None and old[1] is not None and old[1][1]<w-self.late)
                  or (op=='put' and cmd['time']<w-self.late)): status='late'
            else:
                if old is not None and old[1] is not None: self.events.remove(old[1])
                row=(cmd['key'],cmd['time'],cmd['source'],cmd['id'],cmd['value']) if op=='put' else None
                if row is not None: self.events.add(row)
                self.records[identity]=(cmd['revision'],row); status='accepted'
            return {'seq':seq,'status':status,'watermark':w}
        assert op=='checkpoint'
        current=set(); key=None; start=end=count=total=maximum=0
        for k,t,s,i,v in sorted(self.events):
            if k!=key or t-end>self.gap:
                if key is not None and w>end+self.gap: current.add((key,start,end,count,total,maximum))
                key=k; start=t; end=t; count=1; total=v; maximum=v
            else: end=t; count+=1; total+=v; maximum=max(maximum,v)
        if key is not None and w>end+self.gap: current.add((key,start,end,count,total,maximum))
        result={'seq':seq,'checkpoint':cmd['id'],'watermark':w,
                'retract':[list(x) for x in sorted(self.previous-current)],
                'upsert':[list(x) for x in sorted(current-self.previous)]}
        self.previous=current
        return result

def main():
    lines=iter(sys.stdin); engine=Reference(json.loads(next(lines)))
    for seq,line in enumerate(lines,1):
        print(json.dumps(engine.step(json.loads(line),seq),ensure_ascii=False,separators=(',',':')),flush=True)
if __name__=='__main__': main()

"""Audited offline analysis. Standard library only; no source writes or external calls."""
from __future__ import annotations
import csv
import hashlib
import html
import json
import math
import random
import re
import statistics as st
from collections import Counter, defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
OUT = HERE / 'outputs'
CFG = json.loads((HERE / 'scoring_config.json').read_text(encoding='utf-8'))

def med(values):
    values = list(values)
    return st.median(values) if values else None

def quantile(values, p):
    values = sorted(values)
    if not values: return None
    x = (len(values)-1)*p
    i = int(x)
    return values[i] + (values[min(i+1,len(values)-1)]-values[i])*(x-i)

def dump(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value,ensure_ascii=False,indent=2,allow_nan=False),encoding='utf-8')

def csvout(name, rows):
    if not rows: return
    keys = list(dict.fromkeys(k for r in rows for k in r))
    with (OUT/name).open('w',encoding='utf-8-sig',newline='') as f:
        w=csv.DictWriter(f,keys); w.writeheader()
        for r in rows:
            w.writerow({k: json.dumps(v,ensure_ascii=False) if isinstance(v,(list,dict)) else v for k,v in r.items()})

def sources():
    text=(ROOT/'index.html').read_text(encoding='utf-8')
    match=re.search(r'^const DB = (.*);\s*$',text,re.M)
    if not match: raise ValueError('DB block missing')
    db=json.loads(match[1],parse_constant=lambda value:None)
    images=json.loads((ROOT/'main_images_full_analysis.json').read_text(encoding='utf-8'))
    embedded=re.search(r'^\s*const MAIN_IMAGE_DATA = (.*);\s*$',text,re.M)
    image_same=bool(embedded and json.loads(embedded[1]) == images)
    return db,images,image_same

def total_height(name):
    """Use only SKU text, prioritize total/explicit thickness, never median component layers."""
    text=name.lower()
    patterns=[r'(?:总厚(?:度)?|整垫厚(?:度)?|成品厚(?:度)?)\s*[:：约]?\s*(\d+(?:\.\d+)?)\s*(?:cm|厘米|公分)',
              r'(?:厚度|厚)\s*[:：约]?\s*(\d+(?:\.\d+)?)\s*(?:cm|厘米|公分)',
              r'(\d+(?:\.\d+)?)\s*(?:cm|厘米|公分)\s*厚',
              r'[/／|｜【（(]\s*(\d+(?:\.\d+)?)\s*(?:cm|厘米|公分)\s*[】）)/／|｜=]',
              r'(?<![\d.])(\d+(?:\.\d+)?)\s*(?:cm|厘米|公分)\s*[=＝]']
    for pat in patterns:
        m=re.search(pat,text)
        if m:
            value=float(m[1])
            if 2 <= value <= 45: return value,m[0]
    return None,''

def clean(db,images,image_same):
    rows=[]; seen=set(); counts=Counter(); exact_seen=set(); dup_exact=0
    for p in db['products']:
        for ix,s in enumerate(p['skus'],1):
            price=s.get('price'); name=s.get('name','')
            exact=(p['rank'],name,price)
            if exact in exact_seen: dup_exact+=1
            exact_seen.add(exact)
            key=(p['rank'],re.sub(r'\s+','',name).lower(),price)
            height,evidence=total_height(name)
            reason=''
            if price is None or not math.isfinite(price): reason='缺失或非有限价格'
            elif price<100: reason='低于100元待核验（不认定为虚假）'
            elif re.search(r'定金|订金|补差|差价|单床架|仅床架',name): reason='定金差价或单床架'
            elif key in seen: reason='同商品SKU名+价格重复（空白归一）'
            seen.add(key)
            bundle=bool(re.search(r'套餐|床架|软床|皮床|套床|组合|搭配',name))
            custom=bool(re.search(r'定制|特殊尺寸',name))
            row={'row_id':f"R{p['rank']:03d}-S{ix:03d}",'rank':p['rank'],'shop':p['shop'],'title':p['title'],
                 'link':p['link'],'sku_name':name,'price':price,'orig':s.get('orig'),'tag':s.get('tag',''),
                 'height':height,'height_evidence':evidence,'bundle':bundle,'custom':custom,
                 'exclude':reason,'text':(p['title']+' '+name).lower()}
            rows.append(row);counts[reason or '保留']+=1
    audit={'raw_products':len(db['products']),'raw_skus':len(rows),'raw_exact_duplicate_rows':dup_exact,
           'mutually_exclusive_cleaning_counts':dict(counts),'clean_skus':sum(not r['exclude'] for r in rows),
           'clean_products':len({r['rank'] for r in rows if not r['exclude']}),
           'height_known':sum(r['height'] is not None for r in rows if not r['exclude']),
           'bundle_flags':sum(r['bundle'] for r in rows if not r['exclude']),
           'custom_flags':sum(r['custom'] for r in rows if not r['exclude']),
           'image_records':len(images),'valid_images':sum(bool(v.get('has_image')) for v in images.values()),
           'main_image_prices':sum(v.get('price_analysis',{}).get('main_image_price') is not None for v in images.values()),
           'embedded_images_equal_json':image_same,
           'image_mismatch_examples':[{'rank':p['rank'],'shop':p['shop'],'title':p['title'],'ocr':images[str(p['rank'])]['ocr_raw']}
                                      for p in db['products'] if p['rank'] in [7,17,289,300]],
           'duplicate_item_ids':{k:v for k,v in group_ids(db).items() if len(v)>1},
           'source_hashes':{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in [ROOT/'index.html',ROOT/'main_images_full_analysis.json',ROOT/'床垫300款排名与SKU价格交互分析大屏.html']}}
    return rows,audit

def group_ids(db):
    groups=defaultdict(list)
    for p in db['products']:
        m=re.search(r'[?&]id=(\d+)',p['link'])
        groups[m[1] if m else p['link']].append(p['rank'])
    return dict(groups)

def qualifies(r,t,strict_height=False,price_shift=0,include_bundles=False):
    if r['exclude']: return False
    if (r['bundle'] or r['custom']) and not include_bundles and t['id']!='T5': return False
    if not t['price'][0]*(1+price_shift)<=r['price']<=t['price'][1]*(1+price_shift): return False
    if not all(re.search(g,r['text'],re.I) for g in t['groups']): return False
    if t['height']:
        if r['height'] is None: return not strict_height
        if not t['height'][0]<=r['height']<=t['height'][1]: return False
    return True

def summarize(rows):
    by=defaultdict(list)
    for r in rows: by[r['rank']].append(r)
    ranks=sorted(by); n=len(ranks)
    shops=Counter(v[0]['shop'] for v in by.values())
    prices=[med(r['price'] for r in v) for v in by.values()]
    discounts=[1-r['price']/r['orig'] for r in rows if r['orig'] and r['orig']>=r['price'] and r['orig']>0]
    return {'n':n,'sku_n':len(rows),'shops':len(shops),'median_rank':med(ranks),
            'top30':sum(r<=30 for r in ranks),'top50':sum(r<=50 for r in ranks),'top100':sum(r<=100 for r in ranks),
            'top50_rate':sum(r<=50 for r in ranks)/n if n else 0,
            'median_price':med(prices),'price_q25':quantile(prices,.25),'price_q75':quantile(prices,.75),
            'sku_price_median':med(r['price'] for r in rows),
            'hhi':sum((v/n)**2 for v in shops.values()) if n else 1,
            'largest_shop_share':max(shops.values())/n if n else 1,
            'largest_shop':shops.most_common(1)[0][0] if n else '',
            'height_coverage':sum(r['height'] is not None for r in rows)/len(rows) if rows else 0,
            'discount_median':med(discounts),'ranks':ranks}

def score(metrics,lenses=None,neutral_expert=False):
    """Fixed anchors are declared decision rules, not empirical probabilities."""
    result=[]
    for m in metrics:
        t=next(t for t in CFG['tracks'] if t['id']==m['id']);n=m['n']
        demand=0 if not n else 60*(301-m['median_rank'])/300+40*min(m['top50_rate']/.4,1)
        breadth=60*min(n/60,1)+40*min(m['shops']/25,1)
        entry=60*(1-m['hhi'])+40*(1-m['largest_shop_share'])
        dimensions=dict(zip(CFG['dimensions'],[demand,breadth,entry,st.mean(t['supply']),st.mean(t['proof'])]))
        if neutral_expert:
            dimensions['供应可执行性']=50
            dimensions['表达可验证性']=50
        if not n: dimensions=dict.fromkeys(CFG['dimensions'],0)
        scores={key:sum(dimensions[d]*w for d,w in zip(CFG['dimensions'],weights))/100
                for key,weights in (lenses or CFG['lenses']).items()}
        raw=.75*st.mean(scores.values())+.25*min(scores.values())
        # Analyst-defined evidence penalty, not a statistical posterior or confidence interval.
        adjusted=50+n/(n+20)*(raw-50) if n else 0
        result.append({**m,'dimension_scores':dimensions,'lens_scores':scores,'raw_score':raw,'score':adjusted})
    return sorted(result,key=lambda x:x['score'],reverse=True)

def explore(rows):
    groups={t['id']:[r for r in rows if qualifies(r,t)] for t in CFG['tracks']}
    metrics=[{'id':t['id'],'name':t['name'],**summarize(groups[t['id']])} for t in CFG['tracks']]
    ranked=score(metrics)
    sensitivity=[]
    for label,kwargs in [('必须识别整垫厚度',{'strict_height':True}),('价带下移10%',{'price_shift':-.1}),('价带上移10%',{'price_shift':.1}),('包含套餐及定制',{'include_bundles':True})]:
        rr=score([{'id':t['id'],'name':t['name'],**summarize([r for r in rows if qualifies(r,t,**kwargs)])} for t in CFG['tracks']])
        sensitivity.append({'scenario':label,'ranking':[{'id':r['id'],'n':r['n'],'score':r['score']} for r in rr]})
    for label,weights in CFG['lenses'].items():
        rr=score(metrics,{label:weights})
        sensitivity.append({'scenario':label,'ranking':[{'id':r['id'],'n':r['n'],'score':r['score']} for r in rr]})
    neutral=score(metrics,neutral_expert=True)
    sensitivity.append({'scenario':'主观两维均设50分','ranking':[{'id':r['id'],'n':r['n'],'score':r['score']} for r in neutral]})
    no_leader=score([{'id':t['id'],'name':t['name'],**summarize([r for r in groups[t['id']] if r['shop']!=next(m for m in metrics if m['id']==t['id'])['largest_shop']])} for t in CFG['tracks']])
    sensitivity.append({'scenario':'各赛道剔除最大店铺','ranking':[{'id':r['id'],'n':r['n'],'score':r['score']} for r in no_leader]})
    rng=random.Random(20260917);wins=Counter()
    for _ in range(1000):
        base=CFG['lenses']['均衡首发']; ws=[v*rng.uniform(.8,1.2) for v in base];ws=[v/sum(ws)*100 for v in ws]
        wins[score(metrics,{'扰动':ws})[0]['id']]+=1
    overlap=[{'left':a['id'],'right':b['id'],'products':len(set(groups_rank(groups[a['id']]))&set(groups_rank(groups[b['id']]))) }
             for i,a in enumerate(CFG['tracks']) for b in CFG['tracks'][i+1:]]
    return ranked,groups,{'scenarios':sensitivity,'weight_trials':1000,'weight_winners':dict(wins),'seed':20260917},overlap

def groups_rank(rows): return {r['rank'] for r in rows}

def baseline_stats(rows):
    cleaned=[r for r in rows if not r['exclude'] and not r['bundle'] and not r['custom']]
    bands=[]
    for low,high in [(100,300),(300,800),(800,1500),(1500,2000),(2000,3000),(3000,5000),(5000,10000),(10000,1000000)]:
        vals=[r for r in cleaned if low<=r['price']<high]
        bands.append({'band':f'{low}–{high if high<1000000 else "以上"}',**summarize(vals)})
    features=[]
    patterns={'双面双睡感':r'双面|双睡感|双睡|软硬两|正反', '独袋静音':r'独立袋|独袋|袋装|静音|抗干扰',
              '偏硬承托':r'偏硬|护脊|舒脊|护腰|承托','0胶宣称':r'0胶|零胶|无胶','可拆洗':r'可拆洗|可拆可洗|可拆.*洗',
              '乳胶':r'乳胶','透气':r'透气|空气纤维|3d','儿童人群':r'儿童|青少年|kids'}
    for name,pat in patterns.items():
        matched=[r for r in cleaned if re.search(pat,r['text'],re.I)]
        features.append({'feature':name,**summarize(matched)})
    return {'bands':bands,'features':features,'clean_sku_median':med(r['price'] for r in cleaned)}

def image_stats(images):
    valid=[v for v in images.values() if v.get('has_image')]
    result={}
    for key in ['selling_points','marketing_text','visual_format']:
        c=Counter(x for v in valid for x in set(v.get(key,[])))
        result[key]=[{'label':label,'count':n,'share':n/len(valid)} for label,n in c.most_common()]
    return result

def main():
    OUT.mkdir(exist_ok=True)
    db,images,same=sources();rows,audit=clean(db,images,same)
    tracks,members,sensitivity,overlap=explore(rows)
    base=baseline_stats(rows)
    result={'config_version':CFG['version'],'assumption':CFG['assumption'],'audit':audit,'tracks':tracks,
            'sensitivity':sensitivity,'overlap':overlap,'baseline':base,'images':image_stats(images)}
    result['strict_dual']=summarize([r for r in members['T1'] if re.search('双面|双睡感|双睡|软硬两',r['text'])])
    if (HERE/'product_concepts.json').exists():
        from product_review import evaluate
        result['products']=evaluate(rows,tracks[0]['id'],members[tracks[0]['id']])
    result['analysis_input_hashes']={str(p.relative_to(HERE)):hashlib.sha256(p.read_bytes()).hexdigest()
         for p in sorted(list(HERE.glob('*.py'))+[HERE/'scoring_config.json',HERE/'product_concepts.json']+list((HERE/'expert_reviews').glob('*.json')))}
    dump(OUT/'analysis_result.json',result)
    csvout('全量SKU清洗台账.csv',[{k:v for k,v in r.items() if k!='text'} for r in rows])
    csvout('赛道命中明细.csv',[{'track_id':t,**{k:v for k,v in r.items() if k!='text'}} for t,rs in members.items() for r in rs])
    csvout('赛道评分.csv',[{k:v for k,v in r.items() if k!='ranks'} for r in tracks])
    csvout('价格带.csv',base['bands']);csvout('功能信号.csv',base['features'])
    from render_report import render
    render(result,CFG,rows,members)
    for name,digest in audit['source_hashes'].items():
        assert hashlib.sha256((ROOT/name).read_bytes()).hexdigest()==digest,'source changed'
    print(json.dumps({'products':audit['raw_products'],'raw_skus':audit['raw_skus'],'clean_skus':audit['clean_skus'],
                      'track_winner':tracks[0]['id'],'track_score':round(tracks[0]['score'],2),
                      'product_status':result.get('products',{}).get('status'),
                      'product_ranking':[{'id':p['id'],'score':None if p['score'] is None else round(p['score'],2)} for p in result.get('products',{}).get('ranking',[])],
                      'report':str(HERE/'深度分析报告.md')},ensure_ascii=False,indent=2))

if __name__=='__main__': main()

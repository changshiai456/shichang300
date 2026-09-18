"""Independent reviews and explicitly hypothetical unit economics."""
import json
import random
import statistics as st
from collections import Counter
from pathlib import Path

HERE=Path(__file__).resolve().parent

def economics(product):
    p=product['hero_price'];c=product['cost_assumption'];f=product['freight_assumption']
    values=[]
    for name,mult,extra,fee,reserve,ad in [('顺利',.9,-30,.06,.05,.15),('基准',1,0,.06,.08,.20),('压力',1.15,50,.06,.12,.28)]:
        cost=c*mult;freight=f+extra
        contribution=p*(1-fee-reserve-ad)-cost-freight
        max_c=p*(1-fee-reserve-ad-.15)-freight
        values.append({'scenario':name,'price':p,'manufacturing_packaging':cost,'freight':freight,
                       'platform_rate':fee,'aftersales_reserve_rate':reserve,'ad_rate':ad,
                       'ad_cost':p*ad,'contribution':contribution,'contribution_rate':contribution/p,
                       'max_manufacturing_packaging_at_15pct':max_c,
                       'max_cac_at_15pct':p*(1-fee-reserve-.15)-cost-freight,
                       'breakeven_cac':p*(1-fee-reserve)-cost-freight,
                       'price_floor_at_15pct':(cost+freight)/(1-fee-reserve-ad-.15)})
    return values

def evaluate(rows,winning_track,winning_rows):
    from pipeline import summarize
    import re
    cfg=json.loads((HERE/'scoring_config.json').read_text(encoding='utf-8'))
    concepts=json.loads((HERE/'product_concepts.json').read_text(encoding='utf-8'))
    if concepts['track_id']!=winning_track:
        raise ValueError('Winning track changed; redesign product concepts before rerunning.')
    reviews={}
    for path in sorted((HERE/'expert_reviews').glob('*.json')):
        value=json.loads(path.read_text(encoding='utf-8'))
        role=value['role'];assert role not in reviews,'duplicate expert role'
        assert value['rubric']==cfg['product_rubric'][role],'rubric mismatch'
        assert {p['id'] for p in value['products']}=={p['id'] for p in concepts['products']}
        reviews[role]=value
    missing=sorted(set(cfg['product_weights'])-set(reviews))
    result=[]
    for p in concepts['products']:
        assert abs(sum(layer[1] for layer in p['layers'])-p['height'])<1e-8
        row={**p,'economics':economics(p),'expert_scores':{},'reviews':[]}
        evidence=[r for r in winning_rows if all(re.search(pat,r['text'],re.I) for pat in p['evidence_groups'])]
        row['evidence']=summarize(evidence)
        for role,review in reviews.items():
            item=next(r for r in review['products'] if r['id']==p['id'])
            assert set(item['scores'])==set(cfg['product_rubric'][role]),'score keys mismatch'
            assert all(isinstance(v,(int,float)) and 0<=v<=100 for v in item['scores'].values())
            score=sum(item['scores'][k]*w for k,w in cfg['product_rubric'][role].items())/100
            row['expert_scores'][role]=score
            row['reviews'].append({'role':role,**item,'total':score})
        row['score']=None if missing else sum(row['expert_scores'][k]*w for k,w in cfg['product_weights'].items())/100
        result.append(row)
    result.sort(key=lambda p:p['score'] if p['score'] is not None else 0,reverse=True)
    sensitivity={'status':'pending'}
    if not missing:
        scenarios=[]
        for role in cfg['product_weights']:
            weights={k:(40 if k==role else 20) for k in cfg['product_weights']}
            score={p['id']:sum(p['expert_scores'][k]*w/100 for k,w in weights.items()) for p in result}
            scenarios.append({'scenario':role+'权重40%','scores':score,'winner':max(score,key=score.get)})
        rng=random.Random(20260917);wins=Counter()
        for _ in range(1000):
            weights={k:v*rng.uniform(.8,1.2) for k,v in cfg['product_weights'].items()};total=sum(weights.values())
            ss={p['id']:sum(p['expert_scores'][k]*w/total for k,w in weights.items()) for p in result}
            wins[max(ss,key=ss.get)]+=1
        # Score perturbation explores judgement uncertainty separately from weights.
        jitter=Counter()
        for _ in range(1000):
            ss={p['id']:sum(max(0,min(100,p['expert_scores'][k]+rng.uniform(-5,5)))*w/100 for k,w in cfg['product_weights'].items()) for p in result}
            jitter[max(ss,key=ss.get)]+=1
        sensitivity={'status':'complete','scenarios':scenarios,'weight_trials':1000,'weight_winners':dict(wins),'score_jitter_winners':dict(jitter),'seed':20260917}
    return {'status':'pending' if missing else 'complete','missing_reviews':missing,'ranking':result,
            'sensitivity':sensitivity,'winner':None if missing else result[0]['id'],
            'score_interpretation':'四角色智能体对方案的判断分，不是销量概率、实际CTR、检测评分或财务预测。'}

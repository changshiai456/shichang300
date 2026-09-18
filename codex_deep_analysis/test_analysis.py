"""Run with python codex_deep_analysis/test_analysis.py after the analysis."""
import csv
import hashlib
import json
import re
import unittest
from collections import Counter
from html.parser import HTMLParser

import pipeline as p
from product_review import economics

class AnalysisChecks(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.db,cls.images,same=p.sources()
        cls.rows,cls.audit=p.clean(cls.db,cls.images,same)
        cls.result=json.loads((p.OUT/'analysis_result.json').read_text(encoding='utf-8'))

    def test_all_source_records_accounted_for(self):
        self.assertEqual(len(self.rows),sum(len(x['skus']) for x in self.db['products']))
        self.assertEqual(sum(self.audit['mutually_exclusive_cleaning_counts'].values()),len(self.rows))
        self.assertEqual(len({r['row_id'] for r in self.rows}),len(self.rows))
        with (p.OUT/'全量SKU清洗台账.csv').open(encoding='utf-8-sig') as f:
            self.assertEqual(len(list(csv.DictReader(f))),len(self.rows))

    def test_dedup_and_price_validity(self):
        keep=[r for r in self.rows if not r['exclude']]
        keys=[(r['rank'],re.sub(r'\s+','',r['sku_name']).lower(),r['price']) for r in keep]
        self.assertEqual(len(keys),len(set(keys)))
        self.assertTrue(all(r['price']>=100 for r in keep))
        self.assertFalse(any(r['rank'] in [24,181,202] for r in keep))

    def test_whole_height_not_component_median(self):
        self.assertEqual(p.total_height('厚23CM，2cm乳胶+1cm黄麻')[0],23)
        self.assertEqual(p.total_height('6cm厚=4cm椰棕+2cm面料')[0],6)
        self.assertEqual(p.total_height('双睡感/25CM】2cm乳胶')[0],25)
        self.assertIsNone(p.total_height('2cm乳胶+3cm黄麻')[0])
        self.assertIsNone(p.total_height('标准1.8m')[0])

    def test_keyword_groups_and_price_same_sku(self):
        track=p.CFG['tracks'][0]
        r={'exclude':'','bundle':False,'custom':False,'price':2199,'height':23,'text':'双面独立袋装弹簧'}
        self.assertTrue(p.qualifies(r,track))
        self.assertFalse(p.qualifies({**r,'price':999},track))
        self.assertFalse(p.qualifies({**r,'text':'针织面料'},track))
        self.assertFalse(p.qualifies({**r,'height':10},track))
        self.assertTrue(p.qualifies({**r,'height':None},track))
        self.assertFalse(p.qualifies({**r,'height':None},track,strict_height=True))
        self.assertFalse(p.qualifies({**r,'bundle':True},track))

    def test_evidence_aggregates_match_output(self):
        for t in p.CFG['tracks']:
            vals=[r for r in self.rows if p.qualifies(r,t)]
            summary=p.summarize(vals)
            result=next(x for x in self.result['tracks'] if x['id']==t['id'])
            for key in ['n','sku_n','shops','median_price','top50','hhi']:
                self.assertEqual(result[key],summary[key])
        self.assertTrue(all('image' not in r and 'ocr' not in r for r in self.rows))

    def test_expert_completeness_and_arithmetic(self):
        result=self.result['products']
        self.assertEqual(result['status'],'complete')
        self.assertEqual(len(result['ranking']),5)
        for product in result['ranking']:
            self.assertEqual(set(product['expert_scores']),set(p.CFG['product_weights']))
            for review in product['reviews']:
                weight=p.CFG['product_rubric'][review['role']]
                expected=sum(review['scores'][k]*w/100 for k,w in weight.items())
                self.assertAlmostEqual(review['total'],expected)
            expected=sum(product['expert_scores'][k]*w/100 for k,w in p.CFG['product_weights'].items())
            self.assertAlmostEqual(product['score'],expected)

    def test_economics_and_layer_sum(self):
        for product in self.result['products']['ranking']:
            self.assertAlmostEqual(sum(h for _,h in product['layers']),product['height'])
            es=economics(product);base=es[1];price=product['hero_price']
            self.assertAlmostEqual(base['contribution'],price*.66-product['cost_assumption']-product['freight_assumption'])
            c=base['max_manufacturing_packaging_at_15pct']
            self.assertAlmostEqual(price*.66-c-product['freight_assumption'],price*.15)
            self.assertLess(es[2]['contribution'],base['contribution'])

    def test_sources_unchanged(self):
        for name,digest in self.result['audit']['source_hashes'].items():
            self.assertEqual(hashlib.sha256((p.ROOT/name).read_bytes()).hexdigest(),digest)

    def test_report_and_csv_same_winner(self):
        report=(p.HERE/'深度分析报告.md').read_text(encoding='utf-8')
        winner=self.result['products']['ranking'][0]
        self.assertIn('产品终选：'+winner['id']+' '+winner['name'],report)
        self.assertNotIn('尚待四角色',report)
        with (p.OUT/'产品方案与评分.csv').open(encoding='utf-8-sig') as f:
            rows=list(csv.DictReader(f))
        self.assertEqual(rows[0]['id'],winner['id'])
        self.assertAlmostEqual(float(rows[0]['score']),winner['score'])

    def test_offline_html_tables_and_anchors(self):
        class Inspector(HTMLParser):
            def __init__(self):
                super().__init__();self.tables=[];self.cells=[];self.ids=set();self.links=[];self.current=0
            def handle_starttag(self,tag,attrs):
                attrs=dict(attrs)
                if 'id' in attrs:self.ids.add(attrs['id'])
                if tag=='a':self.links.append(attrs.get('href',''))
                if tag=='table':self.cells=[]
                if tag=='tr':self.current=0
                if tag in ['td','th']:self.current+=1
            def handle_endtag(self,tag):
                if tag=='tr':self.cells.append(self.current)
                if tag=='table':self.tables.append(list(self.cells))
        checker=Inspector();checker.feed((p.HERE/'index.html').read_text(encoding='utf-8'))
        self.assertGreater(len(checker.tables),15)
        self.assertTrue(all(len(set(t))==1 for t in checker.tables))
        self.assertTrue(all(link[1:] in checker.ids for link in checker.links if link.startswith('#')))

if __name__=='__main__': unittest.main(verbosity=2)

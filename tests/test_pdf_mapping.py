import json
import unittest
from pdf_mapping import suggest_mappings, pdf_requirements, exclude_score_summaries

class MappingTests(unittest.TestCase):
    def document(self):
        return {'pages':[{'page':1,'mode':'ocr','ocr_text':'We encrypt data.','native_text':''}]}
    def responder(self, ids):
        def call(base,endpoint,payload,timeout):
            req=json.loads(payload['messages'][1]['content'])['requirements']
            return {'choices':[{'finish_reason':'stop','message':{'content':json.dumps({'selections':[{'requirement_id':r['id'],'block_ids':ids if i==0 else []} for i,r in enumerate(req)]})}}]}
        return call
    def test_twenty_questions_verbatim_and_not_found(self):
        result=suggest_mappings(self.document(),pdf_requirements(),self.responder([0]))
        self.assertEqual(len(result),20)
        self.assertEqual(result[0]['answer'],'We encrypt data.')
        self.assertEqual(result[0]['pages'],[1])
        self.assertEqual(result[0]['correction_note'],'')
        self.assertEqual(result[1]['answer'],'')
        self.assertEqual(result[1]['pages'],[])
    def test_invalid_reference_rejected(self):
        for ids in [[999],[True],[-1]]:
            with self.assertRaises(ValueError):
                suggest_mappings(self.document(),pdf_requirements(),self.responder(ids))

    def test_known_table_row_retains_response_without_inference(self):
        text = 'Column 1: HLPP-03 | Column 2: Policy? | Column 3: No | Column 4: Planned next year | Column 5: Supply a policy'
        doc = {'pages':[{'page':2,'mode':'native','native_text':text,'ocr_text':''}]}
        def forbidden(*args):
            raise AssertionError('Known table row should not need inference')
        result = suggest_mappings(doc,[pdf_requirements()[5]],forbidden)
        self.assertEqual(result[0]['answer'],text)
        self.assertEqual(result[0]['pages'],[2])

    def test_empty_scan_is_unresolved_without_fabricated_text(self):
        doc = {'pages':[{'page':1,'mode':'ocr','ocr_text':'','native_text':''}]}
        result = suggest_mappings(doc,pdf_requirements())
        self.assertEqual(len(result),20)
        self.assertTrue(all(not m['answer'] and not m['pages'] for m in result))

    def test_scorecard_is_not_supplier_evidence(self):
        score='Column 1: Incident Handling | Column 2: | Column 3: 100.00% | Column 4:'
        rows=[dict(requirement_id='BUYER-02',answer='Plan exists.\n\n'+score,pages=[1,2],modes={'1':'native','2':'native'})]
        doc={'pages':[{'page':1,'mode':'native','native_text':'Plan exists.'},{'page':2,'mode':'native','native_text':score}]}
        result=exclude_score_summaries(rows,doc)
        self.assertEqual(result[0]['answer'],'Plan exists.')
        self.assertEqual(result[0]['pages'],[1])

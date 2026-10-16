"""Extract ruled table rows locally, retaining labeled cells and source pages."""
import json
import sys
import pdfplumber

pages = []
with pdfplumber.open(sys.argv[1]) as document:
    for page in document.pages:
        rows = []
        tables = page.find_tables()
        for table in tables:
            for row in table.extract():
                cells = [cell or '' for cell in row]
                if any(cells):
                    # Keep column positions explicit; no claim that every table has a HECVAT layout.
                    rows.append(' | '.join(f'Column {i+1}: {cell}' for i, cell in enumerate(cells)))
        if rows:
            outside = page.filter(lambda obj: not any(
                obj.get('x0',0)>=t.bbox[0] and obj.get('x1',0)<=t.bbox[2] and
                obj.get('top',0)>=t.bbox[1] and obj.get('bottom',0)<=t.bbox[3] for t in tables))
            pages.append({'page':page.page_number,'text':(outside.extract_text() or '')+'\n\n'+'\n\n'.join(rows)})
print(json.dumps(pages))

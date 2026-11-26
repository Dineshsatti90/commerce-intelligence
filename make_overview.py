"""Small GitHub-native SVG of actual results; not a fabricated application screenshot."""
from pathlib import Path
import csv,json
from datetime import date
ROOT=Path(__file__).resolve().parent
m=json.loads((ROOT/'reports/metrics.json').read_text())
rows=sorted(csv.DictReader((ROOT/'reports/mart_monthly.csv').open()),key=lambda x:x['month'])
values=[float(r['delivered_gmv_brl'] or 0) for r in rows]
dates=[date.fromisoformat(r['month']).toordinal() for r in rows]
coords=[(65+(d-min(dates))/(max(dates)-min(dates))*970,410-v/max(values)*200) for d,v in zip(dates,values)]
line=' '.join(f'{x:.1f},{y:.1f}' for x,y in coords)
svg=f'''<svg xmlns="http://www.w3.org/2000/svg" width="1100" height="540" viewBox="0 0 1100 540">
<rect width="1100" height="540" fill="#101c2c" rx="16"/>
<g font-family="Arial,sans-serif" fill="#f4f7fc">
<text x="48" y="54" font-size="28" font-weight="bold">Commerce Intelligence</text>
<text x="48" y="83" font-size="14" fill="#a8b9d0">Real Olist orders · historical marketplace analysis · purchases before September 2018</text>
<text x="48" y="137" font-size="14" fill="#a8b9d0">ANALYZED ORDERS</text><text x="48" y="176" font-size="34">{m['orders']:,}</text>
<text x="390" y="137" font-size="14" fill="#a8b9d0">DELIVERED MERCHANDISE GMV</text><text x="390" y="176" font-size="34">R${m['delivered_gmv_brl']/1e6:.2f}m</text>
<text x="800" y="137" font-size="14" fill="#a8b9d0">90-DAY REPEAT RATE</text><text x="800" y="176" font-size="34">{m['repeat_90d_rate']:.2%}</text>
<text x="48" y="225" font-size="16">Monthly delivered merchandise GMV (BRL)</text>
<line x1="65" y1="410" x2="1035" y2="410" stroke="#3c4e68"/>
<polyline points="{line}" fill="none" stroke="#64d4c3" stroke-width="3"/>
<text x="65" y="440" font-size="13" fill="#a8b9d0">{rows[0]['month']}</text><text x="945" y="440" font-size="13" fill="#a8b9d0">{rows[-1]['month']}</text>
<text x="48" y="482" font-size="14" fill="#a8b9d0">Repeat rate uses {m['eligible_90d_customers']:,} customers with complete 90-day observation. GMV is not company revenue.</text>
<text x="48" y="509" font-size="13" fill="#a8b9d0">Source: Olist, Kaggle release v2 · CC BY-NC-SA 4.0 · calculations: dbt marts and reports/metrics.json</text>
</g></svg>'''
(ROOT/'reports/overview.svg').write_text(svg,encoding='utf-8')

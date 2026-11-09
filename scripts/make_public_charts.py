"""Export an aggregate forecast chart without row-level machine telemetry."""
import csv
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
source = ROOT / 'Task1' / 'forecasts.csv'
totals = defaultdict(lambda: [0.0, 0.0, 0])
with source.open(newline='', encoding='utf-8') as handle:
    for row in csv.DictReader(handle):
        h = int(row['horizon_steps'])
        actual = float(row['actual'])
        totals[h][0] += abs(actual-float(row['persistence']))
        totals[h][1] += abs(actual-float(row['random_forest']))
        totals[h][2] += 1
values = [(h, totals[h][0]/totals[h][2], totals[h][1]/totals[h][2]) for h in sorted(totals)]
assert len(values) == 12
width, height = 760, 330
def path(col):
    return ' '.join(f"{'M' if i==0 else 'L'} {70+i*55} {270-v[col]*9:.1f}" for i,v in enumerate(values))
svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img" aria-label="Forecast MAE by horizon, persistence versus random forest">
<rect width="100%" height="100%" fill="#f7faf8"/><text x="60" y="35" font-family="Arial" font-weight="bold" font-size="19" fill="#152b32">Forecast error by horizon</text>
<text x="60" y="55" font-family="Arial" font-size="12" fill="#65747a">Held-out MAE · twelve five-minute steps · units unspecified</text>
<path d="M70 80 V270 H710" fill="none" stroke="#93aaa6" stroke-width="1"/>
<path d="{path(1)}" fill="none" stroke="#6e8294" stroke-width="3"/>
<path d="{path(2)}" fill="none" stroke="#087f70" stroke-width="3"/>
<text x="560" y="93" font-family="Arial" font-size="12" fill="#6e8294">— Persistence</text>
<text x="560" y="113" font-family="Arial" font-size="12" fill="#087f70">— Random forest</text>
<text x="310" y="310" font-family="Arial" font-size="12" fill="#65747a">Forecast horizon (5-minute steps)</text>
</svg>'''
destination = ROOT / 'frontend' / 'public' / 'forecast-error.svg'
destination.write_text(svg, encoding='utf-8')
print(destination)

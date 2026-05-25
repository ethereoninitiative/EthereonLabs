from pathlib import Path
import json

ROOT = Path(__file__).resolve().parents[1]
html = list(ROOT.rglob('*.html'))
flags = []
for path in html:
    text = path.read_text(encoding='utf-8', errors='ignore')
    if 'position: absolute' in text:
        flags.append({'file': str(path.relative_to(ROOT)), 'issue': 'absolute positioning'})
    if 'grid-template-columns: repeat(5' in text:
        flags.append({'file': str(path.relative_to(ROOT)), 'issue': 'dense desktop grid'})
report = {'check': 'page_layout_r1', 'flags': flags, 'status': 'watch' if flags else 'pass'}
out_dir = ROOT / '_site_trials'
out_dir.mkdir(exist_ok=True)
(out_dir / 'page_layout_r1_report.json').write_text(json.dumps(report, indent=2), encoding='utf-8')
print(json.dumps(report, indent=2))

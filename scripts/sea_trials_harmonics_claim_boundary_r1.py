from pathlib import Path
import json

ROOT = Path(__file__).resolve().parents[1]
TEXT = (ROOT / 'harmonics.html').read_text(encoding='utf-8').lower()

required = ['advisory', 'does not govern']
forbidden = [
    'proves continuity',
    'governs runtime',
    'authorizes capability',
    'determines legality',
    'establishes autonomy',
]

report = {
    'check': 'harmonics_claim_boundary_r1',
    'missing_required': [item for item in required if item not in TEXT],
    'forbidden_hits': [item for item in forbidden if item in TEXT],
}
report['passed'] = not report['missing_required'] and not report['forbidden_hits']

out_dir = ROOT / '_site_trials'
out_dir.mkdir(exist_ok=True)
(out_dir / 'harmonics_claim_boundary_r1_report.json').write_text(json.dumps(report, indent=2), encoding='utf-8')
print(json.dumps(report, indent=2))
if not report['passed']:
    raise SystemExit(1)

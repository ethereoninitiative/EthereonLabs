from pathlib import Path
import json

ROOT = Path(__file__).resolve().parents[1]
FILES = list(ROOT.rglob('*.html')) + list(ROOT.rglob('*.md'))
SYMBOLIC = ['resonance', 'harmonic', 'witness', 'spiral', 'signal']
AUTHORITY = ['proves continuity', 'governs runtime', 'authorizes capability']
text = '\n'.join(path.read_text(encoding='utf-8', errors='ignore').lower() for path in FILES)
report = {
  'meta_pulse_version': 'r1',
  'symbolic_density': sum(text.count(x) for x in SYMBOLIC),
  'authority_leakage_hits': [x for x in AUTHORITY if x in text],
}
report['status'] = 'watch' if report['authority_leakage_hits'] else 'pass'
out_dir = ROOT / '_site_trials'
out_dir.mkdir(exist_ok=True)
(out_dir / 'meta_pulse_core_integrity_r1_report.json').write_text(json.dumps(report, indent=2), encoding='utf-8')
print(json.dumps(report, indent=2))

# IRP-R1 bounded exchange fixture

Synthetic protocol evidence only. No OpenAI, Anthropic, or Google model was
called. Provider and resident labels are declared fixture metadata.

`exchange.json` contains three independent root packets over one bounded sensor
evidence set, followed by one synthesis attributed to the first resident. Two
interpretations favor thermal drift (7800 and 6200 basis points); one favors
sensor noise (5400). The fourth packet preserves all three positions and binds
its parent packets and referenced claims. No authority or identity authentication
follows from validation.

Regenerate from the V2 directory:

```bash
python runtime/interresident_resonance_demo_r1.py > artifacts/interresident_resonance/fixture_r1/exchange.json
```

The sea trial requires deterministic equality with this fixture, exercises disk
append/reopen and tampering in temporary stores, and validates all CLI paths.
Full contract: `docs/Interresident_Resonance_Protocol_R1.md` in the V2 directory.

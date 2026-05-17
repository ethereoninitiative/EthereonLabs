# DryDock Site Header Normalization Runbook

This runbook records the current post-normalization state of the EthereonLabs site header and the safe process for future header/navigation changes.

## Current state

The site header has completed migration away from runtime header normalization.

Current source-of-truth layers:

1. Root HTML pages — contain baked canonical primary navigation markup.
2. `assets/js/site-navigation-data.js` — stores canonical primary and secondary footer navigation data.
3. `assets/js/brand-sigil.js` — focused enhancer that restores the animated brand sigil inside `.brand-mark`.
4. `assets/js/site.js` — lightweight enhancement bootstrap for nav data, brand sigil, footer secondary links, and year rendering.
5. `tools/audit_site_headers.py` — checks root HTML headers against canonical navigation.
6. `.github/workflows/site-header-audit.yml` — runs the header audit on relevant pull requests.
7. `.github/workflows/canonicalize-site-headers.yml` — manually generates a patch artifact when canonicalization is needed.

## Important dependency note

The animated brand sigil previously lived inside `header-normalizer.js`. Retiring the normalizer without replacing that visual payload caused the brand mark to disappear.

Future cleanup must distinguish between:

- header/nav mutation logic, which should stay retired;
- focused visual enhancement, currently handled by `brand-sigil.js`.

Do not remove visual enhancer scripts without checking what visible payload they carry.

## Deprecated compatibility file

`assets/js/header-normalizer.js` is now inert and retained temporarily as a compatibility stub. It should not be used for new work.

Before removing it entirely, confirm:

- no HTML page loads it directly;
- `assets/js/site.js` does not load it;
- deploy preview shows the animated brand sigil on desktop and mobile;
- `python tools/audit_site_headers.py` passes.

## Future navigation change process

When changing primary navigation:

1. Update `assets/js/site-navigation-data.js`.
2. Run the canonicalizer:

```bash
python tools/canonicalize_site_headers.py
```

3. Run the audit:

```bash
python tools/audit_site_headers.py
```

4. Inspect the resulting HTML diff.
5. Confirm the diff only changes intended header/nav/brand markup.
6. Check the Netlify deploy preview on desktop and mobile.

## Manual GitHub workflow path

For repo-hosted canonicalization:

1. Go to GitHub Actions.
2. Run **Canonicalize Site Headers** manually.
3. Download the `site-header-canonicalization-patch` artifact.
4. Inspect the patch.
5. Apply the patch in a normal PR if it is correct.
6. Confirm the **Site Header Audit** workflow passes.
7. Check Netlify preview on desktop and mobile.

The workflow intentionally generates a patch artifact rather than trying to open a pull request automatically.

## Guardrail

The goal is not merely to make the header look correct after JavaScript runs. The goal is for source HTML, shared nav data, visual enhancement, and audit tooling to agree.

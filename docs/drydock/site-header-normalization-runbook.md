# DryDock Site Header Normalization Runbook

This runbook records the current post-normalization state of the EthereonLabs site header and the safe process for future header/navigation changes.

## Current state

The site header has completed migration away from runtime header normalization.

Current source-of-truth layers:

1. `assets/js/site-navigation-data.js` — owns the ordered canonical primary navigation contract and secondary footer navigation data.
2. Root HTML pages — contain baked primary navigation markup that must mirror the shared contract before JavaScript runs.
3. `tools/site_navigation_contract.py` — parses and validates the shared primary-navigation contract, including duplicate and missing-target checks.
4. `tools/canonicalize_site_headers.py` — rewrites baked root HTML headers from the shared navigation contract and normalizes brand markup.
5. `tools/audit_site_headers.py` — checks baked root HTML headers against that same shared contract.
6. `assets/js/brand-sigil.js` — focused enhancer that restores the animated brand sigil inside `.brand-mark`.
7. `assets/js/site.js` — lightweight enhancement bootstrap for nav data, brand sigil, footer secondary links, and year rendering.
8. `.github/workflows/site-header-audit.yml` — runs the contract audit on relevant pull requests.
9. `.github/workflows/canonicalize-site-headers.yml` — manually generates a patch artifact when canonicalization is needed.

The primary list is defined once. The baked markup, canonicalizer, and audit must not carry competing hard-coded primary lists.

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

1. Update the ordered `primary` array in `assets/js/site-navigation-data.js`.
2. Run the canonicalizer:

```bash
python tools/canonicalize_site_headers.py
```

3. Run the audit:

```bash
python tools/audit_site_headers.py
```

4. Run the wider public-surface sea trial:

```bash
python scripts/sea_trials_website_public_surface_r1.py
```

5. Inspect the resulting HTML diff.
6. Confirm the diff only changes intended header/nav/brand markup.
7. Check the Netlify deploy preview on desktop and mobile.

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

The goal is not merely to make the header look correct after JavaScript runs. The goal is for shared navigation data, baked source HTML, visual enhancement, audit tooling, and the public-surface sea trial to agree.

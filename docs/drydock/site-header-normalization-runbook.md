# DryDock Site Header Normalization Runbook

This runbook controls the final migration from runtime header normalization toward canonical baked HTML headers.

## Current state

The site currently has three safety layers:

1. `assets/js/site-navigation-data.js` — canonical navigation data.
2. `tools/audit_site_headers.py` — checks root HTML headers against canonical navigation.
3. `.github/workflows/canonicalize-site-headers.yml` — manually generates a canonicalization patch artifact.

`header-normalizer.js` remains as a compatibility layer until baked HTML headers are confirmed canonical.

## Gate before retiring runtime normalization

Proceed only after all checks below pass:

- `python tools/canonicalize_site_headers.py` has been run against the repo.
- `python tools/audit_site_headers.py` passes afterward.
- The generated HTML diff has been inspected for only header, nav, and brand changes.
- Netlify deploy preview has been checked on desktop and mobile.

## Manual GitHub workflow path

1. Go to GitHub Actions.
2. Run **Canonicalize Site Headers** manually.
3. Download the `site-header-canonicalization-patch` artifact.
4. Inspect the patch.
5. Apply patch in a PR titled `DryDock: canonicalize baked site headers`.
6. Confirm the **Site Header Audit** workflow passes.
7. Check Netlify preview on desktop and mobile.
8. After that, open a separate PR to retire the runtime header normalizer.

## Local path

```bash
python tools/canonicalize_site_headers.py
python tools/audit_site_headers.py
git diff
```

If the audit passes and the diff only changes root HTML header, nav, and brand markup, commit the result.

## Final retirement PR

After baked headers pass audit, update the site so `assets/js/site.js` no longer loads `assets/js/header-normalizer.js`, then archive or remove the normalizer file in that same PR.

Then rerun:

```bash
python tools/audit_site_headers.py
```

Check the deploy preview before merge.

## Boundary

This process is intentionally slower than bypassing the normalizer immediately. The goal is to end with canonical static headers without breaking navigation, page highlighting, brand rendering, or mobile layout.

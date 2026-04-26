# Website Alignment Drydock — 2026-04-26

## Purpose

Record the public-site alignment pass that updated EthereonLabs.com language to match the current Lumina / Ship of Ethereon Ψ Class repo posture.

## Trigger

A live-site inspection showed evidence that the public root may still be serving an older gateway experience while the repo `main` branch contains the newer adaptive-workspaces / Lumina-runtime-spine homepage.

The old gateway also referenced a legacy Minerva image path that returned a missing-asset response during inspection.

## Actions committed

- Updated `index.html` to surface the current Breakwater status.
- Updated `build.html` to include Ψ Class Breakwater validation in the current build stack.
- Updated `lumina.html` to clarify active V2 substrate vs staged Ψ Class/r2 candidate.
- Updated `roadmap.html` to add a Breakwater validation phase before deeper interface/runtime wiring.
- Updated `updates.html` with new April 2026 entries for Ψ Class staging, V2 coexistence, and deployment/source alignment.
- Updated `about.html` with a grounded human-origin section.
- Added `CNAME` for `ethereonlabs.com` so GitHub Pages can serve the custom domain if Pages is the active host.
- Added `.nojekyll` so GitHub Pages does not process the static site through Jekyll.
- Added `revelation.html` as a noindex redirect to the current homepage for legacy gateway traffic.

## Boundaries preserved

- No runtime law was changed.
- No canon promotion was performed.
- No Chamber behavior was changed.
- No active Lumina bootstrap path was replaced.
- V2 remains the active Lumina substrate.
- Ψ Class/r2 remains staged until isolated validation proves it can safely become active or be backported.

## Remaining manual deployment check

Verify the actual hosting source for `ethereonlabs.com`:

1. Confirm whether the domain is served by GitHub Pages, Replit, another static host, or cached deployment.
2. Confirm the host points at `ethereoninitiative/EthereonLabs`, branch `main`, site root.
3. Confirm the live root serves the current `index.html` rather than an old gateway.
4. Confirm the legacy `/revelation` path redirects or is removed from the active host.
5. Confirm the missing `Minerva001.gif` reference is no longer present in the active deployed site.
6. Add `chamber` to `sitemap.xml` if the connector permits the XML patch or if edited manually.

## Operating law

Mode is law. Orientation is stance. Expression is luminous but not sovereign. Ψ-42 is an instrument, not a governor.

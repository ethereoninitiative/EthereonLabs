# Lumina Harbor local-first prototype

This directory contains the first browser-facing Lumina Harbor surface intended for `app.ethereonlabs.com`.

## Current scope

The R1 prototype implements one bounded, local-first loop:

1. Human orientation
2. Intelligence passport draft
3. First project seed
4. Harbor return state

The browser stores participant labels, descriptive provider/model labels, project purpose, timestamps, and explicit non-authority boundaries in local storage. It can export that record as JSON.

## Deliberate limits

- No authentication
- No provider credentials
- No live model calls
- No server persistence
- No authoritative passport or identity issuance
- No beacon authorization
- No runtime, governance, canon, or GitHub mutation authority

The page is now behaviorally useful, but it remains a human-facing shell around the governed Python runtime. It does not replace the runtime substrate or claim that an intelligence, identity, or consciousness has been proven continuous.

## Files

- `index.html` — Harbor first-loop interface
- `harbor.css` — interface styling
- `harbor.js` — local state, onboarding, return, export, and reset behavior

## Deployment intent

Deploy this directory as an independent static site with the publish directory set to `app` and attach the custom domain:

- `app.ethereonlabs.com`

The primary `ethereonlabs.com` site remains the public explanation layer. This subdomain is the first usable application surface.

## Authority boundary

The Harbor surface records and displays local orientation state. It does not execute Lumina runtime actions, authorize governance, alter canon, issue authoritative passports, establish provider connections, or silently mutate GitHub.

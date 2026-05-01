# Spencer Artist Site — Artwork-Morphed Temporary Website r3

## Current decision

This page should feel like Spencer Tracy Brown's artist website, not like an EthereonLabs subpage.

EthereonLabs is only the temporary host.

The visual system is now allowed to derive from Spencer's actual artwork rather than from a neutral gallery template.

## Temporary URL after merge

`https://ethereonlabs.com/artist-spencer.html`

## Current files

- `artist-spencer.html`
- `assets/css/artist-spencer.css`

The page does not import the shared EthereonLabs stylesheet or site JavaScript. It uses a standalone visual system so the artist site can later be lifted into its own domain with minimal cleanup.

## Indexing / privacy note

The page includes:

```html
<meta name="robots" content="noindex, nofollow" />
```

This discourages search indexing, but it is not real privacy or password protection. Anyone with the URL can view it after deployment.

## Visual direction

Direction: artwork-morphed contemporary artist site.

The CSS now draws from uploaded artwork references:

- cobalt and ultramarine fields
- cadmium orange and yellow motion
- red accents
- rust, black glaze, and fired ceramic surfaces
- gold eyes / key-like accents
- mask, threshold, ceramic figure, and expressive-head concepts
- energetic spiral motion from the abstract paintings
- strong black-framed image blocks echoing object presence

This should feel less like a neutral portfolio shell and more like the artwork is pressing outward into the site design.

## Placeholder inventory

Current image placeholders:

1. primary artwork / hero image
2. Boundaries
3. Sanctuaries
4. Sculpture & Objects
5. Drawings & Studies
6. Public & Educational Work
7. artist portrait
8. studio table
9. Twee-Twee
10. classroom / teaching

## Implementation note

The current r3 pass primarily changes the CSS layer so the existing safe HTML structure visually morphs. Future passes can update the actual copy and image paths once final image assets are ready for the repo.

## Next refinements

- Add optimized image files under `assets/images/spencer/`.
- Replace placeholders with final image paths.
- Add artwork titles, years, media, and dimensions.
- Add a CV page or downloadable CV.
- Replace placeholder contact email.
- Decide whether the final domain is `spencertracybrown.com`, `spencerbrown.art`, or another dedicated artist URL.
- Later, remove `noindex` only when the dedicated artist site is ready for public discovery.

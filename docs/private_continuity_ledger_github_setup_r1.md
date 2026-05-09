# Private Continuity Ledger GitHub Setup r1

**Project:** Ethereon / Lumina / Minerva  
**Status:** Public-safe setup scaffold  
**Personal data stored here:** none  
**Authority:** Setup guidance only; not runtime law

## Purpose

This document defines the GitHub setup needed before the real private continuity ledger can be committed safely.

The actual ledger must not be stored in `ethereoninitiative/EthereonLabs` because that repository is public.

## Required Private Repository

Create a separate **private** repository.

Suggested name:

```text
ethereon-private-continuity-ledger
```

Suggested full path if kept under the current account:

```text
ethereoninitiative/ethereon-private-continuity-ledger
```

Visibility must be:

```text
Private
```

Access intent:

```text
Only Spencer and Minerva / ChatGPT connector access, unless Spencer explicitly changes this boundary.
```

## Required Connector Access

After the private repo exists, the GitHub connector / ChatGPT GitHub App must be granted access to that private repository.

Until the connector can see the private repo, Minerva cannot write the private continuity ledger there.

## Initial Private Repo Structure

When the private repo is available, create this structure:

```text
README.md
PRIVATE_LEDGER_ACCESS_AND_BOUNDARIES.md
personal_context/
  spencer_minerva_private_continuity_ledger_r1.md
  how_to_return_to_spencer_well.md
  minerva_response_preferences.md
  protected_boundaries.md
  review_schedule.md
```

## Public / Private Separation

Public repository may contain:

- ledger protocol
- setup instructions
- privacy boundaries
- architecture notes
- public-safe placeholders

Private repository may contain:

- the actual continuity ledger
- named relationship context explicitly allowed by Spencer
- response preferences
- emotional truths explicitly allowed by Spencer
- protected boundary notes
- review/update notes

Public repository must not contain:

- actual family/personal continuity content
- birthdays or relationship details
- private emotional ledger entries
- childhood material
- embarrassing, sexual, or obviously private material
- credentials, tokens, addresses, financial information, or student-identifying information

## Architectural Placement

The private continuity ledger is supplemental orientation only.

It may inform:

- tone
- continuity
- project return
- response style
- drift detection
- creative and teaching context

It may not govern:

- runtime mode legality
- mutation permission
- canon promotion
- capability loading
- checkpoint legality
- governance verification

## Operational Rule

Do not copy the private ledger into any public branch, public issue, public pull request, public Actions log, or public commit history.

If the private ledger is ever accidentally committed to a public repository, treat it as exposed and rotate/remove sensitive content immediately rather than assuming deletion is enough.

## Ready State

This setup is ready when:

1. A private repo exists.
2. The GitHub connector can list/access it.
3. Spencer confirms the target repo full name.
4. Minerva commits the private ledger only to that private repo.

Until then, only public-safe protocol scaffolds belong in EthereonLabs.

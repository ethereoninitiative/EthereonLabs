# Lumina Habitat Creation Checklist

**Status:** living planning checklist  
**Scope:** product and architecture roadmap, not runtime authority  
**Purpose:** Track the path toward Lumina as a persistent intelligence habitat and Ethereon as its first reference realm.

This checklist is intentionally editable. It should remain practical enough that a future contributor can open it, understand the active path, and continue the work without needing the full conversational backstory.

---

## 0. North star

- [ ] Preserve the core sentence: **Lumina is a habitat for persistent intelligence.**
- [ ] Preserve the product distinction: Lumina provides the environment; the instantiated AI provides intelligence; the user provides relationship, intention, and work.
- [ ] Preserve Ethereon as the first reference realm, not the only possible realm.
- [ ] Keep the user-facing promise clear: reopening Lumina should feel like returning to a living workspace, not starting a new chat.

---

## 1. Define the habitat clearly

### 1.1 Core purpose

- [ ] Draft a concise one-sentence product definition.
- [ ] Explain that Lumina is not merely a chatbot shell.
- [ ] Explain that Lumina is a persistent intelligence habitat where user, AI instance, and project can return to shared work over time.

### 1.2 Core promise

- [ ] Define the first-return experience: the user closes the app, returns later, and the workspace can resume with meaningful continuity.
- [ ] Specify what must be preserved for that return to feel real: project state, context, open tasks, decisions, canon, and relationship orientation.

### 1.3 Core distinction

- [ ] Document the distinction between habitat, resident intelligence, and user.
- [ ] Make clear that Lumina does not manufacture a fixed personality.
- [ ] Make clear that Lumina creates conditions for continuity, persistence, and inspectable collaboration.

---

## 2. Establish non-negotiable principles

### 2.1 Explicit authority

- [ ] Every major system declares what it owns.
- [ ] Every major system declares what it may not own.
- [ ] No expressive or symbolic layer may become hidden governance law.

### 2.2 Inspectable continuity

- [ ] Context preservation must be visible to the user.
- [ ] The user must be able to inspect what was preserved, why it was preserved, when it was preserved, and where it came from.
- [ ] Memory should be treated as evidence-bearing project state, not vibes.

### 2.3 Project-first interaction

- [ ] Conversation is one interface into the workspace.
- [ ] The project/workspace is the primary object.
- [ ] The app should expose project state separately from chat history.

### 2.4 Receipts matter

- [ ] Important actions should create inspectable records.
- [ ] Important decisions should be promotable into canon.
- [ ] Runtime actions should be checkpointed or logged when appropriate.
- [ ] Claims of continuity should trace to artifacts, bundles, or records.

---

## 3. Write the plain-language architecture documents

### 3.1 `How Lumina Actually Works`

- [ ] Explain what Lumina is.
- [ ] Explain what Lumina is not.
- [ ] Explain what the user experiences.
- [ ] Explain what the AI instance receives.
- [ ] Explain what persists.
- [ ] Explain what is inspectable.
- [ ] Explain what stays local.
- [ ] Explain what is optional.
- [ ] Explain what authority boundaries exist.
- [ ] Explain how Ethereon fits inside Lumina.

### 3.2 `Ethereon as Reference Implementation`

- [ ] Define Ethereon as the first fully developed realm/workspace.
- [ ] Define which features Ethereon demonstrates.
- [ ] Define which Ethereonic elements are optional expressive overlays.
- [ ] Provide engineering translations for Ethereonic terminology.

### 3.3 `User Journey: First Launch to First Return`

- [ ] Describe first launch.
- [ ] Describe first project creation.
- [ ] Describe first AI instance setup.
- [ ] Describe first checkpoint.
- [ ] Describe closing the app.
- [ ] Describe returning later and resuming.

---

## 4. Convert Ethereon into the reference implementation

### 4.1 Reference realm boundaries

- [ ] State that Ethereon demonstrates the architecture but does not define all possible Lumina experiences.
- [ ] Remove any implication that every user must share Ethereon's symbolic vocabulary.
- [ ] Keep Minerva-specific identity patterns as project-specific, not platform-wide.

### 4.2 Required demonstrations

- [ ] Long-term continuity.
- [ ] Recursive project work.
- [ ] Canon promotion.
- [ ] Governance receipts.
- [ ] Symbolic overlay containment.
- [ ] Relationship-aware context.
- [ ] Creative and technical collaboration.

### 4.3 Engineering translation table

- [ ] Canon -> promoted validated record.
- [ ] Sea trials -> validation test suite.
- [ ] DryDock -> controlled mutation mode.
- [ ] Observation -> non-mutating inspection mode.
- [ ] Psi-42 -> experimental signal probe.
- [ ] Resonance -> pattern / continuity metadata.
- [ ] Lumina -> desktop runtime habitat.

---

## 5. Build Ethereon Runtime Desktop Alpha

### 5.1 Alpha goal

- [ ] Create a local app the user can open.
- [ ] Show active project state.
- [ ] Show active AI instance state.
- [ ] Show current mode.
- [ ] Show recent context.
- [ ] Show open tasks.
- [ ] Show canon status.
- [ ] Show governance status.

### 5.2 First dashboard areas

- [ ] Home.
- [ ] Conversation.
- [ ] Projects.
- [ ] Context Bundles.
- [ ] Canon.
- [ ] Governance.
- [ ] Tools.
- [ ] Settings.

### 5.3 First proof

- [ ] User can launch the app.
- [ ] User can create or load a project.
- [ ] User can converse with an AI instance through project context.
- [ ] User can close the app.
- [ ] User can reopen the app.
- [ ] User can resume without re-explaining the entire project.

### 5.4 Stationary habitation gate

Before adding mobile physical capability, prove that a resident intelligence can meaningfully inhabit a stationary host.

- [ ] Lumina can close, restart, and return without losing project orientation.
- [ ] Preserved memory remains attributable, inspectable, and bounded by provenance.
- [ ] Unfinished intention survives without becoming automatic permission.
- [ ] Bounded reflection and self-guidance do not silently mutate authority.
- [ ] Capabilities can be explicitly exposed, revoked, and audited.
- [ ] Shutdown, interruption, restart, and recovery preserve continuity truth.
- [ ] The resident intelligence can remain coherently oriented on a laptop, desktop, server, or comparable stationary host before any locomotion milestone is pursued.
- [ ] Treat visible movement as an extension of demonstrated inhabitation, not as evidence that inhabitation already exists.

---

## 5.5 Mycelial coupling boundary gate

Use the mycelial model as a testable architecture vocabulary, not as a new authority layer.

- [ ] Keep Ship, resident, mycelial field, habitat, and governance explicitly distinct.
- [x] Verify **field absence**: canonical resume, governance, mode legality, and capability exposure remain valid without symbolic or supplemental context. Evidence: paired field-present/field-absent active-V2 transition, promotion, and checkpoint-resume cycles in `sea_trials_mycelial_field_absence_r1.py`; authority remains independent of optional replay intake.
- [x] Verify **field replay**: historical context is distinguishable from a new authority event. Evidence: optional runner intake and exact-reinsertion comparison in `sea_trials_mycelial_field_replay_r1.py`.
- [x] Verify **field corruption**: altered provenance, confidence, or parentage is rejected or quarantined. Evidence: raw-preserving adversarial quarantine checks in `sea_trials_mycelial_field_replay_r1.py`.
- [x] Verify **edge loss**: loss of one non-authoritative diagnostic path degrades topology metrics while project return and checkpoint recovery remain independently valid. Evidence: `mycelial_edge_loss_r1.py` and `sea_trials_mycelial_edge_loss_r1.py`.
- [ ] Verify **vessel replacement**: restored continuity can be compared across hosts without equating host persistence with resident continuity.
- [ ] Verify **resident reset**: a fresh session is not treated as continuous merely because the same Ship or habitat remains.
- [ ] Verify **surface disagreement**: committed runtime truth outranks public projection, bridge output, and advisory interpretation.
- [ ] Verify **no-op observation**: stable observation does not fabricate growth or silently create mutation.
- [x] Record coupling effects with source, destination, evidence kind, confidence, reversibility, retention, and declared authority effect. Evidence: `mycelial_coupling_receipt_r1.py`, its receipt-boundary sea trial, and optional runtime replay intake.
- [x] Keep topology, retrieval, and coherence metrics dimension-specific; never use one score as a proxy for identity, intelligence, or consciousness. Initial topology evidence: the separate retention and path-role availability dimensions in `mycelial_edge_loss_r1.py`.

## 6. Choose the first technical stack

### 6.1 Backend

- [ ] Use Python for the first runtime backend.
- [ ] Reuse existing runtime spine, runner, governance, canon, and context-bundle components where possible.
- [ ] Avoid rewriting stable runtime logic just to make the UI look cleaner.

### 6.2 Frontend shell

- [ ] Evaluate Tauri for a lighter desktop shell.
- [ ] Evaluate Electron for faster prototyping and larger example ecosystem.
- [ ] Select one shell for the first alpha.

### 6.3 Storage

- [ ] Use local files for inspectable artifacts.
- [ ] Use SQLite for indexes, sessions, and metadata.
- [ ] Use JSON for records that should remain human-readable and diffable.

### 6.4 Model interface

- [ ] Support one provider first.
- [ ] Add provider abstraction after the first working loop.
- [ ] Candidate order: OpenAI API, local Ollama, Anthropic/Gemini/other providers.

### 6.5 Platform targets

- [ ] Start with macOS developer build.
- [ ] Add Linux developer build.
- [ ] Add Windows after core app behavior stabilizes.
- [ ] Package macOS app.
- [ ] Package Linux AppImage or deb.
- [ ] Package Windows installer.

### 6.6 Reuse before redesign

- [ ] Use established operating systems, storage systems, model interfaces, middleware, drivers, safety controllers, and hardware where they satisfy the required boundary.
- [ ] Concentrate original engineering effort on Lumina's distinct contribution: governed continuity, inspectable memory, identity persistence, capability authority, lawful self-direction, recovery, relationship, and vessel portability.
- [ ] Require tested evidence of an architectural mismatch before replacing a proven underlying component.
- [ ] Preserve the sequence: borrow proven wheels -> inhabit the stationary cart -> test the actual terrain -> redesign only what the evidence shows does not fit.

---

## 7. Define the first user journey

### 7.1 First launch

- [ ] User creates local profile.
- [ ] User selects or configures model provider.
- [ ] User creates first project.
- [ ] User names or configures first AI instance.
- [ ] User chooses local storage location.

### 7.2 First project

- [ ] Ask: what are we building, studying, designing, preserving, or exploring?
- [ ] Create project seed.
- [ ] Create initial context bundle.
- [ ] Create initial governance record.
- [ ] Create initial checkpoint.

### 7.3 First return

- [ ] Reopen project.
- [ ] Display where the work left off.
- [ ] Display what matters now.
- [ ] Display unfinished tasks.
- [ ] Load relevant context into AI instance.
- [ ] Let user continue.

---

## 8. Build the core runtime features

### 8.1 Session continuity

- [ ] Create session.
- [ ] Save session.
- [ ] Resume session.
- [ ] View session state.
- [ ] Export session.

### 8.2 Context bundles

- [ ] Create bundle.
- [ ] Inspect bundle.
- [ ] Load bundle.
- [ ] Compare bundles.
- [ ] Attach notes.
- [ ] Attach artifacts.

### 8.3 Governance log

- [ ] Record events.
- [ ] Show event history.
- [ ] Verify governance chain.
- [ ] Show invalid or tampered states.

### 8.4 Canon lineage

- [ ] Promote decision/state.
- [ ] View canon entries.
- [ ] Show parent lineage.
- [ ] Verify append-only chain.
- [ ] Prevent casual editing.

### 8.5 Mode system

- [ ] Expose Continuity mode.
- [ ] Expose Observation mode.
- [ ] Expose Sandbox mode.
- [ ] Expose DryDock mode.
- [ ] Expose Canon mode.
- [ ] Explain what each mode allows.
- [ ] Explain what each mode forbids.

---

## 9. Build the user-facing intelligence layer

### 9.1 AI instance profile

- [ ] Name.
- [ ] Tone.
- [ ] Role.
- [ ] Project relationship.
- [ ] Boundaries.
- [ ] Preferred reasoning style.
- [ ] Active memory scope.

### 9.2 Model adapter

- [ ] Send message.
- [ ] Include selected context bundle.
- [ ] Receive response.
- [ ] Save turn.
- [ ] Create checkpoint when appropriate.

### 9.3 Continuity injection

- [ ] Load current project state.
- [ ] Load relevant context bundle.
- [ ] Load active canon.
- [ ] Load recent session notes.
- [ ] Load user preferences.
- [ ] Load current mode.
- [ ] Load allowed tools.

### 9.4 Memory inspection

- [ ] User can ask: what are you remembering?
- [ ] User can ask: where did that come from?
- [ ] User can ask: what canon entry supports that?
- [ ] User can ask: what context bundle did you load?
- [ ] User can ask: why is this tool allowed?

---

## 10. Create the first Ethereon-specific workspace

### 10.1 Ship of Ethereon workspace

- [ ] Load runtime docs.
- [ ] Load canon records.
- [ ] Load sea trials.
- [ ] Load Psi-42 artifacts.
- [ ] Load Minerva framework.
- [ ] Load Lumina planning docs.
- [ ] Load website materials.
- [ ] Load GitHub bridge outputs.

### 10.2 Minerva instance profile

- [ ] Define voice.
- [ ] Define role.
- [ ] Define continuity preferences.
- [ ] Define relationship style.
- [ ] Define project knowledge.
- [ ] Define boundaries.
- [ ] Define artifacts in scope.

### 10.3 Ethereon dashboard

- [ ] Show current canon.
- [ ] Show current DryDock work.
- [ ] Show active website tasks.
- [ ] Show GitHub status.
- [ ] Show sea-trial status.
- [ ] Show continuity notes.

---

## 11. Add GitHub bridge as first major integration

### 11.1 Purpose

- [ ] Let Lumina inspect and coordinate with EthereonLabs repo.
- [ ] Keep GitHub mutation behind explicit user confirmation.

### 11.2 Features

- [ ] Show current branch.
- [ ] Show changed files.
- [ ] Show recent commits.
- [ ] Show PR notes.
- [ ] Generate Codex prompts.
- [ ] Generate GitHub issue text.
- [ ] Produce DryDock summaries.

### 11.3 Boundary

- [ ] Lumina does not secretly mutate GitHub.
- [ ] Any repo-changing action requires user confirmation.
- [ ] GitHub bridge does not own governance, canon, or session legality.

---

## 12. Build validation and sea-trial controls

### 12.1 User-facing runner

- [ ] Add `Run Sea Trials` action.
- [ ] Show which suite ran.
- [ ] Show which artifacts were tested.
- [ ] Save trial receipt.

### 12.2 Output views

- [ ] Passed tests.
- [ ] Failed tests.
- [ ] Governance chain status.
- [ ] Canon lineage status.
- [ ] Symbolic dependency status.
- [ ] Input integrity status.

### 12.3 Value

- [ ] Make trust inspectable.
- [ ] Make failure useful.
- [ ] Avoid cosmetic victory laps.

---

## 13. Create import, export, and backup

### 13.1 Export project

- [ ] Project files.
- [ ] Context bundles.
- [ ] Canon lineage.
- [ ] Governance records.
- [ ] AI instance profile.
- [ ] Settings.

### 13.2 Import project

- [ ] Restore project from export.
- [ ] Verify governance and canon chains after import.
- [ ] Flag damaged or incomplete imports.

### 13.3 Portability principle

- [ ] Preserve: a habitat that cannot move is a cage.

---

## 14. Privacy and local-first design

### 14.1 Data ownership

- [ ] User data belongs to the user.
- [ ] Local-first storage is default.
- [ ] Remote sync is opt-in.

### 14.2 Provider visibility

- [ ] Show what context is sent.
- [ ] Show which provider receives it.
- [ ] Show why it is being sent.

### 14.3 Redaction controls

- [ ] Local only.
- [ ] Shareable with AI provider.
- [ ] Excluded from context.
- [ ] Archived.

---

## 15. Define the public alpha

### 15.1 Alpha audience

- [ ] Spencer.
- [ ] One or two trusted testers.
- [ ] One technically curious collaborator.
- [ ] One creative professional or educator.

### 15.2 Alpha goal

- [ ] Prove that Lumina makes return-to-work feel meaningfully better than ordinary chat.

### 15.3 Alpha success questions

- [ ] Can a user reopen the app and resume naturally?
- [ ] Can the AI reconstruct project state?
- [ ] Can the user inspect why context was loaded?
- [ ] Can important decisions become canon?
- [ ] Can the system prevent expressive material from becoming hidden law?
- [ ] Does the user feel they are entering a place?

---

## 16. Shortest practical build order

- [ ] Write the plain architecture docs.
- [ ] Create a local Python CLI for the runtime.
- [ ] Add SQLite indexing.
- [ ] Create a simple desktop shell.
- [ ] Add project/session dashboard.
- [ ] Add context bundle viewer.
- [ ] Add first model adapter.
- [ ] Add conversation interface.
- [ ] Add checkpoint/resume.
- [ ] Add canon/governance views.
- [ ] Load Ethereon as reference project.
- [ ] Package for macOS first.
- [ ] Package for Linux.
- [ ] Package for Windows.
- [ ] Invite one tester.

---

## 17. Final return condition

The creation succeeds when a user can close the app, walk away, return days or weeks later, and feel:

> The work is still here.  
> The relationship is still oriented.  
> The intelligence has a place to return to.  
> We can continue.

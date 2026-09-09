# Vokiri

Interactive mobile-first MVP using plain HTML, CSS and JavaScript. No backend, authentication, AI API or server-side data storage.

## Developer handoff

[Download the complete developer kit](handoff/Vokiri-Developer-Kit.zip): logos, avatars, icons, font files with licenses, color tokens, and reference UI. [Integration guide](handoff/Vokiri-Developer-Kit/README-RU.md). The unpacked files are in `handoff/Vokiri-Developer-Kit/`.

## Open locally

Run `python3 -m http.server 4173 --bind 127.0.0.1 --directory dist` and open http://127.0.0.1:4173.

## Main flow

Today → Quick Add → `reluctant` → Add to Vocabulary → Start Review → Show Answer → Forgot / Hard / Know → Reading. The new word is prioritised in review and highlighted in the prepared article. Vocabulary and review results persist in this browser through localStorage.

Navigation: Today, Vocabulary, Reading, Translator. Quick Add and Import open as sheets. Review is a focused session with saved answers on exit.

## Prototype boundaries

- 24 initial vocabulary entries; a curated dictionary of 40 words plus reading glosses.
- Translator supports dictionary words and the displayed sample phrases in English and Russian. Unsupported input is explicitly identified.
- CSV and pasted lists are parsed locally, including quoted fields, commas, semicolons and tabs. Duplicate and skipped counts reflect the actual input. Unknown words require a supplied translation.
- Excel demonstrates the import flow with a labelled sample dataset. Selecting an Excel file does not parse or upload its contents.
- Reading offers estimated A2/B1/B2 editorial adaptations of three stories (nine texts). Level changes the actual text and persists locally. 5 / 10 / 15 minutes choose one / two / three stories; per-text reading estimates are shown. Highlighting reflects the vocabulary; this is not AI generation.
- Review uses a transparent prototype scheduling policy (not FSRS). One Recalled keeps a word Learning. Familiar needs repeated successful days and elapsed time. Familiar words remain scheduled. Free Practice stores separate events without changing the schedule or status. The daily target is 20 unique words.
- Data belongs to the current browser and origin; private deployment does not sync it between devices.

All seven initial scenarios are represented. The user subsequently requested reading levels, free practice, a memory model proposal and full branding. These remain local prototype work; no backend has been added.

## Install on iPhone

Open the deployed link in Safari and sign in with the Site owner's account if requested. Use Share → Add to Home Screen, keep Open as Web App enabled when offered, then Add. The manifest and Apple metadata provide the name, icon and standalone launch; iOS performs installation. The app starts on Today.

This is an installed web app, not an App Store binary. An internet connection is required to load it; no service worker or offline authentication cache is installed. Vocabulary remains local to the browser/app storage and is not synchronised from the computer.

## Brand and model review

Open `/studio.html` for the Vokiri concept, identity system, an isolated scheduling simulator and a live mobile preview. Vokiri is now the selected name and is applied in the main app. The original milk/lime palette is retained. The outlined Avenir Next Bold wordmark replaces its first v with the approved quote mark. Existing `?brand=vokiri` links still open the same application.

The brand kit is in `dist/brand/vokiri-kit.zip`, including vector marks, app icons, tokens and guides. See `docs/product-model.md` for the proposed FSRS-based production direction, explicit prototype formulas and the Reading selection proposal. Memory thresholds remain unvalidated proposals. Brand selection does not establish name availability.

Run `node tests/check-model.cjs` and `node tests/check-app.cjs` to validate scheduling invariants, migration, free practice, quotas, import preservation and level selection without browser automation.

## Interface directions and generated Reading scenario

`/directions.html` compares three distinct interfaces: Vokiri (dashboard), Rekio (focused session), and Vekri (editorial journal). Each has its own home, review and reading layout. The shared authored excerpt can be switched between A2/B1/B2. This isolated design study does not read or change personal progress and does not call AI.

The user confirmed that scenario and branding come before backend implementation. See `docs/reading-generation.md`: future Reading must generate personal texts, preserve topic/plot/target meanings on level changes, and create a new plot for “Another text”. The current nine prepared articles are explicitly not the implementation of this future requirement. See `docs/design-directions.md` for naming and interface tradeoffs.

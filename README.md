# English Hub

Interactive mobile-first MVP using plain HTML, CSS and JavaScript. No backend, authentication, AI API or server-side data storage.

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
- Reading uses three prepared stories. 5 / 10 / 15 minutes choose one / two / three stories, starting with the selected topic. Highlighting reflects the current vocabulary; this is not AI generation.
- Review is a simple daily local queue, not a spaced-repetition engine. Forgot → Weak, Hard → Learning, Know → Learned.
- Data belongs to the current browser and origin; private deployment does not sync it between devices.

All seven requested MVP scenarios are represented. No excluded features have been added.

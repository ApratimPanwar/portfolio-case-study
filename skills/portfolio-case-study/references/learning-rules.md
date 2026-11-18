# LEARN — extracting house rules from an existing portfolio

Goal: a rules file specific enough that two different runs on the same project
produce nearly the same case study. "Clean, minimal, professional" is not a rule.
"Title is `<Deliverable> for <Client>`, no trailing punctuation" is.

## 1. Collect the sample

- Read **every** existing case study, not one. Rules come from repetition; one
  example only gives you a layout.
- From a live URL: use the browser tools. `get_page_text` for copy, `read_page`
  for structure, and run JS in the page to dump the DOM of one project block —
  the markup is the real spec on hosted builders.
- Save what you read (copy + one block of markup) to a scratch file so the
  numbers below are counted, not estimated.

## 2. Measure structure

Per case study, record:

| What | Example |
|---|---|
| Container / layout | 9-col media + 3-col text; full-width hero then two-col |
| Order of elements | index letter → rule → title → body → link |
| Image count & mix | 10 images, 1 autoplay loop, 2 wide |
| Grid | 3-column masonry, wide shots span 2 |
| Word count | count it |
| Paragraph count | count it |
| Headings inside body | none / "Challenge · Approach · Outcome" |
| Trailing elements | link with `->`, credits line, year, tags |
| Navigation / index scheme | letters, numbers, titles, years |

Then find the **mode** across all samples — what most of them do. That is the
rule. Record the range (min–max) beside it.

## 3. Read the voice

Collect evidence, quote it:

- Person: first (I/we), third, or impersonal/passive?
- Tense: past, present?
- Sentence length: short and punchy, or long and academic?
- Opening move: client? problem? outcome? context-setting?
- Vocabulary: technical, plain, playful? Recurring words?
- Does it name decisions *and reasons*, or list deliverables?
- Does it mention rejected directions?

Write the voice rule as **do / don't with real quotes** from the site.

## 4. Separate rules from accidents

Every deviation goes in one of three buckets:

- **Rule** — most case studies do it. Encode it.
- **Variant** — a deliberate alternate (e.g. series work gets an Instagram link
  instead of a PDF). Encode it with the condition.
- **Accident** — typo, one-off, truncated copy, outdated year. List it under
  "Observed issues", do NOT encode it.

When unsure, it is a question for the user, not a guess.

## 5. Quality check on the voice itself

If the existing copy is weak (passive, generic adjectives, no reasons, could be
pasted into any other project), say so and show one paragraph rewritten.
Then ask: **codify as-is, or codify the improved voice?** It is the user's
portfolio; it is their call. Record the answer in the rules file.

## 6. Pick a reference example

Choose the strongest existing case study (or the rewritten one) as the worked
example in `house-rules.md`. Future runs imitate the example more reliably than
they follow abstract rules.

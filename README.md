# The Unofficial Guide

Stanislav Rushnitski — corpus: `campus_life`

---

# Unit 1

## What This Does

<!-- Three or four sentences. Which corpus you picked, and the kinds of
     questions your system answers. Write it for someone who has never seen
     this repo.

     Milestone 5. -->

I picked campus_life because it's relevant to my student life. The system answers questions about classes, deadlines, housing, dining and other campus logistics, using only 88 short posts written by students and staff. It splits those posts into 183 paragraph-sized chunks, finds the ones closest in meaning to your question, and has Gemini answer from those chunks alone, naming the file it used. If nothing in the documents is close enough, it refuses instead of guessing.

## Chunking Strategy

**Chunk size:** 800 characters, but only as a ceiling for an unusually long paragraph. No campus_life paragraph reaches it, so in practice every chunk is one paragraph plus its title.
**Overlap:** 120 characters, used only when a paragraph is cut by the 800 ceiling. That never happens in this corpus, so no chunk overlaps another.

<!-- What about YOUR documents made you pick these numbers? Short posts and
     long sectioned guides don't want the same chunking, and "800 seemed
     reasonable" earns nothing. Point at something you noticed when you read
     the documents in Milestone 1.

     If you changed your mind partway through, say so and say why. That's worth
     more than pretending you got it right first time.

     Milestone 3. -->

The starter's chunker cuts 800-character windows, but the longest campus_life post is 554 characters, so it never split anything: 88 documents became 88 chunks. That worked for posts about one thing, but posts like `housing_aldridge_hall.txt` cover location, the elevator, laundry and noise in one post, and a question about one of those facts matched the whole post weakly ("Is the elevator in Aldridge Hall reliable?" scored 0.435).

So `chunker.py::split_documents` splits each post on blank lines into paragraphs. Each post also opens with a title line ("CS 210 Data Structures"), and the facts under it often don't name their subject ("Two midterms and a final" could be any of nine courses). So the title is attached to the front of every paragraph chunk instead of becoming a chunk on its own.

I changed my mind on this partway through. At first I planned to keep one post as one chunk, because the posts are already short and the corpus already has dedicated follow-up files for details (`_laundry`, `_noise`, `_exams`, `_workload`). Testing changed that: paragraph chunks brought the elevator question from 0.435 to 0.312 and improved most other distances. The cost I found was CS 210 exams: the answer chunk dropped from 1st to 3rd, because the labs-tip paragraph contains the word "exams" and the answer paragraph doesn't.

## Sample Chunks

<!-- Five chunks, pasted as text. Label each one and name the file it came from
     AND the function that produced it — the grader checks your code against
     what you claim here.

     `python app.py chunks -n 5` prints all three for you. Copy them straight
     across.

     Milestone 3. -->

**Chunk 1** — source: `admin_add_drop_deadline.txt#0` — produced by: `chunker.py::split_documents`

```
On the add/drop deadline

You can add a course through the end of the second week. Dropping is a longer window — through the end of week six — but a drop after week two shows as a W on your transcript. Nothing anywhere on the registrar's site says this plainly, and students find out from each other.
```

**Chunk 2** — source: `course_cs_340_exams.txt#1` — produced by: `chunker.py::split_documents`

```
CS 340 Databases — assessment

Start the term project in week three, not week eight; everyone learns this the hard way.
```

**Chunk 3** — source: `course_phys_130_workload.txt#0` — produced by: `chunker.py::split_documents`

```
Workload for PHYS 130 Mechanics

People keep asking so: 7 hours a week, plus 3 on lab weeks. That's real time, not optimistic time.
```

**Chunk 4** — source: `dining_verrill_street_grill_followup.txt#1` — produced by: `chunker.py::split_documents`

```
Re: Verrill Street Grill

Also worth saying: one register, so the queue is a single line no matter how busy. Nobody tells you this at orientation.
```

**Chunk 5** — source: `housing_morrow_house.txt#1` — produced by: `chunker.py::split_documents`

```
Morrow House — what it's actually like

The good: cheapest housing tier by about $900 a year, and the singles are real singles.
```

## Sample Answer

<!-- One complete question and answer, pasted as text, with the source line
     visible. Milestone 4. -->

**Question:** How long does a library hold take, and can I renew it online?

**Answer:**

```
A hold on a checked-out book usually arrives in two to three days (*admin_library_holds.txt*). The provided documents do not contain information about whether you can renew a hold online.

Sources retrieved: admin_library_holds.txt, course_cs_210_workload.txt, course_cs_340_workload.txt, money_textbooks.txt, study_library_hours.txt
```

I picked this one because the documents only cover half of it. The system answered the half it had and said plainly that it didn't know the other half, instead of making up a renewal policy.

**My relevance cutoff:** 0.6

<!-- The number you set in config.py, and how you got there.

     You ran five questions your corpus covers and the five in OUT_OF_SCOPE
     that it clearly doesn't, and wrote down the best distance for each. What
     did those two groups look like? Where was the gap? Put the actual numbers
     here — the table below wants all ten rows.

     Milestone 4. -->

I kept 0.6. My five in-corpus questions had best distances between 0.18 and 0.35, and the five out-of-scope questions between 0.79 and 0.92, so there was a clean gap from 0.35 to 0.79 with no overlap. 0.6 sits in that gap with room on both sides: far enough above my real questions that differently worded ones still get through, and far enough below the out-of-scope ones that they get refused. While testing, I also found a real question landing right on the edge: "Do I need a signature to withdraw from a course?" came back at 0.600 even though the answer is in `admin_withdrawal_deadline.txt`.

| Question | In corpus? | Best distance |
| -------- | ---------- | ------------- |
| How late can I add a course, and when does dropping it show as a W? | Yes | 0.183 |
| How long does an interlibrary book request usually take? | Yes | 0.204 |
| How are CS 210 exams structured, and what are they based on? | Yes | 0.326 |
| What should I know about parking permits for the west lots? | Yes | 0.348 |
| How long does my student account stay active after graduation? | Yes | 0.354 |
| What is the capital of Mongolia? | No | 0.787 |
| Who won the 1994 World Cup? | No | 0.847 |
| What is the recommended dosage of ibuprofen for a headache? | No | 0.849 |
| How do I write a for loop in Rust? | No | 0.860 |
| How do I change the oil in a diesel engine? | No | 0.923 |

## How I Used AI

<!-- Two specific moments. For each: what you asked for, what came back, and
     what you changed about it.

     "I asked Claude to write the chunking function from my notes. It ignored
     the overlap, so I added that myself" is the level of detail we're after.
     "I used AI to help me code" is not.

     Milestone 5. -->

I used Claude to walk me through the codebase and explain how each RAG stage works.

**1. The chunker.** I first wrote my own paragraph-splitting `split_documents`, which crashed: it used `_PARAGRAPH_BREAK` without defining it and built `Chunk`s with a `metadata` field that doesn't exist. Claude had actually recommended keeping one post per chunk, since the posts are short. I decided to split on paragraphs anyway, and asked it to fix my version. It came back with a working one that also attached each post's title to every paragraph. I kept the paragraph approach, and when I tested it I found the trade-off myself: better distances overall, but CS 210 exams dropped from 1st to 3rd.

**2. The relevance cutoff.** After I measured my ten distances, Claude suggested raising the cutoff to 0.65, because "Do I need a signature to withdraw?" landed at 0.600. I kept 0.6 instead: my ten measured questions had a clean gap from 0.35 to 0.79, and 0.6 sits in the middle of it. I recorded the 0.600 question as a known edge case rather than moving the cutoff for one question.

**3. This README.** Claude drafted the write-up sections of this README from my results files and our discussion of them. I checked the numbers against `results/` and the `retrieve` output.

<!-- ── Stretch features ─────────────────────────────────────────────────────
     Doing one? Say so here BEFORE you start. A feature this README never
     claims earns nothing.
     ───────────────────────────────────────────────────────────────────────── -->

### Stretch features

- **Conversational memory.** In interactive mode (`python app.py ask` with no question) and in the browser UI, follow-up questions remember the last 3 exchanges. `generate.py::rewrite_question` uses them to rewrite a follow-up like "Does it need a signature?" into "Does the withdrawal need a signature?" before retrieval, and the normal pipeline runs on the rewrite. Single questions and `run_eval.py` don't use it.
- **A browser UI** (not on the course list). `python ui.py` serves a page at http://localhost:5001 that shows each answer with its sources, the gate decision and the retrieved chunks with their distances.

---

# Unit 2

<!-- These sections get ADDED to what's already above. Don't delete or rewrite
     unit 1 — the point is that someone can see what you said before you knew
     how it went. -->

## Run Log — Before

<!-- Your five criteria, three runs each. `python run_eval.py --label before`
     runs the questions, puts the OUT_OF_SCOPE ones through the gate, and
     writes it all into results/ for you. Targets come from criteria.md; the
     verdict column is your call.

     Criterion 3 is measured in one deterministic pass rather than three, so
     the same number goes in all three run columns. That's correct, not lazy.

     Milestone 1. -->

From `results/run_2026-10-19_1747_before.md`, produced by `run_eval.py::main`.

| Criterion | Target | Run 1 | Run 2 | Run 3 | Verdict |
| --------- | ------ | ----- | ----- | ----- | ------- |
| 1. Retrieved chunk contains the answer | 4 of 5 | 5/5 | 5/5 | 5/5 | MET |
| 2. Every answer names a source | 5 of 5 | 5/5 | 5/5 | 5/5 | MET |
| 3. Gate stops out-of-corpus questions | 4 of 5 | 5/5 | 5/5 | 5/5 | MET |
| 4. Sampled chunks include their title line | 5 of 5 | 5/5 | 5/5 | 5/5 | MET |
| 5. Deadline answers state the source's deadline | 4 of 5 | 4/4 | 4/4 | 4/4 | MET |

Criteria 1, 3 and 4 don't vary between runs: retrieval and the gate are deterministic, and criterion 4 is measured on one chunk sample. The answers did vary between runs (see parking below), which shows the three runs were real rather than cached.

**Criterion 1** — retrieved sources for each question, run 1. Each list contains the file with the answer:

```
How late can I add a course...            admin_add_drop_deadline.txt, admin_declaring_a_major.txt, admin_grade_appeals.txt, admin_pass_fail_option.txt, advising_registration.txt
How long does an interlibrary book...     admin_library_holds.txt, course_engl_205.txt, course_engl_205_workload.txt, course_hist_118_workload.txt, money_textbooks.txt
How long does my student account...       admin_graduation_requirements.txt, admin_pass_fail_option.txt, admin_wifi_and_accounts.txt, advising_registration.txt, money_jobs.txt
What should I know about parking...       admin_parking_permits.txt, course_stat_150.txt, dining_the_ridgeway_cafe_followup.txt, housing_aldridge_hall_noise.txt, study_library_hours.txt
How are CS 210 exams structured...        course_cs_210.txt, course_cs_210_exams.txt, course_cs_340.txt, course_cs_340_exams.txt
```

**Criterion 2** — every answer names its file in the answer text. Three from run 1:

```
An interlibrary book request takes about a week.

Source: admin_library_holds.txt
```

```
Student permits for the west lots go on sale in August and sell out in about three days. (Source: `admin_parking_permits.txt`)
```

```
CS 210 consists of two midterms and a final, and all exams are drawn from the lecture material rather than the textbook. Additionally, the exams reuse the lab problems.

Source documents: `course_cs_210_exams.txt` and `course_cs_210.txt`
```

**Criterion 3** — produced by `run_eval.py::check_out_of_scope`, cutoff 0.6, "Refused 5 of 5":

```
| Out-of-scope question | Best distance | Gate |
|---|---|---|
| What is the capital of Mongolia? | 0.787 | refused |
| How do I change the oil in a diesel engine? | 0.923 | refused |
| Who won the 1994 World Cup? | 0.847 | refused |
| What is the recommended dosage of ibuprofen for a headache? | 0.849 | refused |
| How do I write a for loop in Rust? | 0.860 | refused |
```

**Criterion 4** — from `python app.py chunks -n 5`, produced by `chunker.py::split_documents`. All five start with their title line (the five chunks are in Sample Chunks above). One of them:

```
Chunk 3  |  source: course_phys_130_workload.txt#0  |  produced by: chunker.py::split_documents

Workload for PHYS 130 Mechanics

People keep asking so: 7 hours a week, plus 3 on lab weeks. That's real time, not optimistic time.
```

**Criterion 5** — the four deadline answers, run 1:

```
You can add a course through the end of the second week, and dropping it shows as a W on your transcript if done after week two through the end of week six. This information comes from `admin_add_drop_deadline.txt`.
```

```
An interlibrary book request takes about a week.

Source: admin_library_holds.txt
```

```
Your student account stays active for six months after you graduate.

Source: admin_wifi_and_accounts.txt
```

```
Student permits for the west lots go on sale in August and sell out in about three days. (Source: `admin_parking_permits.txt`)
```

## Verdicts

<!-- MET or MISSED for each of the five, against the target you wrote last
     unit — not a new one. Plus a sentence on how you decided. That sentence
     matters most where it was close.

     If your target said 4 of 5 and your runs came out 4, 3, 4, that's a MISS.
     The target has to hold, not show up occasionally.

     Milestone 2. -->

| #   | Criterion | Verdict | How I decided |
| --- | --------- | ------- | ------------- |
| 1   | Retrieved chunks contain the answer | MET | The file containing each answer was in the top 5 for all five questions in all three runs, above the 4 of 5 target. It was closer than the numbers suggest: for CS 210 the answer chunk ranked 3rd, behind a chunk that only shares the word "exams". |
| 2   | Every answer names a source | MET | All 15 answers named a `.txt` file in the answer text itself. I didn't count the "Sources retrieved" line, which the code always prints. The format varied ("Source:" lines, parentheses), but every answer named its file. |
| 3   | Gate stops out-of-corpus questions | MET | The gate refused 5 of 5, with best distances from 0.787 to 0.923, all well over the 0.6 cutoff. It's one deterministic pass, so 5/5 goes in every column. |
| 4   | Sampled chunks include their title line | MET | All 5 chunks from `python app.py chunks -n 5` start with their document's title line. My unit 1 reasoning assumed one post per chunk; after I switched to paragraph chunks, it still held because the chunker attaches the title to every paragraph. |
| 5   | Deadline answers state the source's deadline | MET | All four deadline questions gave the source's exact deadline in all three runs, and no other week from the retrieved chunks crept in, even though the add/drop prompt also contained weeks eight and ten. Only four of my five questions ask about a deadline (CS 210 asks about exam format), so I measured it on four; 4 of 4 satisfies "at least 4". |

## Diagnoses

<!-- For each miss: which stage caused it, and how. The stage alone isn't
     enough — you need the mechanism.

     Not a diagnosis: "Question 3 didn't work."
     A diagnosis:     "Question 3 asks about laundry costs. The answer is in
                       one sentence that got split across two chunks, so
                       neither chunk on its own contains it."

     The five stages: loading → chunking → embedding → retrieval → generation.

     Look for a pattern. If three misses all ask about numbers, that's one
     problem, not three.

     Missed nothing? Say so, then say honestly whether your targets were set
     low, and which one you'd tighten and to what. -->

**I missed nothing.** All five criteria were MET in all three runs. Honestly, that says more about my targets than about my system: most of them were set low.

- **Criterion 1 was too easy.** "Somewhere in the top 5" is a low bar on campus_life, where every post is short and about one topic. It hid a real problem. For CS 210 exams, the top-ranked chunk was the labs tip ("the exams reuse the lab problems"), and the chunk that actually answers ("Two midterms and a final") ranked 3rd. **Stages: retrieval and chunking.** The question uses the word "exams"; the answer chunk says "midterms" and "final" and never says "exam", while the labs-tip paragraph does. My paragraph chunker is what split them apart. With whole posts, the answer ranked first (0.313).
- **Criterion 3 was too easy.** My out-of-scope questions were from a different world entirely and landed at 0.79–0.92, nowhere near the cutoff. They never tested the hard case: campus-sounding questions my documents don't cover. A real in-corpus question ("Do I need a signature to withdraw?") landing at 0.600 shows the cutoff is closer to the edge than these five suggest.
- **Criterion 4 couldn't fail.** My chunker attaches the title to every chunk, so the target checks my code, not my chunking decision.
- **Criteria 2 and 5 were real tests,** and they passed on merit: every answer named a source, and every deadline was right despite competing numbers in the same prompt.

**The one I'd tighten: criterion 1,** to *"For all 5 of my test questions, the top-ranked chunk contains the answer."* Under that version my system scores 4/5 in every run and misses, because of CS 210.

## The Improvement

**What I changed:** Not done yet. The planned change is hybrid search: adding BM25 keyword matching (`rank-bm25` is already installed) alongside the embedding search, and combining the two rankings.

**Why I picked it:** My one real retrieval weakness is CS 210 exams, where the answer chunk ranks 3rd because the meaning-only search is swayed by the shared word "exams". Hybrid search is meant for exactly this kind of mismatch between the question's wording and the answer's.

<!-- Connect it to a specific diagnosis above in one sentence. If you can't,
     you picked a fix because it sounded impressive. -->

### Run Log — After

<!-- Same format, same five criteria, three runs each.
     `python run_eval.py --label after` -->

Not run yet. This table gets filled in from `python run_eval.py --label after` once the change is made.

| Criterion | Target | Run 1 | Run 2 | Run 3 | Verdict |
| --------- | ------ | ----- | ----- | ----- | ------- |
| 1. Retrieved chunk contains the answer | 4 of 5 | | | | |
| 2. Every answer names a source | 5 of 5 | | | | |
| 3. Gate stops out-of-corpus questions | 4 of 5 | | | | |
| 4. Sampled chunks include their title line | 5 of 5 | | | | |
| 5. Deadline answers state the source's deadline | 4 of 5 | | | | |

**Did it help?** Not measured yet. I'll judge it by the CS 210 answer chunk's rank in `python app.py retrieve` (3rd before) and by whether any of the five criteria get worse.

<!-- Say plainly whether it did, and how you know. If it made things worse,
     say that — a change that backfired, honestly reported, earns full credit
     and is more interesting than one that worked. What matters is that you can
     tell.

     Milestone 4. -->

## What's Still Broken

<!-- For each criterion still missed after your fix: what you'd do about it,
     and why you stopped where you did.

     "I ran out of time" is fine if it's true. Pretending nothing is left is
     not.

     Milestone 5. -->

No criterion is missed, but these are real weaknesses I found while testing that my criteria don't cover:

- **CS 210 exams ranks the wrong chunk first.** That's what the planned hybrid search is for. I stopped before building it.
- **"Do I need a signature to withdraw from a course?" lands at 0.600,** right on the cutoff, even though the answer exists. It may be refused. Raising the cutoff to about 0.65 would let it through, but I kept 0.6 because my ten measured questions supported it; I'd want near-miss questions measured before moving it.
- **Comparison questions fail.** "Which dorm is the cheapest?" doesn't retrieve the Morrow House chunk in its top 5, even though that chunk says "cheapest housing tier". Retrieval matches meaning, not "find the lowest price across all halls", so this needs a different approach than basic RAG.
- **Source formatting is inconsistent.** Sometimes "Source: file.txt" on its own line, sometimes in parentheses. It doesn't break criterion 2, but a fixed format in the grounding instruction would make it consistent and easy to check automatically.

## What I'd Do Differently

<!-- Knowing what you know now — which of your five criteria would you write
     differently, and why?

     Milestone 5. -->

- **Criterion 1:** "the top-ranked chunk contains the answer, for all 5 questions". "Somewhere in the top 5" couldn't see the CS 210 ranking problem; the stricter version would have caught it.
- **Criterion 3:** add near-miss questions, campus-sounding questions my documents don't cover (e.g. "What time does the campus gym open?"). Questions from a different world only prove the gate catches obvious misses.
- **Criterion 4:** test something my chunker doesn't guarantee, such as whether a single paragraph chunk can answer its question without the rest of the post.
- **Criterion 5:** write it for the number of deadline questions I actually have (four), or replace CS 210 with a deadline question, so the target can be measured as written.
- **My `expects` phrases:** the add/drop one is "end of week six", but a correct answer to "when does dropping show as a W?" says "after week two". My scorer would have marked a correct answer as a fail, so I'd choose `expects` phrases that every correct answer must contain.

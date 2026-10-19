# Acceptance criteria — The Unofficial Guide

Five criteria that say what "working" means for this system, written in unit 1
**before** any results existed.

An acceptance criterion names a target: a number, a count, a rate, or something
a person could plainly observe. _"Retrieval works"_ is an opinion. _"For at
least 4 of my 5 test questions, the top results include a chunk containing the
answer"_ is a criterion.

Under each one, write a sentence or two on **why that target** and not a
stricter or looser one. A reason that says something about your corpus or your
pipeline earns credit; _"80% seemed reasonable"_ does not.

> Missing your own targets next unit costs you nothing. Setting a target so
> easy you can't miss it does.

---

## 1. Retrieved chunks contain the answer

For at least 4 of my 5 test questions, the retrieved chunks include one that
contains the answer.

**Why this target:**
campus_life documents are short, single-topic posts that each stay as one chunk, so retrieval should rarely miss. I allowed one miss rather than requiring five because my add/drop question asks two things whose answers sit in different files, and the corpus has near-duplicate files (each course has a main, an exams and a workload document) that can outrank the right one. Fewer than four would mean retrieval is broken, not unlucky, on a corpus this clean.

## This is to ensure that the RAG system is retrieving answers relevant to the user's queries.

## 2. Every answer names a source

Every answer the system produces names at least one source document.

**Why this target:**

Every question that passes the gate reaches the model with each chunk labelled by its filename, and both the system instruction and the prompt tell it to name the file it used. So there’s no question in my set that’s harder to cite than another, and a single uncited answer is a failure I can’t explain away. I’m counting a source only when the model’s answer text names a filename, not the “Sources retrieved” line the code prints, which would make this impossible to miss. Refused questions don’t count, since there’s no answer to cite.

---

## 3. The relevance gate stops out-of-corpus questions

When I ask a question my documents clearly don't cover, the relevance gate
stops it and the system returns "I don't have enough information about that" —
in at least 4 of 5 tries.

<!-- The five questions are the ones in `OUT_OF_SCOPE` at the bottom of
     `questions.py`, and `run_eval.py` puts them through the gate and writes
     what happened into your run log. Swap them for your own if you'd rather —
     just keep five of them, or the "4 of 5" above has nothing to be 4 of. -->

**Why this target:**

<!-- What did your distances look like when you set the cutoff in Milestone 4?
     Was there a clean gap, or did the two groups overlap? -->

---

## 4. Something about your chunks

At least 5 of 5 sampled chunks include their document’s title line (e.g. “CS 210 Data Structures”), so every fact in a chunk can be tied to the course, hall or office it’s about.
**Why this target:**
campus_life posts start with a title line, and the facts under it often don’t name their subject. “Two midterms and a final” only means something next to “CS 210”, and nine courses and seven halls share the same kinds of facts. Right now every post fits in one 800-character chunk (the longest is 554 characters), so the title always comes along. I’m requiring all five because splitting a post by paragraph or sentence would separate facts from their titles, and even one such chunk could be retrieved for the wrong course.

---

## 5. Your choice

For at least 4 of 5 deadline or timeframe questions, the answer states the same deadline or timeframe as the source document, with no other week, day or month from the retrieved chunks substituted in.

**Why this target:**
campus_life’s deadline posts put several similar numbers close together. My add/drop question pulls in chunks mentioning weeks two, six, eight and ten, and the library post gives both “two to three days” for holds and “about a week” for interlibrary loans. Retrieval already finds the right document for all five, so a wrong number here is a generation mistake, not a retrieval one. I allowed one miss because the add/drop question asks for two dates at once, which gives the model twice the chance to swap one. But a system that gets deadlines wrong more than once is giving students wrong dates, which is the worst failure this guide could have.

---

<!-- ─────────────────────────────────────────────────────────────────────────
     UNIT 2 — read this before you change anything above.

     If a criterion turns out to be BROKEN rather than merely unmet, you can
     revise it, and that earns credit. But never delete or edit the original
     line. Add the revision underneath it, like this:

         ## 1. Retrieved chunks contain the answer

         For at least 4 of my 5 test questions, the retrieved chunks include
         one that contains the answer.

         **Why this target:** ...

         > **Revised in unit 2:** For at least 4 of 5 questions, the top three
         > results contain the answer.
         >
         > **Why revised:** I couldn't judge "the chunks include one that
         > contains the answer" the same way twice — I scored two questions
         > differently on Monday than on Wednesday. The new version is
         > something I can actually check.

     That's a revision because the criterion couldn't be MEASURED.

     Lowering a target because you missed it is not a revision, and it costs
     you the point:

         ✗ "I said 4 of 5 but got 2 of 5, so 2 of 5 is more realistic."

     A number you missed stays where it is, gets diagnosed, and gets a fix
     attempted. That's where the points are.

     The whole reason the originals stay visible is so someone can see what you
     said before you knew the answer.
     ───────────────────────────────────────────────────────────────────────── -->

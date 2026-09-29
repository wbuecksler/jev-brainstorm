# Anti-patterns

Where not to use TypeSafe Jev. Grounded in the [model jaggedness notes](https://docs.typesafe.ai/model-jaggedness/jev-1.13.md), the Beam rule of thumb, OpenRouter “when to skip,” Leonis, and Langfuse. This list does not add benchmarks.

Jev returns a **Choice**, **Score**, or **Noul** (plus probabilities). It does not write. If the valuable output is prose, a plan, or a number computed exactly, Jev is the wrong tool — or only the verify step after something else does the work.

Use this page before recommending an application from the [application map](application-map.md).

## Do not recommend these as Jev applications

1. **Any task whose primary output is prose.** Replies, summaries, code patches, explanations, and plans belong to a generative model or a person. Jev can optionally check a draft against a closed rubric (policy, citation, brand) after the draft exists.

2. **Open-ended answers.** Unknown label sets, creative naming, and free-form extraction of novel fields with no candidate set are not Choices. If you cannot write the options down before the call, you do not have a Jev question yet.

3. **Exact arithmetic, counting, date/time math, and numeric precision.** Code, regex, or a database owns exactness. Jev may handle the semantic part only (the date-extraction cookbook pattern: parse candidates in code, then Choice among them).

4. **Multi-hop or highly indirect reasoning (“System Two”).** Decompose the job, or hand the chain to a reasoner. Jev is a fast typed decision on state you already assembled.

5. **Huge noisy state.** Filter or select first. Context rot hurts accuracy. The vendor-stated state window is about 32k (OpenRouter/Vercel listings) — that is a ceiling, not a suggestion to fill it.

6. **Forcing generation through chained Choices.** Spelling a sentence one closed set at a time is slow and poor. Do not do it.

7. **Treating schema-safety as correctness.** A valid option can still be the wrong one. Calibrate on labeled traffic and keep a review band.

8. **Carrying thresholds across primitives.** A Noul probability is not a Choice “yes” probability. Do not assume complementary options sum to 1. Do not reuse a cutoff from another primitive, cookbook, or customer.

9. **Autonomous high-consequence acts without a human.** Wire transfers, clinical diagnosis, SAR filing, and lethal or safety-critical control stay with people. Leonis states this caution explicitly. Jev may prioritize or confirm; it does not close those loops alone.

10. **Overlapping, non-exclusive Choice sets, or a missing escape hatch.** If two options can both be true, they are separate Nouls or Scores, not one Choice. If none of the options may fit, include `other` or `unclear`. Langfuse calls out forced wrong picks when the hatch is missing.

11. **Images, audio, or video as the only state.** Jev state today is text or JSON. Transcribe, OCR, or describe elsewhere, then decide.

12. **Using Score interpolation as a precise continuous meter.** Ordered levels are weakly calibrated for reconstructing a magnitude (jaggedness notes). Use Score for a named rubric, not as a fake sensor.

13. **Replacing deterministic rules, regex, or database lookups.** When the answer is exact, code wins.

14. **Treating a shadow-router result as authorization.** Advice is not permission. The Pulumi jev-router and Codila patterns keep irreversible actions with humans until a calibrated policy says otherwise.

## Quick test before you recommend

All three should be true (Beam / OpenRouter framing):

1. The answer set is known in advance.
2. The same decision repeats at volume.
3. Code can act on confidence or probability — including the act “only log this, for now.”

If the pain is “write better replies,” recommend a generative model plus an optional Jev verify step, and say that plainly.

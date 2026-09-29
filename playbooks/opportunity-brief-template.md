# Opportunity Brief (template)

A one-page summary a leader can forward internally after a [discovery interview](discovery-interview.md). It's written for the people who approve and own the workflow, not the engineer. The engineer gets the [Claude Code prompt](claude-code-prototype-template.md).

Fill it from the [opportunity spec](../spec/opportunity-spec.schema.json) and the interview only. Unknown → `not stated`. No invented savings, accuracy, or headcount.

---

````markdown
# Opportunity Brief: {{WORKFLOW_NAME}}

**For:** {{LEADER_FUNCTION}}, {{COMPANY}} · **Prepared:** {{DATE}} · **Status:** proposal, shadow mode only

## The decision
Today, {{WHO}} decides **{{THE_DECISION}}** for each {{ITEM}} ({{VOLUME_AS_STATED}}).
The options are fixed: {{OPTIONS_IN_PLAIN_WORDS}}.

## Why it matters (in your words)
{{VALUE_AS_STATED}}

## What changes
A decision model (TypeSafe Jev) reads {{STATE_IN_PLAIN_WORDS}} and returns the same decision, with a probability for each option. It writes nothing. Your rules decide what happens next:

| Band | When (starting rule — yours to tune) | What happens during the pilot |
|---|---|---|
| Act | {{ACT_RULE_PLAIN}} | Logged only. A person still decides. |
| Review | {{REVIEW_RULE_PLAIN}} | Logged; flagged for a second look |
| Escalate | {{ESCALATE_RULE_PLAIN}} | Logged; goes to {{ESCALATION_OWNER}} |

## Why this is a fit
- **Volume:** {{V}} — {{V_WHY}}
- **Fixed options:** {{D}} — {{D_WHY}}
- **Safe with review:** {{R}} — {{R_WHY}}
- **History to check against:** {{L}} — {{L_WHY}}
- Closest known pattern: {{PATTERN}} (application map card {{MAP_CARD}})

## Risk and control
- **Pilot runs in shadow mode.** Nothing is sent, changed, or approved automatically.
- **What a wrong call costs today:** {{CONSEQUENCE_IF_WRONG}}
- **Policy owner:** {{POLICY_OWNER}} sets and changes the thresholds. {{HIGH_STAKES_LINE}}
- **Data:** the pilot reads {{STATE_IN_PLAIN_WORDS}} only. The API key sits in a repository secret, never in chat or code.

## Cost shape
{{COST_LINE_OR_NOT_STATED}}
*(Vendor-stated price of about $0.042 per million input tokens, applied to the volume you gave. This is not a measured result.)*

## The pilot
1. **This week:** an engineer runs the prototype on {{N}} past {{ITEM}}s where we already know the right answer.
2. **Then:** {{POLICY_OWNER}} reviews where Jev and people disagreed, and adjusts the bands.
3. **Decision point:** we turn anything on only if {{POLICY_OWNER}} is satisfied with the comparison. Even then, it starts with the safest band only.

**Not in scope:** {{OUT_OF_SCOPE}}

**Ask:** {{THE_ASK}}  *(e.g. "an engineer for two days and a read-only export of last quarter's closed tickets")*
````

---

## Fill notes

- `{{COST_LINE_OR_NOT_STATED}}`: include it only if the leader gave a volume and you can state the input size. Show the arithmetic. Otherwise write `Not estimated: volume or item size not stated.`
- `{{HIGH_STAKES_LINE}}`: if the spec has `high_stakes: true`, write "This workflow never acts automatically; Jev prioritizes and a person decides." Otherwise leave it empty.
- Keep it to one page. If it runs long, cut the explanations, not the risk section.

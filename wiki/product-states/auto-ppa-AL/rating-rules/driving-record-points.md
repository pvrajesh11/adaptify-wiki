---
title: "Auto PPA — Alabama — Driving Record Points"
summary: "Alabama Auto PPA driving record point structure. Overrides the multistate base in the same five cells as AK and documents AL-specific exceptions."
type: product-state-sub
cq_category: manuals
relevant_roles: [actuary]
product: auto-ppa
state: AL
parent: rating-rules
sub: driving-record-points
scope: state-override
source_docs: ["2026-04-14_auto-ppa_AL_manual_v1.5"]
scope_notes: "Point structure differs from multistate base in 5 cells — same overrides as AK. See deviation table below."
last_updated: 2026-04-14
---

# Auto PPA — Alabama — Driving Record Points

Parent: [Auto PPA — Alabama — Rating Rules](../rating-rules.md)
Source: PAU AL MAN-1.5 §6.4.1, §6.4.2
Multistate base: [Auto PPA — Multistate — Driving Record Points](../../../multistate/auto-ppa/rating-rules/driving-record-points.md)

> **AL deviations from multistate base:** 5 cells differ in the point table (identical overrides to AK). See deviation table below.
> Experience period, triggers, additional points, and most exceptions are `[multistate, unchanged]`.

---

## Experience Period

3 years immediately preceding the policy inception date or renewal effective date. `[multistate, unchanged]`

(SOURCE: 2026-04-14_auto-ppa_AL_manual_v1.5 §6.4.1)

---

## Point Assignment Triggers

`[multistate, unchanged]`

Points are assigned for:
- Convictions for motor vehicle violations
- At-fault accidents where a claim was paid by the company exceeding the approved dollar threshold (refer to company for threshold amount)

When multiple violations arise from one occurrence, use only the violation with the highest point value.

A 2nd or subsequent violation within the experience period is assessed both the age-of-violation points AND the additional violation surcharge.

---

## Point Structure `[multistate override — 5 cells differ]`

| Classification | 0–<6 Mo | 0–<1 Yr | 1–<2 Yr | 2–<3 Yr | Add'l Violation Surcharge |
|---|---|---|---|---|---|
| Speeding Violation (non-Major) | N/A | 2 | 1 | 1 | 1 |
| Minor Violation (non-Speeding) | N/A | **3** ¹ | 2 | 1 | 1 |
| Major Violation | N/A | 4 | 3 | **3** ² | **1** ³ |
| At-Fault Accident | N/A | 3 | **2** ⁴ | **1** ⁵ | **1** ⁶ |
| No Prior Insurance | 4 | N/A | N/A | N/A | N/A |

AL deviations from multistate base (bold cells):
1. Minor Violation 0–<1yr: AL **3** vs multistate 2
2. Major Violation 2–<3yr: AL **3** vs multistate 2
3. Major Violation add'l surcharge: AL **1** vs multistate 2
4. At-Fault Accident 1–<2yr: AL **2** vs multistate 3
5. At-Fault Accident 2–<3yr: AL **1** vs multistate 2
6. At-Fault Accident add'l surcharge: AL **1** vs multistate 0

Note: These deviations are identical to those found in Alaska (AK). See [AK — Driving Record Points](../../../product-states/auto-ppa-AK/rating-rules/driving-record-points.md) for comparison.

(SOURCE: 2026-04-14_auto-ppa_AL_manual_v1.5 §6.4.1)

Violation classification follows the AAMVA Code Dictionary.

---

## Additional Points

`[multistate, unchanged]`

- **4 points** — lapse in mandatory/compulsory insurance of 30+ days immediately preceding policy inception, unless:
  - Driver did not own a vehicle requiring mandatory coverage during that period, OR
  - Lapse was due to active military service or deployment
- **1 point** — conviction not in the classification table above that results in license suspension or revocation

---

## Exceptions — Points NOT Assigned For

`[multistate, unchanged]` with the following as documented in the AL manual:

- Violations/accidents for a driver who is the named insured of a separate policy or the principal driver of a vehicle on a separate policy
- Non-moving violations (e.g., equipment violations)
- A single conviction under 75 Pa. C.S. § 1535 during the experience period ⚠️ *(flagged: possible Pennsylvania statute artifact — verify AL applicability)*
- Two or more convictions under 75 Pa. C.S. § 1535 unless committed by the same insured driver ⚠️ *(same flag)*
- At-fault accidents eliminated by Accident Forgiveness (Rule 4.7.4)
- Accidents where the insured auto was lawfully parked and stationary *(if a parked auto rolls and causes an accident, points are assigned to the driver who parked it)*
- Accidents where the insured driver is reimbursed by or has a judgment against another person determined responsible
- Accidents covered under UM or UIM coverage
- Accidents where damage is covered under Comprehensive Coverage
- The insured auto was struck in the rear and the insured driver had no moving violation conviction
- The operator of the other auto was convicted of a moving violation and the insured driver was not
- Emergency response accidents (paid/volunteer: police, fire, first-aid, law enforcement) — exception ends when auto ceases being used in response
- Hit-and-run accidents reported to proper authority within 24 hours
- Damage from contact with animals or fowl
- Physical damage from flying gravel, missiles, or falling objects
- Comprehensive claims unless the loss was intentionally caused by an insured

---

## Financial Responsibility Filing `[multistate override]`

Rule **does not apply** in Alabama. Multistate rule (6.4.2) applies in all other states. (SOURCE: 2026-04-14_auto-ppa_AL_manual_v1.5 §6.4.2)

## Unverifiable Driving Record `[multistate, status unconfirmed]`

Multistate Rule 6.4.3 applies to drivers whose history cannot be verified. The AL state manual does not address this rule explicitly — verify whether multistate rule applies in AL.

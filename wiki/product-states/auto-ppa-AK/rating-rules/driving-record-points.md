---
title: "Auto PPA — Alaska — Driving Record Points"
type: product-state-sub
product: auto-ppa
state: AK
parent: rating-rules
sub: driving-record-points
source_docs: ["2026-04-14_auto-ppa_AK_manual_v1.5"]
scope_notes: "Structure ingested from AK state manual. Scope vs multistate base TBD after MULTI manual ingested."
last_updated: 2026-04-14
---

# Auto PPA — Alaska — Driving Record Points

Parent: [[product-states/auto-ppa-AK/rating-rules]]
Source: PAU AK MAN-1.5 §6.4.1, §6.4.2

> Scope note: This structure was extracted from the AK state manual. Whether these rules are multistate or AK-specific will be confirmed after ingesting MULTI PAU Manual 01 21.docx.

---

## Experience Period

3 years immediately preceding the policy inception date or renewal effective date. (SOURCE: 2026-04-14_auto-ppa_AK_manual_v1.5 §6.4.1)

---

## Point Assignment Triggers

Points are assigned for:
- Convictions for motor vehicle violations
- At-fault accidents where a claim was paid by the company exceeding the approved dollar threshold (refer to company for threshold amount)

When multiple violations arise from one occurrence, use only the violation with the highest point value.

A 2nd or subsequent violation within the experience period is assessed both the age-of-violation points AND the additional violation surcharge.

---

## Point Structure

| Classification | 0–<6 Mo | 0–<1 Yr | 1–<2 Yr | 2–<3 Yr | Add'l Violation Surcharge |
|---|---|---|---|---|---|
| Speeding Violation (non-Major) | N/A | 2 | 1 | 1 | 1 |
| Minor Violation (non-Speeding) | N/A | 3 | 2 | 1 | 1 |
| Major Violation | N/A | 4 | 3 | 3 | 1 |
| At-Fault Accident | N/A | 3 | 2 | 1 | 1 |
| No Prior Insurance | 4 | N/A | N/A | N/A | N/A |

Violation classification follows the AAMVA Code Dictionary.

---

## Additional Points

- **4 points** — lapse in mandatory/compulsory insurance of 30+ days immediately preceding policy inception, unless:
  - Driver did not own a vehicle requiring mandatory coverage during that period, OR
  - Lapse was due to active military service or deployment
- **1 point** — conviction not in the classification table above that results in license suspension or revocation

---

## Exceptions — Points NOT Assigned For

- Violations/accidents for a driver who is the named insured of a separate policy or the principal driver of a vehicle on a separate policy
- Non-moving violations (e.g., equipment violations)
- A single conviction under 75 Pa. C.S. § 1535 during the experience period ⚠️ *(flagged: possible Pennsylvania statute artifact — verify AK applicability)*
- Two or more convictions under 75 Pa. C.S. § 1535 unless committed by the same insured driver ⚠️ *(same flag)*
- At-fault accidents eliminated by Accident Forgiveness (Rule 4.7.4)
- Accidents where the insured auto was lawfully parked and stationary *(if a parked auto rolls and causes an accident, points are assigned to the driver who parked it)*
- Accidents where the insured driver is reimbursed by or has a judgment against another person determined responsible
- Accidents covered under UM or UIM coverage
- Accidents where damage is covered under Comprehensive Coverage
- Rear-end collisions where the insured auto was struck from behind and the insured driver had no moving violation conviction
- Accidents where the other driver was convicted of a moving violation and the insured driver was not
- Emergency response accidents (paid/volunteer: police, fire, first-aid, law enforcement) — exception ends when auto ceases being used in response
- Hit-and-run accidents reported to proper authority within 24 hours
- Damage from contact with animals or fowl
- Physical damage from flying gravel, missiles, or falling objects
- Comprehensive claims unless the loss was intentionally caused by an insured

---

## Financial Responsibility Filing `[AK-specific]`

Rule **does not apply** in Alaska. (SOURCE: 2026-04-14_auto-ppa_AK_manual_v1.5 §6.4.2)

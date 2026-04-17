---
title: "Motor Truck Cargo — Multistate — Rating Factors"
summary: "Multistate Motor Truck Cargo rating factors: commodity classes, operating radius, vehicle protection tiers, and rating sequences drawn from CIM MTC MU RTG REV 04 18."
type: multistate
product: motor-truck-cargo
page: rating-factors
scope: multistate
source_docs: ["2026-04-14_motor-truck-cargo_MULTI_manual_v04-18"]
version_current: "REV 04 18"
last_updated: 2026-04-14
---

# Motor Truck Cargo — Multistate — Rating Factors

Parent: [Motor Truck Cargo — Multistate — Rating Rules](../rating-rules.md)
Source: CIM MTC MU RTG REV 04 18

> Rating rules and classification definitions only. Numerical loss costs and base rate tables are in the Loss Cost Schedule (CIM MTC MU LCS 0823), which was not ingested.

---

## Commodity Classification

Commodity class is the primary cargo risk variable. The Commodity Classification Index assigns each commodity to one of five classes. (SOURCE: 2026-04-14_motor-truck-cargo_MULTI_manual_v04-18 §Step 1.A / Step 1.B)

- **Class 1** — lowest hazard (bulk commodities, low theft risk)
- **Classes 2, 3, 4** — increasing hazard
- **Class 5** — target/hazardous cargo; requires Target/Hazardous Cargo Modification (1.25–2.00) in addition to the base load

In Method B (Gross Receipts), Class 5 commodities use the Class 4 load for Step 2.B, with the separate Step 6.B modification applied afterward.

See [Coverage Options](coverage-options.md) for the full commodity index by class.

---

## Operating Radius

Radius of operations is a required rating variable for both Method A (Step 2.A) and Method B (Step 2.B). Three tiers: (SOURCE: 2026-04-14_motor-truck-cargo_MULTI_manual_v04-18 §Step 2.A / Step 2.B)

| Radius | Definition |
|---|---|
| Local | Within 50 miles |
| Intermediate | 51 to 200 miles |
| Long Haul | Over 200 miles |

Long haul operations may require an additional Radius of Operations Modification (Step 8.A / Step 8.B) when exposures exceed those contemplated in the basic load. See [Coverage Modifications](coverage-modifications.md).

---

## Vehicle Protection Tier

Vehicle protection affects the basic load for cargo (Methods A and B) and the basic load for mobile/electronic equipment (Method C) and trailers (Method D). (SOURCE: 2026-04-14_motor-truck-cargo_MULTI_manual_v04-18 §Step 2.A)

For cargo:
1. Guards or guards in following vehicle
2. Vehicle alarms and/or tracking equipment (satellite, black box)
3. No additional protection

For mobile/electronic equipment and trailers:
1. Vehicle alarms with secured, fenced lot when not in use
2. No additional vehicle protection

---

## Premium Base — Per Vehicle vs. Gross Receipts

**Method A (Per Vehicle):** Premium base is the per vehicle limit. The basic load factor is applied to the per vehicle limit (per $100 limit), producing a per-vehicle load which is then multiplied by number of vehicles. (SOURCE: 2026-04-14_motor-truck-cargo_MULTI_manual_v04-18 §Step 2.A)

Limit tiers for basic load factor:
- $1–$50,000
- $50,001–$100,000
- $100,001 and over

**Method B (Gross Receipts):** Premium base is annual gross receipts. The basic load is a rate per $100 of gross receipts, determined by both gross receipts tier and commodity class. (SOURCE: 2026-04-14_motor-truck-cargo_MULTI_manual_v04-18 §Step 2.B)

Gross receipts tiers: $250,000–$500,000; $500,001–$2,500,000; $2,500,001–$5,000,000; over $5,000,000.

---

## Rating Sequence — Method A (Per Vehicle)

1. Determine commodity class (Step 1.A)
2. Determine basic load from per vehicle limit and risk features (Step 2.A)
3. Add refrigeration breakdown load if applicable (Step 3.A)
4. Apply contingent coverage modification if applicable (Step 4.A)
5. Multiply by number of vehicles (Step 5.A)
6. Apply target/hazardous cargo modification if Class 5 (Step 6.A)
7. Apply loss cost multiplier (Step 7.A)
8. Add long haul radius additional premium if applicable (Step 8.A)
9. Add terminal additional premium if applicable (Step 9.A)
10. Sum steps 7/8/9 (Step 10.A)
11. Apply named perils modification if applicable (Step 11.A)
12. Apply deductible modification (Step 12.A)
13. Apply IRPM if applicable (Step 13.A)

(SOURCE: 2026-04-14_motor-truck-cargo_MULTI_manual_v04-18 §Per Vehicle Premium Determination)

---

## Rating Sequence — Method B (Gross Receipts)

Parallel structure to Method A with gross receipts as the base. Steps 1.B through 13.B correspond to the same functions as Method A. (SOURCE: 2026-04-14_motor-truck-cargo_MULTI_manual_v04-18 §Gross Receipts Premium Determination)

---

## Rating Sequence — Method C (Mobile/Moving/Electronic Equipment/Personal Property)

1. Determine basic load from theft potential, vehicle protection, and radius (Step 1.C) — load range 1.00–1.25
2. Multiply limit of insurance (per $100) by basic load (Step 2.C)
3. Apply loss cost multiplier, multiply by Step 2.C result (Step 3.C)
4. Apply IRPM if applicable (Step 4.C)

(SOURCE: 2026-04-14_motor-truck-cargo_MULTI_manual_v04-18 §Method C)

---

## Rating Sequence — Method D (Trailer Coverage)

1. Determine basic load from theft potential, trailer protection, and radius (Step 1.D) — load range 0.50–1.00
2. Multiply limit of insurance (per $100) by basic load (Step 2.D)
3. Apply loss cost multiplier, multiply by Step 2.D result (Step 3.D)
4. Apply IRPM if applicable (Step 4.D)

(SOURCE: 2026-04-14_motor-truck-cargo_MULTI_manual_v04-18 §Method D)

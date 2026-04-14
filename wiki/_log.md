# Operation Log

<!-- Append only. Never edit or delete past entries. -->
<!-- Format: [YYYY-MM-DD] OPERATION | details -->

[2026-04-14] INIT | Repository created. Schema and CLAUDE.md written. 0 sources ingested.
[2026-04-14] INGEST | 2026-04-14_auto-ppa_AK_manual_v1.5 | source: PAU AK MAN-1.5 - Final.docx | doc_type: manual | state: AK | product: auto-ppa
[2026-04-14] ABSORB | 2026-04-14_auto-ppa_AK_manual_v1.5 | pages updated: 9 | new pages: products/auto-ppa, states/AK, product-states/auto-ppa-AK/rating-rules, rating-rules/coverage-options, rating-rules/driving-record-points, rating-rules/state-specifics, product-states/auto-ppa-AK/endorsements, coverages/uninsured-motorist, coverages/transportation-network
[2026-04-14] REFACTOR | Split rating-rules.md into index + 3 sub-pages; added multistate/ layer structure; removed broken wikilinks from products/auto-ppa.md; updated schema.md with multistate model, sub-page pattern, no-broken-links rule
[2026-04-14] INGEST | 2026-04-14_auto-ppa_AK_filing-summary | source: AK_FilingSummary.pdf | doc_type: filing-summary | state: AK | product: auto-ppa | SERFF: SRFF-TEST-AK-PPA-0001 | effective: 2026-01-01
[2026-04-14] ABSORB | 2026-04-14_auto-ppa_AK_filing-summary | pages updated: 2 | states/AK (filing history, active products table), products/auto-ppa (active states table)
[2026-04-14] INGEST | 2026-04-14_auto-ppa_MULTI_manual_v01-21 | source: MULTI PAU Manual 01 21.docx | doc_type: manual | state: MULTI | product: auto-ppa | edition: 01 21
[2026-04-14] ABSORB | 2026-04-14_auto-ppa_MULTI_manual_v01-21 | pages new: multistate/auto-ppa/rating-rules, rating-rules/coverage-options, rating-rules/driving-record-points, rating-rules/coverage-modifications | pages updated: product-states/auto-ppa-AK/rating-rules/driving-record-points
[2026-04-14] INGEST | 2026-04-14_auto-ppa_AK_form_PPA-0001-07-16 | source: PPA 0001 07 16 Personal Automobile Policy.docx | doc_type: form | state: AK | product: auto-ppa | form: PPA 0001 07 16
[2026-04-14] ABSORB | 2026-04-14_auto-ppa_AK_form_PPA-0001-07-16 | pages new: forms/PPA-0001-07-16
[2026-04-14] INGEST | 2026-04-14_auto-ppa_AK_form_PPA-0154-01-20 | source: PPA 0154 01 20 Amendatory Endorsement Alaska.docx | doc_type: form | state: AK | product: auto-ppa | form: PPA 0154 01 20
[2026-04-14] ABSORB | 2026-04-14_auto-ppa_AK_form_PPA-0154-01-20 | pages new: forms/PPA-0154-01-20 | pages updated: product-states/auto-ppa-AK/rating-rules/state-specifics

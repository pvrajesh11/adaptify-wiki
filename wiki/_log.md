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
[2026-04-14] INGEST | 2026-04-14_auto-ppa_AL_filing-summary | source: AL_FilingSummary.pdf | doc_type: filing-summary | state: AL | product: auto-ppa | SERFF: SRFF-TEST-AL-PPA-0001 | effective: 2026-01-01
[2026-04-14] INGEST | 2026-04-14_auto-ppa_AL_manual_v1.5 | source: PAU AL MAN-1.5 - Final.docx | doc_type: manual | state: AL | product: auto-ppa
[2026-04-14] INGEST | 2026-04-14_auto-ppa_AL_form_PPA-0101-03-18 | source: PPA 0101 03 18 Amendatory Endorsement Alabama.docx | doc_type: form | state: AL | product: auto-ppa
[2026-04-14] ABSORB | 2026-04-14_auto-ppa_AL_* | pages new: states/AL, product-states/auto-ppa-AL/rating-rules + 3 sub-pages, product-states/auto-ppa-AL/endorsements, forms/PPA-0101-03-18 | pages updated: products/auto-ppa, multistate/auto-ppa/rating-rules, multistate/auto-ppa/rating-rules/driving-record-points
[2026-04-14] INGEST | 2026-04-14_homeowners-hobp_MULTI_manual_v0111 | source: MULTI HOBP 0111.docx | doc_type: manual | state: MULTI | product: homeowners-hobp | edition: 01 11
[2026-04-14] INGEST | 2026-04-14_homeowners-hobp_MULTI_flood-supplement_v06-21 | source: HO HOBP Multistate Flood Coverage Supplement Rev 06 21.docx | doc_type: manual | state: MULTI | product: homeowners-hobp
[2026-04-14] ABSORB | 2026-04-14_homeowners-hobp_MULTI_* | pages new: products/homeowners-hobp, multistate/homeowners-hobp/rating-rules + 5 sub-pages (coverage-options, underwriting-rules, coverage-modifications, rating-factors, flood-coverage)
[2026-04-14] INGEST | 2026-04-14_homeowners-hobp_FL_filing-summary | source: FL_FilingSummary.pdf | state: FL | product: homeowners-hobp | SERFF: SRFF-TEST-FL-HO-0001 | effective: 2026-01-01
[2026-04-14] INGEST | 2026-04-14_homeowners-hobp_FL_state-pages_v1215 | source: FL HOBP State Pages 1215.docx | state: FL | product: homeowners-hobp
[2026-04-14] INGEST | 2026-04-14_homeowners-hobp_FL_form_HO-0003-09-20 | source: HO 0003 09 20 Special Form.docx | doc_type: form | state: FL | product: homeowners-hobp
[2026-04-14] INGEST | 2026-04-14_homeowners-hobp_FL_form_HO-0809-02-22 | source: HO 0809 02 22 Amendatory Endorsement Florida.docx | doc_type: form | state: FL | product: homeowners-hobp
[2026-04-14] ABSORB | 2026-04-14_homeowners-hobp_FL_* | pages new: states/FL, product-states/homeowners-hobp-FL/rating-rules + 3 sub-pages, product-states/homeowners-hobp-FL/endorsements, forms/HO-0003-09-20, forms/HO-0809-02-22
[2026-04-14] INGEST | 2026-04-14_homeowners-hobp_AK_filing-summary | source: AK_FilingSummary.pdf | state: AK | product: homeowners-hobp | SERFF: SRFF-TEST-AK-HO-0001 | effective: 2026-01-01
[2026-04-14] INGEST | 2026-04-14_homeowners-hobp_AK_state-pages_v1215 | source: AK HOBP State Pages 1215.docx | state: AK | product: homeowners-hobp
[2026-04-14] INGEST | 2026-04-14_homeowners-hobp_AK_form_HO-0854-02-21 | source: HO 0854 02 21 Amendatory Endorsement Alaska.docx | doc_type: form | state: AK | product: homeowners-hobp
[2026-04-14] ABSORB | 2026-04-14_homeowners-hobp_AK_* | pages new: product-states/homeowners-hobp-AK/rating-rules + 3 sub-pages, product-states/homeowners-hobp-AK/endorsements, forms/HO-0854-02-21 | pages updated: states/AK
[2026-04-14] INGEST | 2026-04-14_homeowners-hobp_AL_filing-summary | source: AL_FilingSummary.pdf | state: AL | product: homeowners-hobp | SERFF: SRFF-TEST-AL-HO-0001 | effective: 2026-01-01
[2026-04-14] INGEST | 2026-04-14_homeowners-hobp_AL_state-pages_v1215 | source: AL HOBP State Pages 1215.docx | state: AL | product: homeowners-hobp
[2026-04-14] INGEST | 2026-04-14_homeowners-hobp_AL_form_HO-0801-09-20 | source: HO 0801 09 20 Amendatory Endorsement Alabama.docx | doc_type: form | state: AL | product: homeowners-hobp
[2026-04-14] ABSORB | 2026-04-14_homeowners-hobp_AL_* | pages new: product-states/homeowners-hobp-AL/rating-rules + 3 sub-pages, product-states/homeowners-hobp-AL/endorsements, forms/HO-0801-09-20 | pages updated: states/AL
[2026-04-14] INGEST | 2026-04-14_motor-truck-cargo_MULTI_manual_v04-18 | source: CIM MTC MU RTG REV 04 18.docx | doc_type: manual | state: MULTI | product: motor-truck-cargo
[2026-04-14] ABSORB | 2026-04-14_motor-truck-cargo_MULTI_manual_v04-18 | pages new: products/motor-truck-cargo, multistate/motor-truck-cargo/rating-rules + 4 sub-pages (coverage-options, underwriting-rules, coverage-modifications, rating-factors)
[2026-04-14] INGEST | 2026-04-14_motor-truck-cargo_AK_filing-summary | source: AK_FilingSummary.pdf | state: AK | product: motor-truck-cargo | SERFF: SRFF-TEST-AK-MTC-0001 | effective: 2026-01-01
[2026-04-14] INGEST | 2026-04-14_motor-truck-cargo_AK_form_CIM-7002-01-15 | source: CIM 7002 01 15 Motor Truck Cargo Coverage.docx | doc_type: form | state: AK | product: motor-truck-cargo
[2026-04-14] INGEST | 2026-04-14_motor-truck-cargo_AK_form_CIM-2003-06-20 | source: CIM 2003 06 20 Amendatory Endorsement Alaska.docx | doc_type: form | state: AK | product: motor-truck-cargo
[2026-04-14] ABSORB | 2026-04-14_motor-truck-cargo_AK_* | pages new: product-states/motor-truck-cargo-AK/rating-rules + 3 sub-pages, product-states/motor-truck-cargo-AK/endorsements, forms/CIM-7002-01-15, forms/CIM-2003-06-20 | pages updated: states/AK
[2026-04-14] INGEST | 2026-04-14_motor-truck-cargo_AL_filing-summary | source: AL_FilingSummary.pdf | state: AL | product: motor-truck-cargo | SERFF: SRFF-TEST-AL-MTC-0001 | effective: 2026-01-01
[2026-04-14] INGEST | 2026-04-14_motor-truck-cargo_AL_form_CIM-2001-08-15 | source: CIM 2001 08 15 Amendatory Endorsement Alabama.docx | doc_type: form | state: AL | product: motor-truck-cargo
[2026-04-14] ABSORB | 2026-04-14_motor-truck-cargo_AL_* | pages new: product-states/motor-truck-cargo-AL/rating-rules + 3 sub-pages, product-states/motor-truck-cargo-AL/endorsements, forms/CIM-2001-08-15 | pages updated: states/AL, multistate/motor-truck-cargo/rating-rules
[2026-04-14] CONSOLIDATE | Updated products/homeowners-hobp (active states AK/AL/FL), products/motor-truck-cargo (active states AK/AL), multistate/homeowners-hobp/rating-rules (state overrides table), multistate/motor-truck-cargo/rating-rules (AK overrides added), wiki/index.md (70 pages)

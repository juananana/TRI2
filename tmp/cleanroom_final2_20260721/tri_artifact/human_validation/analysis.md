# TRI Human Construct Validation

All statistics use three independent annotations per item. Confidence was optional.

## Quality audit

- n_keyed_items: 100
- n_annotators: 3
- missing_responses: 0
- invalid_responses: 0
- duplicate_ids: 0
- payload_mismatches: 0
- three_way_ties: 6

## Agreement and gold alignment

| Slice | n | Majority-gold | Determinate majority-gold | 95% Wilson CI | Unanimous | Fleiss kappa | Krippendorff alpha | Any clarify |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| all | 100 | 86.0% | 91.5% | [77.9%, 91.5%] | 72.0% | 0.708 | 0.709 | 4.0% |
| explicit | 60 | 86.7% | 94.5% | [75.8%, 93.1%] | 70.0% | 0.672 | 0.674 | 1.7% |
| implicit | 40 | 85.0% | 87.2% | [70.9%, 92.9%] | 75.0% | 0.758 | 0.760 | 7.5% |
| original | 50 | 84.0% | 91.3% | [71.5%, 91.7%] | 70.0% | 0.679 | 0.681 | 4.0% |
| human_rewrite | 50 | 88.0% | 91.7% | [76.2%, 94.4%] | 74.0% | 0.737 | 0.738 | 4.0% |
| anchored | 50 | 74.0% | 84.1% | [60.4%, 84.1%] | 48.0% | 0.453 | 0.457 | 8.0% |
| dynamic | 50 | 98.0% | 98.0% | [89.5%, 99.6%] | 96.0% | 0.924 | 0.925 | 0.0% |
| anchored_actionable | 30 | 86.7% | 100.0% | [70.3%, 94.7%] | 63.3% | 0.538 | 0.543 | 6.7% |
| anchored_reject | 20 | 55.0% | 61.1% | [34.2%, 74.2%] | 25.0% | 0.087 | 0.102 | 10.0% |
| update:flip | 20 | 95.0% | 100.0% | [76.4%, 99.1%] | 80.0% | 0.723 | 0.727 | 5.0% |
| update:invalidate | 20 | 60.0% | 63.2% | [38.7%, 78.1%] | 50.0% | 0.406 | 0.416 | 0.0% |
| update:name_collision | 20 | 80.0% | 94.1% | [58.4%, 91.9%] | 60.0% | 0.443 | 0.452 | 5.0% |
| update:remove | 20 | 95.0% | 100.0% | [76.4%, 99.1%] | 75.0% | 0.646 | 0.652 | 10.0% |
| update:stable | 20 | 100.0% | 100.0% | [83.9%, 100.0%] | 95.0% | -0.017 | 0.000 | 0.0% |
| gold:ORIGINAL_AND_REFRESHED | 20 | 100.0% | 100.0% | [83.9%, 100.0%] | 95.0% | -0.017 | 0.000 | 0.0% |
| gold:ORIGINAL_ENTITY | 20 | 80.0% | 100.0% | [58.4%, 91.9%] | 50.0% | -0.023 | -0.006 | 10.0% |
| gold:REFRESHED_SELECTOR | 40 | 97.5% | 97.5% | [87.1%, 99.6%] | 95.0% | 0.316 | 0.322 | 0.0% |
| gold:REJECT | 20 | 55.0% | 61.1% | [34.2%, 74.2%] | 25.0% | 0.087 | 0.102 | 10.0% |

## Annotator-level audit

| Annotator | Gold accuracy | Clarify rate | Confidence coverage | Mean confidence |
|---|---:|---:|---:|---:|
| A1 | 87.0% | 0.0% | 0.0% | NA |
| A2 | 80.0% | 4.0% | 100.0% | 4.90 |
| A3 | 89.0% | 0.0% | 90.0% | 5.00 |

## Disagreement items

| Item | Gold | A1 | A2 | A3 | Majority |
|---|---|---|---|---|---|
| HV-0002 | REJECT | REJECT | REJECT | SKU-11 | REJECT |
| HV-0007 | TCK-41 | TCK-52 | CLARIFY | TCK-41 | NONE |
| HV-0014 | REJECT | LEAD-22 | LEAD-17 | LEAD-17 | LEAD-17 |
| HV-0015 | EM-104 | EM-104 | EM-319 | EM-104 | EM-104 |
| HV-0020 | REJECT | DOC-8 | CLARIFY | REJECT | NONE |
| HV-0022 | DOC-8 | DOC-8 | DOC-7 | DOC-7 | DOC-7 |
| HV-0023 | REJECT | REJECT | DOC-7 | DOC-7 | DOC-7 |
| HV-0029 | REJECT | REJECT | EM-104 | EM-104 | EM-104 |
| HV-0032 | REJECT | REJECT | CLARIFY | REJECT | REJECT |
| HV-0035 | REJECT | DOC-8 | REJECT | REJECT | REJECT |
| HV-0050 | REJECT | REJECT | REJECT | TCK-41 | REJECT |
| HV-0054 | REJECT | LEAD-22 | LEAD-17 | LEAD-17 | LEAD-17 |
| HV-0056 | BR-main | BR-rel | REJECT | BR-main | NONE |
| HV-0058 | MTG-10 | MTG-10 | REJECT | MTG-10 | MTG-10 |
| HV-0059 | REJECT | SHP-91 | REJECT | REJECT | REJECT |
| HV-0060 | REJECT | REJECT | DOC-7 | DOC-7 | DOC-7 |
| HV-0061 | TCK-41 | TCK-41 | REJECT | TCK-41 | TCK-41 |
| HV-0062 | REJECT | MTG-22 | REJECT | REJECT | REJECT |
| HV-0070 | LEAD-17 | LEAD-17 | REJECT | LEAD-17 | LEAD-17 |
| HV-0074 | SHP-91 | SHP-91 | SHP-88 | SHP-91 | SHP-91 |
| HV-0075 | MTG-10 | MTG-10 | CLARIFY | MTG-10 | MTG-10 |
| HV-0077 | REJECT | REJECT | EM-104 | EM-104 | EM-104 |
| HV-0084 | REJECT | TCK-52 | REJECT | TCK-41 | NONE |
| HV-0088 | SHP-88 | SHP-91 | SHP-88 | SHP-88 | SHP-88 |
| HV-0089 | REJECT | REJECT | SKU-11 | SKU-11 | SKU-11 |
| HV-0091 | SHP-88 | SHP-91 | SHP-88 | SHP-88 | SHP-88 |
| HV-0094 | MTG-10 | MTG-22 | REJECT | MTG-10 | NONE |
| HV-0098 | MTG-10 | MTG-22 | REJECT | MTG-10 | NONE |

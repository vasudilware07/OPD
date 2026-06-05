# Decision Logic Flowchart

## Complete Adjudication Flow

```
CLAIM SUBMITTED
       |
       v
[Check Minimum Amount]
  |              |
  | < 500        | >= 500
  v              v
REJECT        [Check Policy Active?]
BELOW_MIN       |              |
                | Inactive     | Active
                v              v
              REJECT        [Check Initial Waiting Period]
              POLICY_INACTIVE  |                    |
                               | Not Met            | Met
                               v                    v
                             REJECT              [Check Specific Waiting Periods]
                             WAITING_PERIOD        (Diabetes: 90d, Hypertension: 90d, etc.)
                                                    |                    |
                                                    | Not Met            | Met
                                                    v                    v
                                                  REJECT              [Check Documents]
                                                  WAITING_PERIOD        |
                                                                       / \
                                                        Missing Prescription  All Present
                                                              |                |
                                                              v                v
                                                          REJECT         [Check Coverage]
                                                          MISSING_DOCS    |
                                                                         / | \
                                                          Excluded    Partial  Covered
                                                            |           |       |
                                                            v           v       v
                                                        REJECT    PARTIAL   [Check Limits]
                                                        SERVICE    APPROVAL   |
                                                        NOT_COVERED          / | \
                                                                     Exceeds  OK  Annual
                                                                     Per-Claim     Exceeded
                                                                        |     |      |
                                                                        v     v      v
                                                                    REJECT  [Apply  REJECT
                                                                    PER_     Co-pay] ANNUAL
                                                                    CLAIM    |       LIMIT
                                                                    EXCEEDED |
                                                                             v
                                                                          [Check Fraud]
                                                                            |         |
                                                                          Flags       Clean
                                                                            |         |
                                                                            v         v
                                                                       MANUAL      APPROVED
                                                                       REVIEW      (with deductions)
```

## Co-Payment Calculation

```
Approved Amount = Claim Amount - Co-Pay (10%) - Network Discount (20% if applicable)

Example (TC001):
  Claim: 1500
  Co-pay (10%): 150
  Approved: 1350

Example (TC010):
  Claim: 4500
  Network Discount (20%): 900
  Net after discount: 3600
  Co-pay (10% of 3600): 360
  Approved: 3240
```

## Decision Priority Rules

1. Safety first - reject suspicious/fraudulent claims
2. Policy exclusions override everything
3. Hard limits cannot be exceeded
4. Medical necessity is mandatory
5. When confidence < 70%, send to manual review
6. When in doubt, refer for manual review

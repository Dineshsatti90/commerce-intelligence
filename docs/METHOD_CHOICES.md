# Explain the analytical choices

**Why a day-30 landmark?** Delivery must precede the outcome it is used to explain. Requiring delivery and no repeat by day 30, then measuring repeat on days 31–90, establishes that ordering but selects a different population and does not identify a causal effect.

**Why pool sparse controls?** Small states and an early quarter had zero repeat events, making unpooled logistic coefficients and robust uncertainty unstable. The revised model pools states below 500 and adjacent sparse quarters using counts alone, retains full design rank, and produces repeatable intervals; the resulting interval is about −0.45 to +0.13 points.

**Why HC1 and the delta method?** HC1 estimates covariance without assuming the binomial variance model is exactly specified; the delta method propagates that uncertainty to the average predicted probability difference. Neither removes unmeasured confounding or accounts for arbitrary seller clustering.

**Why not say no effect?** A confidence interval spanning zero is not evidence of equivalence. The independent two-proportion power sensitivity fixes the landmark baseline and allocation, not the roughly 2% full-window outcome; it is a planning approximation rather than retrospective GLM power.

**Why aggregate joins first?** Orders can contain multiple items, payments and reviews. Aggregating each child table to order grain before joining prevents multiplicative fan-out; latest review selection and persistent customer IDs are explicit.

**Why SQL summaries and scope review?** SQL computes endpoints and weighted rates deterministically while the model selects cited cells. Schema validity and exact matching cannot establish relevance, so fresh-set failures remain public and configured routing requires a person to select the intended scope.

Planning references: [NormalIndPower](https://www.statsmodels.org/stable/generated/statsmodels.stats.power.NormalIndPower.html), [proportion effect size](https://www.statsmodels.org/stable/generated/statsmodels.stats.proportion.proportion_effectsize.html).

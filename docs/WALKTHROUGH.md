# Two-minute delivery decision walkthrough

Open the [live dashboard](https://dineshsatti90-commerce-intelligence.streamlit.app/). If it is waking, use the [overview screenshot](screenshots/overview.jpg) and the [decision memo](../reports/decision_memo.md).

| Time | Show | Explain |
| --- | --- | --- |
| 0:00–0:25 | Overview | 99,421 analyzed orders and R$13.22m delivered merchandise value. Olist is real historical data; fulfillment completion is not browsing conversion. |
| 0:25–1:05 | Delivery & repeat purchase | Late deliveries are associated with review scores of 2.27 versus 4.29. Raw repeat rates differ, but the adjusted day-30 landmark interval spans zero. The roughly 2% full-window baseline is not the landmark baseline. |
| 1:05–1:35 | Decision & experiment | Prioritize MA, CE and BA operational investigation. Do not book retention savings. The separate planning sensitivity needs about 0.39 points of decrease at the low landmark baseline under its stated assumptions; a future randomized test needs its own design. |
| 1:35–2:10 | Evidence explorer | Select a reviewed query, then inspect the full result and SQL fingerprints. Monthly endpoint summaries are calculated by SQL. |
| 2:10–2:30 | AI evaluation | Contrast 3B and 8B results, the fresh set and failures. Valid numbers can come from the wrong query; the configured flow requires scope review. |

Interview close: “I would fund a measured customer-experience test, not forecast retention revenue from this observational association.”

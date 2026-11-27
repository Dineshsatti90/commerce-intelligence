"""Public dashboard runs from the aggregate extracts committed to Git."""

from pathlib import Path
import json

import streamlit as st

from copilot import CATALOG, answer, evidence, route
from demo_data import load_table

ROOT = Path(__file__).resolve().parent


def main() -> None:
    st.set_page_config(page_title="Commerce Intelligence", layout="wide", initial_sidebar_state="collapsed")
    st.title("Delivery & repeat purchase")
    st.caption("Olist marketplace | historical real orders | BRL | purchases before September 2018")
    metrics = json.loads((ROOT / "reports/metrics.json").read_text())
    st.sidebar.header("About this demo")
    st.sidebar.write("Runs from published aggregates. No database download or API key is required.")
    st.sidebar.link_button("Source & methodology", "https://github.com/Dineshsatti90/commerce-intelligence")
    one, two, three = st.columns(3)
    one.metric("Analyzed orders", f"{metrics['orders']:,}")
    two.metric("Delivered merchandise value", f"R${metrics['delivered_gmv_brl'] / 1e6:,.2f}m")
    three.metric("90-day repeat purchase", f"{metrics['repeat_90d_rate']:.2%}")
    tabs = st.tabs(["Overview", "Delivery & repeat purchase", "Evidence explorer", "Decision & experiment"])
    with tabs[0]:
        monthly = load_table("mart_monthly").sort_values("month")
        st.subheader("Delivered merchandise value by purchase month")
        st.line_chart(monthly.set_index("month")["delivered_gmv_brl"], color="#38b2ac")
        st.subheader("Fulfillment completion")
        st.dataframe(load_table("mart_fulfillment").sort_values("step"), hide_index=True, width="stretch")
        st.subheader("Largest product categories")
        categories = load_table("mart_categories").nlargest(8, "delivered_gmv_brl")
        st.bar_chart(categories.set_index("category")["delivered_gmv_brl"], horizontal=True, height=360)
        st.caption(
            "GMV is merchandise value. The completion funnel describes fulfillment, not browsing conversion."
        )
    with tabs[1]:
        cohorts = load_table("mart_retention").sort_values("cohort")
        threshold = st.slider("Minimum customers per displayed cohort", 10, 1000, 100, step=10)
        displayed = cohorts[cohorts.eligible_customers >= threshold]
        st.line_chart(displayed.set_index("cohort")["repeat_rate_90d"])
        st.caption(
            f"{len(cohorts) - len(displayed)} small cohorts hidden; all eligible customers remain in headline totals."
        )
        study = ROOT / "reports/delivery_retention_summary.json"
        if study.exists():
            result = json.loads(study.read_text())
            st.subheader("First-order delivery experience and subsequent purchase")
            st.dataframe(result["groups"], hide_index=True, width="stretch")
            st.info(result["decision"])
        delivery = load_table("mart_delivery")
        state = st.selectbox("State", ["All states", *sorted(delivery.state.unique())])
        if state != "All states":
            delivery = delivery[delivery.state == state]
        st.dataframe(delivery, hide_index=True, width="stretch")
        st.caption(
            "Historical associations; delivery exposure is not randomized. See the memo for uncertainty."
        )
    with tabs[2]:
        mode = st.radio("Mode", ["Offline evidence explorer", "Configured LLM"], horizontal=True)
        if mode == "Offline evidence explorer":
            query_id = st.selectbox(
                "Approved question", list(CATALOG), format_func=lambda key: CATALOG[key]["description"]
            )
            packet = evidence(query_id)
            st.dataframe(packet["records"], width="stretch")
            with st.expander("SQL and evidence fingerprints"):
                st.code(packet["sql"], language="sql")
                st.json({k: packet[k] for k in ("sql_sha256", "result_sha256")})
        else:
            question = st.text_input(
                "Question", "Show 90-day repeat purchase rates by eligible customer cohort."
            )
            st.warning(
                "Free-text routing is experimental. Source lookup does not establish relevance. Review the suggested scope before requesting observations."
            )
            if st.button("Suggest evidence scope"):
                try:
                    suggested = route(question)
                    st.session_state["suggested_scope"] = suggested
                    st.session_state["scope_question"] = question
                except (RuntimeError, ValueError, OSError) as error:
                    st.error(str(error))
            suggested = st.session_state.get("suggested_scope")
            if suggested:
                st.info(
                    "Suggested scope: "
                    + (CATALOG[suggested]["description"] if suggested in CATALOG else "Unsupported request")
                )
            approved = st.selectbox(
                "Review and select the evidence scope",
                ["Not reviewed", *CATALOG],
                format_func=lambda key: CATALOG[key]["description"] if key in CATALOG else key,
            )
            confirmed = st.checkbox("I reviewed the scope and understand that it may not answer my question.")
            if st.button("Investigate", disabled=not confirmed or approved == "Not reviewed"):
                try:
                    response = answer(question, query_id=approved)
                    if response["status"] == "unsupported":
                        st.warning(response["message"])
                    else:
                        for observation in response["observations"]:
                            st.write(observation["text"])
                            st.caption(observation["citation"])
                        st.dataframe(response["evidence"]["records"], hide_index=True, width="stretch")
                        st.caption(
                            "The full reviewed result table is shown; the selected cells are not a free-form conclusion."
                        )
                        with st.expander("Source records"):
                            st.json(response["evidence"])
                except (RuntimeError, ValueError, OSError, KeyError) as error:
                    st.error(str(error))
        evaluation = json.loads((ROOT / "reports/ai_evaluation.json").read_text())
        with st.expander("Recorded local-model evaluation"):
            st.json({k: v for k, v in evaluation.items() if k != "results"})
            st.caption("A recorded run is not a live connection. Configure an endpoint for new questions.")
    with tabs[3]:
        st.markdown((ROOT / "reports/decision_memo.md").read_text(encoding="utf-8"))
        with st.expander("Prospective experiment"):
            st.markdown((ROOT / "reports/experiment_memo.md").read_text(encoding="utf-8"))


if __name__ == "__main__":
    main()

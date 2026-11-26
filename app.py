from pathlib import Path
import json
import streamlit as st
import duckdb
from copilot import CATALOG, evidence, answer

ROOT=Path(__file__).resolve().parent
st.set_page_config(page_title='Commerce Intelligence',layout='wide')
st.title('Commerce Intelligence')
st.caption('Olist marketplace · historical real-world data · BRL · purchases before 1 September 2018')
if not (ROOT/'warehouse/commerce.duckdb').exists():
 st.info('Run python pipeline.py all and python analyze.py first.'); st.stop()

@st.cache_data(ttl=60)
def table(name):
 if name not in ['mart_monthly','mart_retention','mart_delivery','mart_fulfillment','mart_categories']: raise ValueError(name)
 with duckdb.connect(str(ROOT/'warehouse/commerce.duckdb'),read_only=True) as db:
  return db.execute('select * from '+name).df()

m=json.loads((ROOT/'reports/metrics.json').read_text())
a,b,c=st.columns(3)
a.metric('Orders',f"{m['orders']:,}"); b.metric('Delivered merchandise GMV',f"R${m['delivered_gmv_brl']:,.0f}")
c.metric('Mature customer repeat purchase, 90d',f"{m['repeat_90d_rate']:.2%}")
tabs=st.tabs(['Business overview','Delivery & retention','Evidence copilot','Decision & experiment'])
with tabs[0]:
 monthly=table('mart_monthly').sort_values('month')
 st.subheader('Delivered merchandise sales'); st.line_chart(monthly.set_index('month')['delivered_gmv_brl'])
 x,y=st.columns(2)
 with x: st.subheader('Fulfillment completion'); st.dataframe(table('mart_fulfillment').sort_values('step'),hide_index=True)
 with y: st.subheader('Category mix'); st.bar_chart(table('mart_categories').nlargest(10,'delivered_gmv_brl').set_index('category')['delivered_gmv_brl'])
 st.caption('GMV is not company revenue. Fulfillment records do not measure website conversion.')
with tabs[1]:
 st.line_chart(table('mart_retention').sort_values('cohort').set_index('cohort')['repeat_rate_90d'])
 st.dataframe(table('mart_delivery'),hide_index=True)
 st.warning('Delivery and reviews are associated observations. They do not prove causation. Cohorts exclude incomplete 90-day windows.')
with tabs[2]:
 mode=st.radio('Mode',['Offline evidence explorer','Configured LLM'],horizontal=True)
 if mode=='Offline evidence explorer':
  query_id=st.selectbox('Approved analytical question',list(CATALOG),format_func=lambda k:CATALOG[k]['description'])
  packet=evidence(query_id); st.dataframe(packet['records']); st.code(packet['sql'],language='sql'); st.caption('Offline mode executes approved SQL and does not call AI.')
 else:
  question=st.text_input('Ask within the documented query catalog','Show 90-day repeat purchase rates by eligible customer cohort.')
  if st.button('Investigate'):
   try:
    response=answer(question)
    if response['status']=='unsupported': st.warning(response['message'])
    else:
     for observation in response['observations']: st.write(observation['text']); st.caption(observation['citation'])
     with st.expander('SQL and source records'): st.json(response['evidence'])
   except Exception as e: st.error(str(e))
 st.caption('External LLM mode sends only approved aggregate results. Configure model and endpoint in environment variables.')
with tabs[3]:
 st.markdown((ROOT/'reports/decision_memo.md').read_text(encoding='utf-8'))
 with st.expander('Experiment design'): st.markdown((ROOT/'reports/experiment_memo.md').read_text(encoding='utf-8'))

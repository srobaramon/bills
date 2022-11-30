python -m venv .venv
call .venv\Scripts\activate
pip install streamlit, streamlit-pandas-profiling
streamlit run https://github.com/srobaramon/bills/blob/main/app.py
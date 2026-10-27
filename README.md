# YouTube research dashboard

A Streamlit application for exploring public YouTube video statistics by search topic and region. It fetches results through the YouTube Data API and displays views, engagement, title sentiment, tags and charts.

## Run

```bash
git clone https://github.com/abhigurjar101/youtube-automation-os.git
cd youtube-automation-os
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

Enable the YouTube Data API in your Google project and provide an API key in the password field in the sidebar. Set a region and RPM assumption, enter a topic, and launch the search. API quotas and provider terms apply. Do not commit API keys.

## Interpretation

Estimated earnings are `views / 1000 × user-supplied RPM`; they are not verified creator revenue. The relative “virality” score is a hand-written weighted statistic normalized within the result set, not a trained forecast. TextBlob sentiment analyzes titles, not the full video or audience response. Search results are a sample ordered by views and do not establish causality or future performance.

## Structure and limitations

- `app.py`: application, API calls, metrics and visualizations
- `AbhiGurjarYTauto.ipynb`: exploratory notebook
- `requirements.txt`: dependencies

The app has no automated API mocks or live integration checks. Empty results, missing fields, quota errors and zero-score normalization need further hardening before public deployment. No performance or revenue outcome is claimed.

[Abhi Kumar Gurjar](https://www.linkedin.com/in/abhigurjar)

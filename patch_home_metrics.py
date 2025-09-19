from pathlib import Path

path = Path('app.py')
text = path.read_text(encoding='utf-8')
old_snippet = """    responses = client.get_responses(survey=survey, limit=30000)
    if not isinstance(responses, pd.DataFrame):
        responses = pd.DataFrame()

    if total is None and not responses.empty:
        total = len(responses)
    if unique is None and not responses.empty and \"pid\" in responses.columns:
        unique = responses[\"pid\"].nunique()
"""
new_snippet = """    responses = client.get_responses(survey=survey, limit=30000)
    if not isinstance(responses, pd.DataFrame):
        responses = pd.DataFrame()

    if not responses.empty and \"pid\" not in responses.columns:
        if \"profile_id\" in responses.columns:
            responses[\"pid\"] = responses[\"profile_id\"]

    if not responses.empty:
        if total is None:
            total = len(responses)
        if (unique is None or unique == 0) and \"pid\" in responses.columns:
            unique = responses[\"pid\"].dropna().nunique()
"""
if old_snippet not in text:
    raise SystemExit('Target snippet not found')
path.write_text(text.replace(old_snippet, new_snippet), encoding='utf-8')

# Contributing

Discuss material changes through an issue before expanding the analytical scope. Include the business question, source fields, intended table grain and proposed validation.

1. Create a branch and make a focused change.
2. Run `python -m pytest tests -q`.
3. For SQL changes, download the full release and run `python pipeline.py all` followed by `python analyze.py`.
4. Update affected definitions, source manifests and result documentation. Explain any changed population or denominator.
5. Submit a pull request describing the result, tests and limitations.

Never commit API keys, raw datasets, local databases or real private customer records. Keep simulated tests clearly labeled. Do not claim production impact, a causal effect or model accuracy that has not been measured. Report security-sensitive defects privately through the repository owner's GitHub contact rather than posting credentials or exploit data in an issue.

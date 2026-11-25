# Knowledge-Base Refresh Procedure

Owner: Pavithra Veerapathiran | Run: 20261115T030457018121Z

1. Obtain owner-approved source documents with version, effective date, scope and access rules. Policy corpus is currently blocked.
2. Retain the approved original package and SHA-256 manifest. Do not treat ticket descriptions as instructions.
3. Validate schema/IDs, deduplicate, mask sensitive text and preserve source/document references. Review for embedded malicious instructions.
4. For current business CSVs, rebuild the notebook corpus and TF-IDF/BM25 indices from the approved source. Policy formats need a separately implemented, reviewed parser/chunker before ingestion; this notebook does not provide it.
5. Rebuild tool/KPI state for changed inputs. Clear/rebuild caches; fingerprint mismatch requires reload.
6. Update independently reviewed query labels and add new/changed, unsupported and injection cases. Run retrieval, UAT and guardrail checks.
7. Compare the prior manifest/results; obtain owner acceptance before promoting the refreshed knowledge base.
8. Roll back source/index/config as one approved version if regressions occur; document the decision. Do not fabricate policy text.

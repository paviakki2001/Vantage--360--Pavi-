# RAG Evaluation Report

Owner: Pavithra Veerapathiran | Run: 20261115T030457018121Z

## Fresh retrieval measurements
method,queries,hit1,hit3,hit5,mean_latency_ms
fusion,25,1.0,1.0,1.0,7.1357304000230215
tfidf,25,1.0,1.0,1.0,4.219098399953509

## Method and coverage
Top-k hit evaluation over existing labelled business questions. TF-IDF is compared with BM25 lexical rank fusion. Query labels share source wording and are not an independent holdout. Out-of-corpus and paraphrase coverage are limited. Human review: False.

## Review and exclusions
See reviews/rag_answer_review.csv and per-query evidence. No policy retrieval score is reported. Hit@k does not establish answer faithfulness or usefulness.

Lexical TF-IDF/BM25 fusion with source-derived labels; no dense semantic retriever, learned reranker or LLM narrative. Role/session inputs are local fixtures. HTTP checks are in-process. Customer support issues are not approved resolution policy. Forecast dates are retained from supplied artifacts. Policy corpus is unavailable. No hosted accessibility or production certification is asserted.

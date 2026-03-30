# Presentation: AI News Verification System (Academic Overview)

## Abstract
The rapid spread of misinformation has increased the need for reliable, automated verification tools. This project presents an AI-powered news verification system that evaluates user-submitted claims by searching multiple news APIs, computing semantic similarity to published articles, and weighting evidence by source credibility. The system provides a verdict (real, fake, uncertain), a confidence score, and attributed sources. It integrates a React frontend, a FastAPI backend, and an SQLite database, and is designed for transparency, reproducibility, and extensibility.

## 1. Introduction
Misinformation undermines trust in media, public health, and governance. Manual fact-checking is labor-intensive and cannot keep pace with real-time news cycles. Automated verification systems aim to assist by triangulating claims against trusted sources and providing evidence-based outputs.

This project targets three objectives:
1. Provide real-time verification of short news claims.
2. Attribute verification to concrete sources with credibility weighting.
3. Offer interpretable outputs that support user decision-making.

## 2. Problem Statement
Given a short news claim (headline or short paragraph), determine whether the claim is supported by credible sources. The system must:
- Retrieve relevant articles from reliable news providers.
- Measure similarity between the claim and retrieved articles.
- Compute a credibility-weighted confidence score.
- Provide an interpretable verdict with source evidence.

## 3. Research Questions
1. Can multi-source retrieval improve verification accuracy compared to a single provider?
2. Does credibility weighting enhance decision reliability when similarity signals are weak?
3. Can semantic similarity (embeddings) reduce false negatives vs. TF-IDF alone?

## 4. System Architecture
The system is divided into three layers:

- **Frontend (React):** Collects user input, displays verification result, sources, and similar news suggestions.
- **Backend (FastAPI):** Orchestrates retrieval, NLP processing, similarity computation, credibility scoring, and decision logic.
- **Database (SQLite):** Stores verification history, fetched sources, and static domain credibility scores.

External dependencies include:
- News APIs: NewsAPI, GNews, MediaStack
- NLP: spaCy (tokenization, NER)
- Similarity: TF-IDF + optional sentence embeddings

## 5. Methodology
### 5.1 Input Processing
User input is validated (10–5000 chars), HTML is stripped, and the normalized text is hashed (SHA256) for caching. A cached result is returned if identical input was verified in the last 24 hours.

### 5.2 Query Expansion
To improve recall, the system generates multiple search queries:
- Keyword extraction (nouns and proper nouns)
- Named entity extraction (PERSON/ORG/GPE/LOC)
- Full-text query
- Synonym expansion (configurable)

### 5.3 Retrieval
The backend queries multiple APIs in parallel. Results are merged and deduplicated by URL. Query load is biased toward NewsAPI and GNews for higher coverage.

### 5.4 Similarity Scoring
Each retrieved article is compared to the input using:
- TF-IDF + cosine similarity
- Sentence embeddings (all-MiniLM-L6-v2) if enabled
A combined similarity score is produced.

### 5.5 Credibility Scoring
Each article’s domain is mapped to a credibility score stored in SQLite. Unknown domains default to 0.5. A weighted credibility score is computed as:

```
credibility = S(similarity_i × credibility_i) / S(similarity_i)
```

### 5.6 Decision Logic
Rules are applied to determine the final verdict:
- **REAL:** If at least one high-credibility source is found.
- **FAKE:** If no sources are found.
- **UNCERTAIN:** Otherwise, using similarity, credibility, and source count.

This logic is intentionally conservative, prioritizing transparent evidence from high-credibility domains.

## 6. Evaluation Criteria
The system is evaluated on:
- Response time (target: <3 seconds p95)
- Precision of classification in manual trials
- Source coverage and diversity
- Robustness to short or ambiguous inputs

## 7. Implementation Details
- **Backend Framework:** FastAPI 0.104+ with async I/O
- **Database:** SQLite with SQLAlchemy ORM
- **Caching:** SHA256 hash with 24h TTL
- **Rate Limiting:** 10 requests/minute/IP
- **Frontend:** React + Vite with custom CSS

## 8. Ethical Considerations
- **Bias Risk:** Credibility scores are subjective and must be regularly reviewed.
- **Transparency:** Users are shown sources to independently verify results.
- **Privacy:** Inputs are stored for history; retention policies should be configurable.

## 9. Limitations
- Reliance on external APIs can introduce coverage gaps.
- Credibility scores may not capture nuanced reliability differences.
- Absence of sources may reflect API failure rather than falsity.

## 10. Future Work
- Integrate fact-checking datasets and knowledge graphs.
- Add multilingual support.
- Improve contradiction detection.
- Provide user feedback loops for model correction.

## 11. Conclusion
This system demonstrates a practical, extensible pipeline for news verification by combining retrieval, similarity modeling, and credibility weighting. Its modular architecture enables future improvements and supports responsible, transparent fact-checking at scale.
# Search & Retrieval Engine

## Overview

The Search & Retrieval Engine is a production-ready, deterministic search layer that allows searching across Candidates and Jobs using keyword, ontology-aware, and hybrid strategies. It is completely stateless at the query level but relies on an in-memory inverted index for fast O(1) or O(log N) retrieval.

## Architecture

The search flow strictly separates retrieval from ranking:
`SearchContext -> SearchStrategy (Retrieval) -> FilterEngine -> RankingAdapter (Scoring) -> ResultFormatter`

### 1. IndexManager & SearchIndex
Instead of a monolithic generic index, we have specific implementations (e.g., `CandidateIndex`, `JobIndex`) sharing a `SearchIndex` interface. The `IndexManager` oversees the lifecycle (building, clearing, invalidation) of these stores.

### 2. SearchContext
Every search query is wrapped in a `SearchContext`. This object holds not only the initial parameters but also collects `SearchMetrics` (latency, drop rates) and tracks exactly which ontology aliases were used to expand the query.

### 3. SearchStrategy
The engine defines a `SearchStrategy` interface. Current implementations include `KeywordSearchStrategy` (exact match) and `OntologySearchStrategy` (expands to aliases and semantic families before matching). This pattern ensures that we can drop in an `ElasticsearchStrategy` or `VectorSearchStrategy` in the future without refactoring the orchestrator API.

### 4. RankingAdapter
To avoid duplicating the robust scoring configurations defined in Phase 2.4, the `RankingAdapter` converts search hits into mock `MatchResult` objects and feeds them directly through the existing `ScoringService`. 

## Future Extensibility
Because the architecture relies heavily on dependency injection (`strategies["hybrid"] = OntologySearchStrategy()`), swapping out the underlying datastore for pgvector, Pinecone, or OpenSearch requires only writing a new class that implements the `SearchStrategy` and `SearchIndex` interfaces.

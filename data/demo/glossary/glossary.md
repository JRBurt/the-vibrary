# Glossary

## Chunk

A chunk is a slice of a document, usually a few hundred to a thousand tokens,
that gets its own embedding vector. Documents are chunked because embedding
an entire long document into a single vector loses too much distinct meaning
to be useful for retrieval.

## Collection

A named grouping of chunks in the index, used to scope a search (for example,
searching only the "skills" collection instead of the whole corpus). Collections
are the coarse boundary; metadata on each chunk provides finer filtering within
a collection.

## Reranking

A second, more precise scoring pass applied to a small set of already-retrieved
candidates. Initial vector search is fast but approximate; a reranker narrows
a larger candidate set down to the few chunks most worth sending to the model.

## Embedding

A fixed-length numeric vector that represents the meaning of a piece of text,
positioned in a high-dimensional space such that semantically similar text
ends up nearby. Retrieval works by comparing the query's embedding against
every chunk's embedding and returning the closest matches.

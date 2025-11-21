# Processing Benchmarks

## Local

### Trial 1

- Document

life_of_johnson.txt

- Size

1.3 MB

- Chunker Config

{"provider":"langchain","chunk_size":300,"chunk_overlap":0,"chunker_type":"token"}

- Time

14.14 seconds
10.88 seconds (1 table instead of 2)

### Trial 2

- Document

collection1.txt

- Size

10.7 MB

- Chunker Config

{"provider":"langchain","chunk_size":300,"chunk_overlap":0,"chunker_type":"token"}

- Time

170.61 seconds
142.12 seconds (1 table instead of 2)

## Description
**slowfuzz** is a small, dependency-free fuzzy string matcher written in pure Python that provides character-level similarity scoring. It is intended for cases where a lightweight Python solution with reasonable performance is preferred.

Using the official RapidFuzz benchmark setup (10,000 ASCII strings of length 10, compared against 100 samples), `ratio` is approximately 9× slower than the RapidFuzz Simple Ratio scorer, but still evaluates about **900,000 word pairs per second**.

`subsequence_ratio` is slower due to tokenization overhead and handles roughly **100,000 word-sentence comparisons per second**.

> Note: Benchmarks were run on Apple Silicon M4.


## Installation
Given you have cloned the repository:
```bash
cd slowfuzz
pip install .
```

## Scorers
There are two scorers in **slowfuzz**. Inputs for both are normalized by default, but this can be disabled using the `normalize` parameter.

### Ratio

```python
import slowfuzz

slowfuzz.ratio("this is a test", "this is a test!")
# 0.9654761904761906
slowfuzz.ratio("test", "test!")
# 0.8875
```

### Subsequence Ratio

```python
import slowfuzz

slowfuzz.subsequence_ratio("test", "this is a test!")
# 1.0
slowfuzz.subsequence_ratio("test", "this is a test!", strip=False)
# 0.8875
```
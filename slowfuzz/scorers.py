import unicodedata


def ratio(s1: str, s2: str, normalize: bool=True) -> float:
    """
    Compute a character-level similarity ratio between two strings.

    Contiguous matches and similar length are rewarded. The score is symmetric, so swapping `s1` and `s2` does not
    change the result.

    :param s1: String to match against `s2`.
    :param s2: String to match against `s1`.
    :param normalize: If True, applies ASCII normalization and lowercases both strings.
    :return: Similarity score in the range [0.0, 1.0].
    """
    s1 = _apply_normalization(s1, normalize)
    s2 = _apply_normalization(s2, normalize)

    if not s1 or not s2:
        return 0.0

    return _compute_ratio(s1, s2)


def subsequence_ratio(w: str, s: str, normalize: bool=True, strip: bool=True) -> float:
    """
    Compute the best character-level similarity ratio between `w` and any token in `s`.

    `s` is tokenized on whitespace and each token is compared to `w` using the same computation as `ratio`.

    :param w: Word to match against `s`. This parameter is not intended for multi-word input.
    :param s: String to search in.
    :param normalize: If True, applies ASCII normalization and lowercases both strings.
    :param strip: If True, strips leading and trailing non-alphanumeric characters from tokens in `s`.
    :return: Similarity score in the range [0.0, 1.0].
    """
    w = _apply_normalization(w, normalize)
    s = _apply_normalization(s, normalize)

    if not w or not s:
        return 0.0

    r = 0.0
    for token in _tokenize(s):
        token = _apply_strip(token, strip)
        if not token:
            continue
        tr = _compute_ratio(w, token)
        if tr > r:
            r = tr
        if r == 1.0:
            break
    return r


def _apply_normalization(s: str, normalize: bool) -> str:
    if not normalize or not s:
        return s
    if s.isascii():
        return s.lower()
    return _normalize(s)


def _normalize(s: str) -> str:
    return (
        unicodedata
        .normalize("NFKD", s)
        .encode("ascii", "ignore")
        .decode("ascii")
        .lower()
    )


def _apply_strip(s: str, strip: bool) -> str:
    if not strip or not s or s.isalnum():
        return s
    return _strip(s)


def _strip(s: str) -> str:
    isalnum = str.isalnum
    start = 0
    end = len(s)
    while start < end and not isalnum(s[start]):
        start += 1
    while end > start and not isalnum(s[end - 1]):
        end -= 1
    return s[start:end]


def _tokenize(s: str) -> list[str]:
    return s.split()


def _compute_ratio(s1: str, s2: str) -> float:
    len1 = len(s1)
    len2 = len(s2)

    # Do forward match
    find = s2.find
    last_i2 = -1
    m_f = c1_f = c2_f = 0
    last_i1_m = last_i2_m = None
    for i1, ch in enumerate(s1):
        i2 = find(ch, last_i2 + 1)
        if i2 < 0:
            continue
        m_f += 1
        if last_i1_m is not None and i1 == last_i1_m + 1:
            c1_f += 1
        if last_i2_m is not None and i2 == last_i2_m + 1:
            c2_f += 1
        last_i1_m = i1
        last_i2_m = last_i2 = i2

    # Do backward match
    rfind = s2.rfind
    last_i2 = len2
    m_b = c1_b = c2_b = 0
    last_i1_m = last_i2_m = None
    for i1 in range(len1 - 1, -1, -1):
        i2 = rfind(s1[i1], 0, last_i2)
        if i2 < 0:
            continue
        m_b += 1
        if last_i1_m is not None and i1 == last_i1_m - 1:
            c1_b += 1
        if last_i2_m is not None and i2 == last_i2_m - 1:
            c2_b += 1
        last_i1_m = i1
        last_i2_m = last_i2 = i2

    # Choose better direction
    if m_f > m_b:
        m, c1, c2 = m_f, c1_f, c2_f
    elif m_b > m_f:
        m, c1, c2 = m_b, c1_b, c2_b
    else:
        if (c1_f + c2_f) >= (c1_b + c2_b):
            m, c1, c2 = m_f, c1_f, c2_f
        else:
            m, c1, c2 = m_b, c1_b, c2_b

    # Compute ratio
    tr1 = m / len1
    tr2 = m / len2
    tr3 = c1 / (len1 - 1) if len1 > 1 else (1.0 if m else 0.0)
    tr4 = c2 / (len2 - 1) if len2 > 1 else (1.0 if m else 0.0)

    return (tr1 + tr2 + tr3 + tr4) * 0.25

import re


def split_into_sentences(text: str) -> list[str]:
    cleaned_text = " ".join(text.split())

    sentences = re.split(
        r"(?<=[.!?])\s+",
        cleaned_text,
    )

    return [
        sentence.strip()
        for sentence in sentences
        if sentence.strip()
    ]


def split_long_sentence(
    sentence: str,
    chunk_size: int,
) -> list[str]:
    chunks = []
    start = 0

    while start < len(sentence):
        end = start + chunk_size
        chunk = sentence[start:end].strip()

        if chunk:
            chunks.append(chunk)

        start = end

    return chunks


def split_text(
    text: str,
    chunk_size: int = 500,
    overlap_sentences: int = 1,
) -> list[str]:
    if chunk_size <= 0:
        raise ValueError(
            "chunk_size must be greater than 0."
        )

    if overlap_sentences < 0:
        raise ValueError(
            "overlap_sentences cannot be negative."
        )

    sentences = split_into_sentences(text)

    if not sentences:
        return []

    chunks = []
    current_sentences = []
    current_length = 0

    for sentence in sentences:
        if len(sentence) > chunk_size:
            if current_sentences:
                chunks.append(
                    " ".join(current_sentences)
                )

                current_sentences = []
                current_length = 0

            long_sentence_chunks = split_long_sentence(
                sentence=sentence,
                chunk_size=chunk_size,
            )

            chunks.extend(long_sentence_chunks)
            continue

        added_length = len(sentence)

        if current_sentences:
            added_length += 1

        if (
            current_length + added_length
            <= chunk_size
        ):
            current_sentences.append(sentence)
            current_length += added_length
        else:
            chunks.append(
                " ".join(current_sentences)
            )

            if overlap_sentences > 0:
                current_sentences = current_sentences[
                    -overlap_sentences:
                ]
            else:
                current_sentences = []

            current_length = len(
                " ".join(current_sentences)
            )

            if current_sentences:
                current_length += 1

            current_sentences.append(sentence)
            current_length += len(sentence)

    if current_sentences:
        chunks.append(
            " ".join(current_sentences)
        )

    return chunks
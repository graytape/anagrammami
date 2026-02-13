import os
from typing import Dict, List, Tuple

from .anagramgen_fork import AnagramGenerator

APP_DIR = os.path.dirname(os.path.abspath(__file__))


# Available corpora per language.
# Keys are logical identifiers used in settings and APIs,
# values are (filename, human_label).
CORPORA: Dict[str, Dict[str, Tuple[str, str]]] = {
    "it": {
        "1000_parole_italiane_comuni": (
            "1000_parole_italiane_comuni.txt",
            "1.000 parole italiane comuni",
        ),
        "60000_parole_italiane": ("60000_parole_italiane.txt", "60.000 parole italiane"),
        "280000_parole_italiane": ("280000_parole_italiane.txt", "280.000 parole italiane"),
        "660000_parole_italiane": ("660000_parole_italiane.txt", "660.000 parole italiane"),
        "986700_parole_uniche": ("986700_parole_uniche.txt", "986.700 parole uniche"),
    },
    "en": {
        "top-5k": ("top-5k.txt", "Top 5k English words"),
        "top-10k": ("top-10k.txt", "Top 10k English words"),
        "top-178k": ("top-178k.txt", "Top 178k English words"),
        "top-370k": ("top-370k.txt", "Top 370k English words"),
    },
}


def get_default_corpus_key(lang: str) -> str:
    """Return the default logical corpus key for a given language."""
    lang = (lang or "it").lower()
    if lang == "en":
        return "top-5k"
    # default for Italian
    return "660000_parole_italiane"


def get_corpora_for_lang(lang: str) -> Dict[str, Tuple[str, str]]:
    """Return the mapping of corpora for a given language code."""
    lang = (lang or "it").lower()
    if lang not in CORPORA:
        lang = "it"
    return CORPORA[lang]


def generate_anagrams(
    word: str,
    lang: str | None = None,
    corpus_key: str | None = None,
    max_results: int | None = None,
    min_word_length: int | None = None,
    max_word_length: int | None = None,
    prioritize_long_words: bool = True,
):
    """
    High-level helper that prepares the corpus and delegates to AnagramGenerator.

    Parameters are intentionally loose to stay backward compatible with
    existing callers (web UI, Telegram bot).
    """

    # Normalize language and pick the directory
    lang = (lang or "it").lower()
    if lang not in ("it", "en"):
        lang = "it"

    folder = "italian" if lang == "it" else "english"
    corpora_for_lang = get_corpora_for_lang(lang)

    # Backward-compatible handling of corpus / corpus_key:
    # - if caller passes a logical key, use it
    # - otherwise use per-language default
    if corpus_key is None:
        corpus_key = get_default_corpus_key(lang)

    # Fallback to default if an unknown key is provided
    if corpus_key not in corpora_for_lang:
        corpus_key = get_default_corpus_key(lang)

    corpus_filename, corpus_label = corpora_for_lang[corpus_key]

    corpus_path = os.path.join(APP_DIR, "data", folder, corpus_filename)
    with open(corpus_path, "r") as file:
        corpus_list: List[str] = [
            line.strip()
            for line in file
            if line.strip() and line.strip().isalpha()
        ]

    generator = AnagramGenerator(corpus_list, corpus_name=corpus_label)

    # Internal cap for search space: independent from user-facing max_results.
    # The user-facing "number of results" should act on the *final* list,
    # not on the raw generation depth/limit.
    internal_max_results = 10000

    results = generator.generate(
        word,
        max_results=internal_max_results,
        timeout=30,
        prioritize_long_words=prioritize_long_words,
        min_word_length=min_word_length,
        max_word_length=max_word_length,
    )

    # Convert nested list of words to strings for consumers (web UI, Telegram)
    results["anagrams"] = [
        " ".join(anagram) for anagram in results.get("anagrams", [])
    ]

    if max_results is not None:
        results["anagrams"] = results["anagrams"][: max_results]

    # Ensure n_results reflects the final, possibly truncated list
    results["n_results"] = len(results["anagrams"])

    # Also expose which corpus key was used, for UI / Telegram
    results["corpus_key"] = corpus_key

    return results

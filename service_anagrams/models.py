from django.db import models
from django.conf import settings


class UserAnagramSettings(models.Model):
    """
    Per-user configuration for anagram generation.

    These settings are used both by the web UI (hints)
    and can be reused by other services if needed.
    """

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="anagram_settings",
    )

    # Logical key of the corpus within the selected language
    # (e.g. "660000_parole_italiane", "top-5k", etc.)
    corpus_key = models.CharField(max_length=100, default="660000_parole_italiane")

    # Constraints on generated anagram words
    min_word_length = models.PositiveIntegerField(default=2)
    max_word_length = models.PositiveIntegerField(default=20)

    # Whether to prioritize longer words when ordering results
    prioritize_long_words = models.BooleanField(default=True)

    # Maximum number of anagram results to return
    max_results = models.PositiveIntegerField(default=500)

    def __str__(self) -> str:
        return f"Settings for {self.user!s}"


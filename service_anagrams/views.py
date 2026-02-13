import json
from urllib.parse import unquote

from django.http import JsonResponse
from django.views.decorators.http import require_GET, require_POST

from .models import UserAnagramSettings
from .utils import (
    generate_anagrams,
    get_corpora_for_lang,
    get_default_corpus_key,
)


@require_GET
def fetch_hints(request, lang, chars):
    """
    Compute anagrams for the unused characters and return hints plus stats.

    If the user is authenticated and has saved settings, those are applied.
    Otherwise reasonable defaults are used.
    """
    chars = chars.strip()

    # Base language and defaults
    lang = (lang or "it").lower()

    # Try to load per-user settings if available
    settings_kwargs = {}
    if request.user.is_authenticated:
        try:
            user_settings = UserAnagramSettings.objects.get(user=request.user)
        except UserAnagramSettings.DoesNotExist:
            user_settings = None

        if user_settings:
            settings_kwargs = {
                "corpus_key": user_settings.corpus_key or get_default_corpus_key(lang),
                "min_word_length": user_settings.min_word_length,
                "max_word_length": user_settings.max_word_length,
                "prioritize_long_words": user_settings.prioritize_long_words,
                "max_results": user_settings.max_results,
            }
    else:
        # Anonymous users: if a settings cookie is present, use it
        raw_cookie = request.COOKIES.get("anagram_settings")
        if raw_cookie:
            # Cookie value is URL-encoded JSON from the frontend
            try:
                decoded = unquote(raw_cookie)
                cookie_data = json.loads(decoded)
            except json.JSONDecodeError:
                cookie_data = None

            if isinstance(cookie_data, dict):
                def _to_int(value, default):
                    try:
                        return int(value)
                    except (TypeError, ValueError):
                        return default

                corpora_for_lang = get_corpora_for_lang(lang)
                corpus_key = cookie_data.get("corpus_key") or get_default_corpus_key(lang)
                if corpus_key not in corpora_for_lang:
                    corpus_key = get_default_corpus_key(lang)

                min_word_length = _to_int(cookie_data.get("min_word_length"), 2)
                max_word_length = _to_int(cookie_data.get("max_word_length"), 20)
                max_results = _to_int(cookie_data.get("max_results"), 500)

                if min_word_length < 1:
                    min_word_length = 1
                if max_word_length < min_word_length:
                    max_word_length = min_word_length
                if max_results < 1:
                    max_results = 1

                prioritize_long_words = bool(cookie_data.get("prioritize_long_words", True))

                settings_kwargs = {
                    "corpus_key": corpus_key,
                    "min_word_length": min_word_length,
                    "max_word_length": max_word_length,
                    "prioritize_long_words": prioritize_long_words,
                    "max_results": max_results,
                }

    hints = generate_anagrams(
        chars,
        lang,
        **settings_kwargs,
    )

    return JsonResponse(
        {
            "status": "success",
            "hints_html": hints.get("anagrams", []),
            "n_results": hints.get("n_results", 0),
            "recursions": hints.get("recursion", 0),
            "corpus": hints.get("corpus"),
            "corpus_key": hints.get("corpus_key"),
        }
    )


@require_GET
def get_user_settings(request):
    """
    Return current user settings and available corpora for the active language.

    Anonymous users receive default (non-persisted) values.
    """
    lang = getattr(request, "LANGUAGE_CODE", None) or request.GET.get("lang") or "it"
    lang = lang.lower()

    corpora_for_lang = get_corpora_for_lang(lang)

    if request.user.is_authenticated:
        settings_obj, _ = UserAnagramSettings.objects.get_or_create(
            user=request.user,
            defaults={"corpus_key": get_default_corpus_key(lang)},
        )
        settings_data = {
            "corpus_key": settings_obj.corpus_key,
            "min_word_length": settings_obj.min_word_length,
            "max_word_length": settings_obj.max_word_length,
            "prioritize_long_words": settings_obj.prioritize_long_words,
            "max_results": settings_obj.max_results,
        }
    else:
        # Anonymous: just send sensible defaults (not stored in DB)
        default_key = get_default_corpus_key(lang)
        settings_data = {
            "corpus_key": default_key,
            "min_word_length": 2,
            "max_word_length": 20,
            "prioritize_long_words": True,
            "max_results": 500,
        }

    corpora_list = [
        {"key": key, "label": label}
        for key, (filename, label) in corpora_for_lang.items()
    ]

    return JsonResponse(
        {
            "status": "success",
            "settings": settings_data,
            "corpora": corpora_list,
            "is_authenticated": request.user.is_authenticated,
        }
    )


@require_POST
def save_user_settings(request):
    """
    Persist personal settings for the authenticated user.
    """
    if not request.user.is_authenticated:
        return JsonResponse(
            {
                "status": "error",
                "message": "Authentication required to save personal settings.",
            },
            status=403,
        )

    try:
        data = json.loads(request.body or "{}")
    except json.JSONDecodeError:
        data = {}

    lang = getattr(request, "LANGUAGE_CODE", None) or data.get("lang") or "it"
    lang = str(lang).lower()

    corpora_for_lang = get_corpora_for_lang(lang)

    corpus_key = data.get("corpus_key") or get_default_corpus_key(lang)
    if corpus_key not in corpora_for_lang:
        corpus_key = get_default_corpus_key(lang)

    def _to_int(value, default):
        try:
            return int(value)
        except (TypeError, ValueError):
            return default

    min_word_length = _to_int(data.get("min_word_length"), 2)
    max_word_length = _to_int(data.get("max_word_length"), 20)
    max_results = _to_int(data.get("max_results"), 500)

    # Basic sanity checks
    if min_word_length < 1:
        min_word_length = 1
    if max_word_length < min_word_length:
        max_word_length = min_word_length
    if max_results < 1:
        max_results = 1

    prioritize_long_words = bool(data.get("prioritize_long_words", True))

    settings_obj, _ = UserAnagramSettings.objects.get_or_create(user=request.user)
    settings_obj.corpus_key = corpus_key
    settings_obj.min_word_length = min_word_length
    settings_obj.max_word_length = max_word_length
    settings_obj.max_results = max_results
    settings_obj.prioritize_long_words = prioritize_long_words
    settings_obj.save()

    return JsonResponse(
        {
            "status": "success",
            "settings": {
                "corpus_key": settings_obj.corpus_key,
                "min_word_length": settings_obj.min_word_length,
                "max_word_length": settings_obj.max_word_length,
                "prioritize_long_words": settings_obj.prioritize_long_words,
                "max_results": settings_obj.max_results,
            },
        }
    )

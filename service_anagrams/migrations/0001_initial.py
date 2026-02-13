import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="UserAnagramSettings",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("corpus_key", models.CharField(default="660000_parole_italiane", max_length=100)),
                ("min_word_length", models.PositiveIntegerField(default=2)),
                ("max_word_length", models.PositiveIntegerField(default=20)),
                ("prioritize_long_words", models.BooleanField(default=True)),
                ("max_results", models.PositiveIntegerField(default=500)),
                (
                    "user",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="anagram_settings",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
        ),
    ]



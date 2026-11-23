from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

from reconcile.importer import import_all


class Command(BaseCommand):
    help = "Import locations.csv, system_a.csv and system_b.csv (idempotent)."

    def add_arguments(self, parser):
        parser.add_argument("--dir", default=str(Path(settings.BASE_DIR) / "data"))

    def handle(self, *args, **opts):
        s = import_all(opts["dir"])
        self.stdout.write(
            f"A: {s['a_read']} read, {s['a_saved']} saved; "
            f"B: {s['b_read']} read, {s['b_saved']} saved; "
            f"values left empty: {s['values_left_empty']}; refs cleaned: {s['refs_cleaned']}; "
            f"A actor_id null: {s['actor_null']}")
        if s["a_read"] != s["a_saved"] or s["b_read"] != s["b_saved"]:
            raise CommandError("read != saved: rows were lost")

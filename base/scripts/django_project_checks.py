from __future__ import absolute_import, division, print_function, unicode_literals

import os
import subprocess
import sys
import warnings
from collections import defaultdict
from collections.abc import MutableMapping, MutableSequence, MutableSet
from importlib import import_module


def check_migrations():
    import django

    django.setup()

    from django.apps import apps
    from django.db.migrations.autodetector import MigrationAutodetector
    from django.db.migrations.executor import MigrationExecutor
    from django.db.migrations.state import ProjectState

    executor = MigrationExecutor(connection=None)
    conflicts = executor.loader.detect_conflicts()
    if conflicts:
        name_str = "; ".join(
            "%s in %s" % (", ".join(names), app) for app, names in conflicts.items()
        )
        sys.stdout.write(
            "Conflicting migrations detected; multiple leaf nodes in the "
            "migration graph: (%s).\nTo fix them run "
            "'python manage.py makemigrations --merge'" % name_str
        )
        return conflicts

    autodetector = MigrationAutodetector(
        executor.loader.project_state(), ProjectState.from_apps(apps)
    )
    changes = autodetector.changes(graph=executor.loader.graph)
    if changes:
        sys.stdout.write(
            "Your models have changes that are not yet reflected in a migration.\n"
        )
        for app_label, migrations in changes.items():
            sys.stdout.write("\n========== {} ==========\n".format(app_label))
            for migration in migrations:
                for operation in migration.operations:
                    sys.stdout.write("    - {}\n".format(operation.describe()))
        return 1

    untracked_files = set(
        subprocess.check_output(
            ["git", "ls-files", "--exclude-standard", "--others", "--full-name"],
            encoding="utf8",
        ).splitlines()
    )
    if untracked_files:
        untracked_migration_files = []
        for app_label, migration_name in executor.loader.graph.leaf_nodes():
            module_name, _ = executor.loader.migrations_module(app_label)
            migration_file, ext = os.path.splitext(
                import_module("{}.{}".format(module_name, migration_name)).__file__
            )
            if ext != ".py":
                ext = ".py"
            migration_file_path = migration_file + ext

            if any(
                migration_file_path.endswith(untracked_file)
                for untracked_file in untracked_files
            ):
                untracked_migration_files.append(migration_file_path)

        if untracked_migration_files:
            sys.stdout.write("Untracked migration files detected.")
            return "\n".join(untracked_migration_files)

    proj_apps = []

    for a in apps.app_configs.values():
        if "site-packages" not in a.path:
            proj_apps.append(a.label)

    all_proj_migations = defaultdict(list)
    for node, _ in executor.loader.graph.nodes.items():
        label, migration_name = node
        if label in proj_apps:
            all_proj_migations[label].append(migration_name)

    discontinuity = defaultdict(list)
    for app_label, migrations in all_proj_migations.items():
        migration_seq = {
            int(migration_name.split("_", 1)[0]): migration_name
            for migration_name in sorted(migrations)
        }
        sequences = list(migration_seq.keys())
        for cur_seq, next_seq in zip(sequences, sequences[1:]):
            if next_seq - cur_seq > 1:
                discontinuity[app_label].append(
                    (migration_seq[cur_seq], migration_seq[next_seq])
                )

    if discontinuity:
        for app_label in sorted(discontinuity):
            print(f"Discontinuity detected in {app_label} migrations.")
            for pair in discontinuity[app_label]:
                print(f"    {pair[0]} -> {pair[1]}")
        return 1


def check_mutable_defaults():
    from django.apps import apps

    mutables = (MutableMapping, MutableSequence, MutableSet)
    mutable_fields = []
    for m in apps.get_models(True, True):
        for f in m._meta.get_fields(include_hidden=True):
            if hasattr(f, "get_default"):
                default = f.get_default()
                if isinstance(default, mutables):
                    if id(default) == id(f.get_default()):
                        mutable_fields.append(str(f))
    if mutable_fields:
        sys.stdout.write(
            "You have field defaults referencing same object.\n"
            "Fix it by having a callable as default."
        )
        return mutable_fields


def check_arrayfields():
    """
    Defining ArrayField using existing field will give strange errors
    during tests.
    This check is until we figure out the actual bug or
    able to reproduce the bug consistently.
    """
    from django.apps import apps
    from django.contrib.postgres.fields import ArrayField

    culprits = []
    for m in apps.get_models(True, True):
        fields = m._meta.get_fields(include_hidden=True)
        for f in fields:
            if not isinstance(f, ArrayField):
                continue

            if f.base_field in fields:
                culprits.append(str(f))

    if culprits:
        sys.stdout.write("Do not use an existing field to define ArrayField.\n")
        return culprits


def run_system_checks():
    from django.core.management import execute_from_command_line
    from django.core.management.base import SystemCheckError

    try:
        execute_from_command_line(["manage.py", "check"])
    except SystemCheckError as e:
        return str(e)


def print_warnings(warns, include_third_party=True):
    warn = False
    for warning in warns:
        if not include_third_party and "site-packages" in warning.filename:
            continue
        print(
            f"{warning.filename}:{warning.lineno} -> {warning.message}", file=sys.stdout
        )
        warn = True
    return warn


def main():
    sys.path.append(os.path.dirname(os.path.dirname(__file__)))
    # setdefault will break. trust me.
    os.environ["DJANGO_SETTINGS_MODULE"] = "settings"

    from django.utils.deprecation import RemovedInNextVersionWarning

    warnings.filterwarnings("default", category=RemovedInNextVersionWarning)

    with warnings.catch_warnings(record=True) as w:
        return (
            check_migrations()
            or check_mutable_defaults()
            or check_arrayfields()
            or run_system_checks()
            or print_warnings(w, bool(os.getenv("INCLUDE_THIRD_PARTY")))
        )


if __name__ == "__main__":
    sys.exit(main())

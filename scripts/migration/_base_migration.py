import _load_app
import peewee as p
from playhouse import migrate
from app.db import DB

# Documentation: http://peewee.readthedocs.org/en/latest/peewee/playhouse.html#schema-migrations

# Example migrations:
# migrator.add_column("table_name", "column_name", p.Charfield(default=""))
# migrator.drop_column("table_name", "column_name")
# migrator.rename_column("table_name", "column_name", "new_column_name")
# migrator.add_index("table_name", ("column_1", "column_2"), True)
# migrator.drop_not_null("table_name", "column_name")
# migrator.add_not_null("table_name", "column_name")

# Note: All fields must either be nullable or have a default

migrator = migrate.MySQLMigrator(DB)

with DB.atomic():
    migrate.migrate(
        # Migrations go here
    )

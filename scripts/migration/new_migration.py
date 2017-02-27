import os
import sys
import time
import shutil


def new_migration(migration_name):
    dirname = os.path.dirname(os.path.realpath(__file__))
    timestamp = str(int(time.time()))
    shutil.copy(dirname + "/_base_migration.py", dirname + "/migration-" + timestamp + "-" + migration_name + ".py")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print "new_migration.py <migration name>"
        exit(1)
    new_migration(sys.argv[1])

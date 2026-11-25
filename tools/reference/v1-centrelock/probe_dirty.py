r"""Read-only: list documents with unsaved changes."""
from lockcommon import *  # noqa: F401,F403
for p, u in open_docs():
    if u: print("  UNSAVED", p)

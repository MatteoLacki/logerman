import json
from pathlib import Path


class PathlibFriendlyEncoder(json.JSONEncoder):
    """This helps to store the paths."""
    def default(self, z):
        if isinstance(z, Path):
            return str(z.expanduser().resolve())
        else:
            return super().default(z)

def dump2json(obj):
    return json.dumps(obj, cls=PathlibFriendlyEncoder)
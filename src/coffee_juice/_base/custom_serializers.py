import json
import uuid
from datetime import datetime
from functools import partial
from typing import Any


class JSONCustomEncoder(json.JSONEncoder):
    def default(self, obj: Any) -> str:
        if isinstance(obj, uuid.UUID):
            return str(obj)
        elif isinstance(obj, datetime):
            return obj.isoformat()
        return json.JSONEncoder.default(self, obj)


json_serializer = partial(json.dumps, cls=JSONCustomEncoder)

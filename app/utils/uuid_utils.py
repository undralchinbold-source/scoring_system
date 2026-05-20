import uuid as _uuid


def parse_uuid(value):
    return _uuid.UUID(value) if value else None

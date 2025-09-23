from .repository import add, list_recent

def audit(actor_type, actor_id, action, entity, entity_id=None, meta=None):
    return add(actor_type, actor_id, action, entity, entity_id, meta)

def list_audit():
    return list_recent()

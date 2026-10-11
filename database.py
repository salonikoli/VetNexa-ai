# In-memory database (replaces MongoDB — no external connection required)


class InMemoryCollection:
    """A minimal in-memory replacement for a MongoDB collection."""

    def __init__(self):
        self._data = {}  # keyed by user "id" field

    def find_one(self, query: dict):
        for doc in self._data.values():
            if all(doc.get(k) == v for k, v in query.items()):
                return doc
        return None

    def insert_one(self, doc: dict):
        key = doc.get("id") or doc.get("email", str(len(self._data)))
        self._data[key] = dict(doc)

    def update_one(self, query: dict, update: dict):
        doc = self.find_one(query)
        if doc is None:
            return
        key = doc.get("id") or doc.get("email")
        if "$push" in update:
            for field, value in update["$push"].items():
                self._data[key].setdefault(field, []).append(value)
        if "$set" in update:
            for field, value in update["$set"].items():
                self._data[key][field] = value


users_collection = InMemoryCollection()

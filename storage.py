from sqlitedict import SqliteDict

class Store:
    def __init__(self, path="resume.db"):
        self.db = SqliteDict(path, autocommit=True)

    def get_profile(self, user_id):
        return self.db.get(str(user_id), {"contact":{"name":"","email":"","phone":"","location":"","links":[]},
                                          "summary":"","skills":{"core":[],"tools":[],"certs":[]},
                                          "experience":[],"education":[]})

    def set_profile(self, user_id, profile):
        self.db[str(user_id)] = profile

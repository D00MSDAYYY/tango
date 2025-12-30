import tinydb as tdb


db = tdb.TinyDB("test.json")
pages = db.table("pages")
pages.insert({"car": "toyota"})

# doc_list = db.table("pages").search(tdb.where("name") == self.name)

from database.common.models import db, History

with db.connection_context():
    db.create_tables([History])

from datetime import datetime
from .. import db
from .user import business_follower_table

business_type_table = db.Table('business_type_table',
    db.Column('id', db.Integer, primary_key=True, autoincrement=True),
    db.Column('public_id', db.String(100), unique=True),
    db.Column('business_pid', db.String(100), db.ForeignKey('business.public_id')),
    db.Column('type_pid', db.String(100), db.ForeignKey('business_type.public_id')),
    db.Column('registered_on', db.DateTime, nullable=False, default=datetime.utcnow)
)

class Business(db.Model):
    __tablename__ = "business"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    public_id = db.Column(db.String(100), unique=True, nullable=False)
    name = db.Column(db.String(50), nullable=False)
    registered_on = db.Column(db.DateTime, nullable=False)
    bio = db.Column(db.String(100))
    photo = db.Column(db.String(50))

    prop_business_rel = db.relationship('BusinessType', secondary=business_type_table, lazy="joined")
    prop_operation_rel = db.relationship('BusinessOperation', cascade="all,delete", lazy="joined")
    user_follower_rel = db.relationship('User', secondary=business_follower_table, cascade="save-update", lazy="joined")
    post_confiner_rel = db.relationship('Post', cascade="save-update", lazy="joined")
    notification_subject_rel = db.relationship("Notification", cascade="all,delete", lazy="joined")
    
    def __repr__(self):
        return "<Business '{}'>".format(self.name)
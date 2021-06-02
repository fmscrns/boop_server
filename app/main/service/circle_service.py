import uuid
import datetime
from sqlalchemy import func
from sqlalchemy.sql.functions import user

from app.main import db
from app.main.model.circle import Circle, circle_type_table
from app.main.model.circle_type import CircleType
from app.main.model.user import User, circle_member_table

def save_new_circle(user_pid, data):
    try:
        circle_pid = str(uuid.uuid4())
        new_circle = Circle(
            public_id = circle_pid,
            name = data.get("name"),
            bio = data.get("bio"),
            photo = data.get("photo"),
            registered_on = datetime.datetime.utcnow()
        )
        model_save_changes(new_circle)
        for _type in data.get("_type"):
            statement = circle_type_table.insert().values(
                public_id = str(uuid.uuid4()),
                circle_pid = circle_pid,
                type_pid = _type["public_id"]
            )
            table_save_changes(statement)
        statement = circle_member_table.insert().values(
            public_id = str(uuid.uuid4()),
            circle_pid = circle_pid,
            member_pid = user_pid,
            is_accepted = True,
            is_admin = True
        )
        table_save_changes(statement)
        response_object = {
            'status': 'success',
            'message': 'Circle successfully registered.',
            'payload': User.query.filter_by(public_id=user_pid).first().username
        }
        return response_object, 201
    except:
        return 500

def get_all_circles_by_user(user_pid):
    return [
        dict(
            public_id = circle[0],
            name = circle[1],
            bio = circle[2],
            _type = [
                dict(
                    type_pid = _type[0],
                    type_name = _type[1]
                ) for _type in db.session.query(
                    circle_type_table.c.type_pid, 
                    CircleType.name
                    ).filter(circle_type_table.c.circle_pid==circle[0]
                    ).filter(circle_type_table.c.type_pid==CircleType.public_id
                    ).all()
            ],
            photo = circle[3],
            registered_on = circle[4],
            admin_id = circle[5],
            admin_name = circle[6],
            admin_username = circle[7],
            admin_photo = circle[8]
        ) for circle in db.session.query(
            Circle.public_id,
            Circle.name,
            Circle.bio,
            Circle.photo,
            Circle.registered_on,
            User.public_id,
            User.name,
            User.username,
            User.photo
        ).filter(
            circle_member_table.c.member_pid == user_pid
        ).filter(
            User.public_id == circle_member_table.c.member_pid
        ).filter(
            Circle.public_id == circle_member_table.c.circle_pid
        ).order_by(Circle.registered_on.desc()).all()
    ]

def create_circle_member(user_pid, public_id):
    circle = Circle.query.filter_by(public_id=public_id).first()
    if circle:
        member = db.session.query(
            circle_member_table
        ).filter(
            circle_member_table.c.circle_pid == public_id
        ).filter(
            circle_member_table.c.member_pid == user_pid
        ).first()

        if not member:
            statement = circle_member_table.insert().values(
                public_id=str(uuid.uuid4()),
                circle_pid=public_id,
                member_pid=user_pid
            )
            table_save_changes(statement)
            response_object = {
                'status': 'success',
                'message': 'Circle member successfully registered.'
            }
            return response_object, 201
        else:
            response_object = {
                'status': 'fail',
                'message': 'Circle member already exists.',
            }
            return response_object, 409
    else:
        response_object = {
            'status': 'fail',
            'message': 'No circle found.'
        }
        return response_object, 404

def delete_circle_member(user_pid, public_id, member_id):
    circle = Circle.query.filter_by(public_id=public_id).first()
    if circle:
        admin = db.session.query(
            circle_member_table
        ).filter(
            circle_member_table.c.circle_pid == public_id
        ).filter(
            circle_member_table.c.is_admin == True
        ).first()

        member = db.session.query(
            circle_member_table
        ).filter(
            circle_member_table.c.circle_pid == public_id
        ).filter(
            circle_member_table.c.member_pid == user_pid
        ).first()

        member_list_length = db.session.query(
            func.count(circle_member_table.c.public_id)
        ).scalar()

        if member:
            if (admin[3] == user_pid and member_list_length != 1) or (user_pid == member_id):
                statement = circle_member_table.delete().where(
                    circle_member_table.c.member_pid==member_id
                ).where(
                    circle_member_table.c.circle_pid==public_id
                )
                table_save_changes(statement)
                response_object = {
                    'status': 'success',
                    'message': 'Circle member successfully deleted.'
                }
                return response_object, 201
            else:
                response_object = {
                    'status': 'fail',
                    'message': 'Request unauthorized.',
                }
                return response_object, 401
        else:
            response_object = {
                'status': 'fail',
                'message': 'Circle member does not exist.',
            }
            return response_object, 404
    else:
        response_object = {
            'status': 'fail',
            'message': 'No circle found.'
        }
        return response_object, 404

def accept_circle_member(user_pid, public_id, member_id):
    circle = Circle.query.filter_by(public_id=public_id).first()
    if circle:
        admin = db.session.query(
            circle_member_table
        ).filter(
            circle_member_table.c.circle_pid == public_id
        ).filter(
            circle_member_table.c.member_pid == user_pid
        ).filter(
            circle_member_table.c.is_admin == True
        ).first()

        member = db.session.query(
            circle_member_table
        ).filter(
            circle_member_table.c.circle_pid == public_id
        ).filter(
            circle_member_table.c.member_pid == member_id
        ).first()

        if admin and member:
            statement = circle_member_table.update().where(
                circle_member_table.c.member_pid==member_id
            ).where(
                circle_member_table.c.circle_pid==public_id
            ).values(
                is_accepted = True
            )
            table_save_changes(statement)
            response_object = {
                'status': 'success',
                'message': 'Circle member successfully accepted.'
            }
            return response_object, 201
        else:
            response_object = {
                'status': 'fail',
                'message': 'Request unauthorized.',
            }
            return response_object, 401
    else:
        response_object = {
            'status': 'fail',
            'message': 'No circle found.'
        }
        return response_object, 404

def get_all_circle_members(public_id, type):
    circle = Circle.query.filter_by(public_id=public_id).first()
    if circle:
        return db.session.query(
            User
        ).filter(
            circle_member_table.c.circle_pid == public_id
        ).filter(
            circle_member_table.c.member_pid == User.public_id
        ).filter(
            circle_member_table.c.is_accepted == (False if type == "0" else True)
        ).all()

    else:
        response_object = {
            'status': 'fail',
            'message': 'No circle found.'
        }
        return response_object, 404

def patch_a_circle(public_id, user_pid, data):
    circle = Circle.query.filter_by(public_id=public_id).first()

    if circle:
        if circle.user_admin_id == user_pid:
            statement = circle_type_table.delete().where(
                circle_type_table.c.circle_pid==circle.public_id)
            db.session.execute(statement)
            db.session.commit()
            for _type in data.get("_type"):
                statement = circle_type_table.insert().values(
                    public_id = str(uuid.uuid4()),
                    circle_pid = circle.public_id,
                    type_pid = _type["public_id"]
                )
                db.session.execute(statement)
                db.session.commit()
            circle.name = data.get("name")
            circle.bio = data.get("bio")
            circle.photo = data.get("photo")
            db.session.commit()
            response_object = {
                'status': 'success',
                'message': 'Circle successfully updated.'
            }
            return response_object, 201
    else:
        response_object = {
            'status': 'fail',
            'message': 'No circle found.'
        }
        return response_object, 404

def delete_a_circle(public_id, user_pid, data):
    circle = Circle.query.filter_by(public_id=public_id).first()
    if circle:
        if circle.user_admin_id == user_pid and data.get("name") == circle.name:
            db.session.delete(circle)
            db.session.commit()
            response_object = {
                'status': 'success',
                'message': 'Circle successfully deleted.'
            }
            return response_object, 201
        else:
            response_object = {
                'status': 'fail',
                'message': 'Not match or no authorization.'
            }
            return response_object, 401
    else:
        response_object = {
            'status': 'fail',
            'message': 'No circle found.'
        }
        return response_object, 404

def get_all_circles():
    return Circle.query.all()

def get_a_circle(user_pid, public_id):
    circle = db.session.query(
        Circle.public_id,
        Circle.name,
        Circle.bio,
        Circle.photo,
        Circle.registered_on,
        User.public_id,
        User.name,
        User.username,
        User.photo
    ).filter(
        Circle.public_id == public_id
    ).filter(
        circle_member_table.c.circle_pid == public_id
    ).filter(
        circle_member_table.c.is_admin == True
    ).filter(
        User.public_id == circle_member_table.c.member_pid
    ).first()

    if circle:
        return dict(
            public_id = circle[0],
            name = circle[1],
            bio = circle[2],
            _type = [
                dict(
                    type_pid = _type[0],
                    type_name = _type[1]
                ) for _type in db.session.query(
                    circle_type_table.c.type_pid, 
                    CircleType.name
                    ).filter(circle_type_table.c.circle_pid==circle[0]
                    ).filter(circle_type_table.c.type_pid==CircleType.public_id
                    ).all()
            ],
            photo = circle[3],
            registered_on = circle[4],
            admin_id = circle[5],
            admin_name = circle[6],
            admin_username = circle[7],
            admin_photo = circle[8],
            visitor_auth = 2 if db.session.query(
                circle_member_table
            ).filter(
                circle_member_table.c.circle_pid == public_id
            ).filter(
                circle_member_table.c.member_pid == user_pid
            ).filter(
                circle_member_table.c.is_accepted == True
            ).first() else 1 if db.session.query(
                circle_member_table
            ).filter(
                circle_member_table.c.circle_pid == public_id
            ).filter(
                circle_member_table.c.member_pid == user_pid
            ).filter(
                circle_member_table.c.is_accepted == False
            ).first() else 0
        )

def model_save_changes(data):
    db.session.add(data)
    db.session.commit()

def table_save_changes(statement):
    db.session.execute(statement)
    db.session.commit()
from flask.globals import request
from app.main.service import table_save_changes
import uuid
from app.main import db
from app.main.model.pet import Pet
from app.main.model.user import User, pet_follower_table

def create_pet_follower(user_pid, pet_pid):
    pet = Pet.query.filter_by(public_id=pet_pid).first()
    if pet:
        follower = db.session.query(
            pet_follower_table
        ).filter(
            pet_follower_table.c.follower_pid == user_pid
        ).filter(
            pet_follower_table.c.pet_pid == pet_pid
        ).first()

        if not follower:
            statement = pet_follower_table.insert().values(
                public_id=str(uuid.uuid4()),
                follower_pid=user_pid,
                pet_pid=pet_pid,
                is_accepted=(True if pet.is_private == 0 else False)
            )
            table_save_changes(statement)
            response_object = {
                'status': 'success',
                'message': 'Pet successfully followed.'
            }
            return response_object, 201
        else:
            response_object = {
                'status': 'fail',
                'message': 'Pet already followed.',
            }
            return response_object, 409
    else:
        response_object = {
            'status': 'fail',
            'message': 'No pet found.'
        }
        return response_object, 404

def get_all_pet_followers(pet_pid, type):
    pet = Pet.query.filter_by(public_id=pet_pid).first()
    if pet:
        return db.session.query(
            User
        ).filter(
            pet_follower_table.c.pet_pid == pet_pid
        ).filter(
            pet_follower_table.c.follower_pid == User.public_id
        ).filter(
            pet_follower_table.c.is_accepted == (False if type == "0" else True)
        ).filter(
            pet_follower_table.c.is_owner == False
        ).all()

    else:
        response_object = {
            'status': 'fail',
            'message': 'No pet found.'
        }
        return response_object, 404

def create_pet_owner(user_pid, pet_pid, data):
    pet = Pet.query.filter_by(public_id=pet_pid).first()
    if pet:
        user = User.query.filter_by(public_id=data.get("public_id")).first()
        admin = db.session.query(
            pet_follower_table
        ).filter(
            pet_follower_table.c.follower_pid == user_pid
        ).filter(
            pet_follower_table.c.pet_pid == pet_pid
        ).filter(
            pet_follower_table.c.is_owner == True
        ).first()

        if user and admin:
            owner = db.session.query(
                pet_follower_table
            ).filter(
                pet_follower_table.c.follower_pid == data.get("public_id")
            ).filter(
                pet_follower_table.c.pet_pid == pet_pid
            ).filter(
                pet_follower_table.c.is_owner == True
            ).first()

            if not owner:
                statement = pet_follower_table.insert().values(
                    public_id=str(uuid.uuid4()),
                    follower_pid=data.get("public_id"),
                    pet_pid=pet_pid,
                    is_accepted=True,
                    is_owner=True
                )
                table_save_changes(statement)
                response_object = {
                    'status': 'success',
                    'message': 'Pet successfully have new owner.'
                }
                return response_object, 201
            else:
                response_object = {
                    'status': 'fail',
                    'message': 'User is already an owner of the pet.',
                }
                return response_object, 409
        else:
            response_object = {
                'status': 'fail',
                'message': 'User does not exist.',
            }
            return response_object, 404
    else:
        response_object = {
            'status': 'fail',
            'message': 'No pet found.'
        }
        return response_object, 404

def delete_pet_follower(user_pid, pet_pid, follower_pid, data):
    pet = Pet.query.filter_by(public_id=pet_pid).first()
    if pet:
        requestor = db.session.query(
            pet_follower_table
        ).filter(
            pet_follower_table.c.follower_pid == user_pid
        ).filter(
            pet_follower_table.c.pet_pid == pet_pid
        ).first()

        target_follower = db.session.query(
            pet_follower_table
        ).filter(
            pet_follower_table.c.follower_pid == follower_pid
        ).filter(
            pet_follower_table.c.pet_pid == pet_pid
        ).filter(
            pet_follower_table.c.is_owner == False
        ).first()

        if requestor and target_follower:
            owner = db.session.query(
                pet_follower_table
            ).filter(
                pet_follower_table.c.follower_pid == user_pid
            ).filter(
                pet_follower_table.c.pet_pid == pet_pid
            ).filter(
                pet_follower_table.c.is_owner == True
            ).first()

            if owner:
                statement = pet_follower_table.delete().where(
                    pet_follower_table.c.follower_pid==follower_pid
                ).where(
                    pet_follower_table.c.pet_pid==pet_pid
                )
                table_save_changes(statement)
                response_object = {
                        'status': 'success',
                        'message': 'Pet follower successfully deleted.'
                    }
                return response_object, 201
            elif user_pid == follower_pid:
                statement = pet_follower_table.delete().where(
                    pet_follower_table.c.follower_pid==follower_pid
                ).where(
                    pet_follower_table.c.pet_pid==pet_pid
                )
                table_save_changes(statement)
                response_object = {
                        'status': 'success',
                        'message': 'Pet follower successfully deleted.'
                    }
                return response_object, 201
            else:
                response_object = {
                    'status': 'fail',
                    'message': 'Request unauthorized.'
                }
                return response_object, 401

def accept_pet_follower(user_pid, pet_pid, follower_pid):
    pet = Pet.query.filter_by(public_id=pet_pid).first()
    if pet:
        owner = db.session.query(
            pet_follower_table
        ).filter(
            pet_follower_table.c.follower_pid == user_pid
        ).filter(
            pet_follower_table.c.pet_pid == pet_pid
        ).filter(
            pet_follower_table.c.is_owner == True
        ).first()

        follower = db.session.query(
            pet_follower_table
        ).filter(
            pet_follower_table.c.follower_pid == follower_pid
        ).filter(
            pet_follower_table.c.pet_pid == pet_pid
        ).filter(
            pet_follower_table.c.is_owner == False
        ).first()

        if owner and follower:
            statement = pet_follower_table.update().where(
                pet_follower_table.c.follower_pid==follower_pid
            ).where(
                pet_follower_table.c.pet_pid==pet_pid
            ).values(
                is_accepted = True
            )
            table_save_changes(statement)
            response_object = {
                'status': 'success',
                'message': 'Pet follower successfully accepted.'
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
            'message': 'No pet found.'
        }
        return response_object, 404
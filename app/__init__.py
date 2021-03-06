# app/__init__.py

from flask_restx import Api
from flask import Blueprint

from .main.controller.user_controller import api as user_ns
from .main.controller.auth_controller import api as auth_ns
from .main.controller.specie_controller import api as specie_ns
from .main.controller.breed_controller import api as breed_ns
from .main.controller.pet_controller import api as pet_ns
from .main.controller.business_controller import api as business_ns
from .main.controller.post_controller import api as post_ns
from .main.controller.businessType_controller import api as businessType_ns
from .main.controller.circleType_controller import api as circleType_ns
from .main.controller.circle_controller import api as circle_ns
from .main.controller.comment_controller import api as comment_ns
from .main.controller.notification_controller import api as notification_ns
from .main.controller.preference_controller import api as preference_ns

blueprint = Blueprint('api', __name__)

api = Api(blueprint,
          title='FLASK RESTPLUS API BOILER-PLATE WITH JWT',
          version='1.0',
          description='a boilerplate for flask restplus web service'
          )

api.add_namespace(user_ns, path='/user')
api.add_namespace(auth_ns)
api.add_namespace(specie_ns, path='/specie')
api.add_namespace(breed_ns, path='/breed')
api.add_namespace(pet_ns, path='/pet')
api.add_namespace(business_ns, path='/business')
api.add_namespace(post_ns, path='/post')
api.add_namespace(businessType_ns, path='/business_type')
api.add_namespace(circle_ns, path='/circle')
api.add_namespace(circleType_ns, path='/circle_type')
api.add_namespace(comment_ns, path='/comment')
api.add_namespace(notification_ns, path="/notification")
api.add_namespace(preference_ns, path="/preference")


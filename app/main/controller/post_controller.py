from flask import request
from flask_restx import Resource
from ..util.dto import PostDto
from ..util.decorator import *
from ..service.post_service import like_a_post, save_new_post, get_all_posts, get_all_posts_by_user, get_a_post, delete_a_post, get_all_posts_by_business, get_all_posts_by_circle, get_all_posts_by_pet

api = PostDto.api
_post = PostDto.post

@api.route('/')
class PostList(Resource):
    @token_required
    @api.doc('list_of_registered_posts')
    @api.marshal_list_with(_post, envelope='data')
    def get(self, user_pid):
        """List all registered user specific feed posts"""
        return get_all_posts(user_pid, request.args.get("pagination_no", type=int))

    @token_required
    @api.response(201, 'Post successfully created.')
    @api.doc('create a new post')
    @api.expect(_post, validate=True)
    @api.marshal_with(_post)
    def post(self, user_pid):
        """Creates a new Post """
        data = request.json
        return save_new_post(user_pid=user_pid, data=data)

@api.route('/bytoken')
class PostListByToken(Resource):
    @token_required
    @api.doc('list_of_registered_posts')
    @api.marshal_list_with(_post, envelope='data')
    def get(self, user_pid):
        """List all registered posts"""
        return get_all_posts_by_user(user_pid, request.args.get("pagination_no", type=int))

@api.route('/subject/<subject_id>')
@api.param("subject_id", "The Pet public identifier")
class PostListByPet(Resource):
    @token_required
    @api.doc('list_of_registered_posts')
    @api.marshal_list_with(_post, envelope='data')
    def get(self, user_pid, subject_id):
        """List all registered posts"""
        return get_all_posts_by_pet(user_pid, subject_id, request.args.get("w_media_only"), request.args.get("pagination_no", type=int))

@api.route('/pinboard/<pinboard_id>')
@api.param("pinboard_id", "The Business public identifier")
class PostListByBusiness(Resource):
    @token_required
    @api.doc('list_of_registered_posts')
    @api.marshal_list_with(_post, envelope='data')
    def get(self, user_pid, pinboard_id):
        """List all registered posts"""
        return get_all_posts_by_business(user_pid, pinboard_id, request.args.get("w_media_only"), request.args.get("pagination_no", type=int))

@api.route('/confiner/<confiner_id>')
@api.param("confiner_id", "The Circle public identifier")
class PostListByCircle(Resource):
    @token_required
    @api.doc('list_of_registered_posts')
    @api.marshal_list_with(_post, envelope='data')
    def get(self, user_pid, confiner_id):
        """List all registered posts"""
        list = get_all_posts_by_circle(user_pid, confiner_id, request.args.get("w_media_only"), request.args.get("pagination_no", type=int))
        return list
@api.route('/<public_id>')
@api.param('public_id', 'The Post identifier')
@api.response(404, 'Post not found.')
class Post(Resource):
    @token_required
    @api.doc('get a post')
    @api.marshal_with(_post)
    def get(self, user_pid, public_id):
        """get a post given its identifier"""
        post = get_a_post(user_pid, public_id)
        if not post:
            api.abort(404)
        else:
            return post

    @token_required
    @api.doc('like a post')
    def post(self, user_pid, public_id):
        """like a post given its identifier"""
        return like_a_post(user_pid, public_id)

    @token_required
    @api.response(201, 'Post successfully deleted.')
    @api.doc('delete a post')
    def delete(self, user_pid, public_id):
        """delete a post given its identifier"""
        return delete_a_post(public_id, user_pid)
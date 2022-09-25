import os
from flask import Flask, request, jsonify, abort
from sqlalchemy import exc
import json
from flask_cors import CORS

from .database.models import db_drop_and_create_all, setup_db, Drink
from .auth.auth import AuthError, requires_auth

app = Flask(__name__)
setup_db(app)
CORS(app)

'''
@TODO uncomment the following line to initialize the datbase
!! NOTE THIS WILL DROP ALL RECORDS AND START YOUR DB FROM SCRATCH
!! NOTE THIS MUST BE UNCOMMENTED ON FIRST RUN
!! Running this funciton will add one
'''
#db_drop_and_create_all()

# ROUTES
'''
@TODO implement endpoint
    GET /drinks
        it should be a public endpoint
        it should contain only the drink.short() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks')
def get_drinks():
    drinks = Drink.query.all()
    if len(drinks) == 0:
        abort(404)
    drinks_short = [drink.short() for drink in drinks]
    return jsonify({
        'success': True,
        'drinks': drinks_short
    })


'''
@TODO implement endpoint
    GET /drinks-detail
        it should require the 'get:drinks-detail' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks-detail/<int:drink_id>')
@requires_auth('get:drinks-detail')
def get_drinks_detail(jwt, drink_id):
    try:
        # get all drinks and format using .long()
        drinks = Drink.query.filter(Drink.id == drink_id).one_or_none()

        # 404 if no drinks found
        if drinks is None:
            abort(404)

        else:
            # format using .long()
            drinks_long = [drink.long() for drink in drinks]

            return jsonify({
                'success': True,
                'drinks': drinks_long
                })
    except:
        abort(422)

'''
@TODO implement endpoint
    POST /drinks
        it should create a new row in the drinks table
        it should require the 'post:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the newly created drink
        or appropriate status code indicating reason for failure
'''
@app.route('/create', methods=['POST'])
@requires_auth('post:drinks')
def create_drink(jwt):
    # get the drink info from request
    body = request.get_json()

    new_title = body.get("title", None)
    new_recipe = body.get("recipe", None)

    # create a new drink
    drink = Drink(title=new_title, recipe=json.dumps(new_recipe))

    try:
        # add drink to the database
        drink.insert()

        return jsonify({
        "success": True,
        "drinks": drink.long()
        })

    except:
        abort(422)

'''
@TODO implement endpoint
    PATCH /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should update the corresponding row for <id>
        it should require the 'patch:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the updated drink
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks-detail/<int:drink_id>')
@requires_auth('patch:drinks')
def update_drinks(jwt, drink_id):

    # get drink by id
    drink = Drink.query.get(drink_id)
    if drink is None:
        abort(404)

    # get request data
    data = request.get_json()
    # update title if present in data
    if 'title' in data:
        drink.title = data['title']

    # update recipe if present in data
    if 'recipe' in data:
        drink.recipe = json.dumps(data['recipe'])

    drink.update()

    return jsonify({
        'success': True,
        'drinks': [drink.long()]
    })

'''
@TODO implement endpoint
    DELETE /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should delete the corresponding row for <id>
        it should require the 'delete:drinks' permission
    returns status code 200 and json {"success": True, "delete": id} where id is the id of the deleted record
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks/<int:id>', methods=['DELETE'])
@requires_auth('delete:drinks')
def delete_drink(jwt, drink_id):

    drink = Drink.query.get(drink_id)
    if drink is None:
        abort(404)

    try:
        # delete drink from database
        drink.delete()

        # return status and deleted drink id
        return jsonify({
        'success': True,
        'delete': drink.id
        })

    except:
        # server error
        abort(500)

# Error Handling
'''
Example error handling for unprocessable entity
'''


@app.errorhandler(422)
def unprocessable(error):
    return jsonify({
        "success": False,
        "error": 422,
        "message": "unprocessable"
    }), 422


'''
@TODO implement error handlers using the @app.errorhandler(error) decorator
    each error handler should return (with approprate messages):
             jsonify({
                    "success": False,
                    "error": 404,
                    "message": "resource not found"
                    }), 404

'''

'''
@TODO implement error handler for 404
    error handler should conform to general task above
'''
@app.errorhandler(404)
def resource_not_found(error):
    return jsonify({
        "success": False,
        "error": 404,
        "message": "resource not found"
    }), 404

'''
Error handling for bad request
'''
@app.errorhandler(400)
def resource_not_found(error):
    return jsonify({
        "success": False,
        "error": 400,
        "message": "bad request"
    }), 400

'''
@TODO implement error handler for AuthError
    error handler should conform to general task above
'''
@app.errorhandler(AuthError)
def handle_auth_error(ex):
    response = jsonify(ex.error)
    response.status_code = ex.status_code
    return response
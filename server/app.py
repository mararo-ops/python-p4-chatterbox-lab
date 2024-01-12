from flask import Flask, request, make_response, jsonify
from flask_cors import CORS
from flask_migrate import Migrate

from models import db, Message

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

CORS(app)
migrate = Migrate(app, db)

db.init_app(app)

@app.route('/messages',methods=['GET'])
def messages():
    messages = Message.query.order_by(Message.created_at.asc()).all()

    message_list=[]
    for message in messages:
          message_dict = {
            'id': message.id,
            'body':message.body,
            'username': message.username,
           'created_at': message.created_at.strftime('%Y-%m-%d %H:%M:%S'),  # Format the datetime as a string
            'updated_at': message.updated_at.strftime('%Y-%m-%d %H:%M:%S'), 
        }
    message_list.append(message_dict)
    response =make_response(jsonify(message_list),200)
    response.headers['Content-Type']='application/json'

    return response

@app.route('/messages/<int:id>')
def messages_by_id(id):
    message = db.session.get(Message, id)

    if message is None:
        response = make_response(
            jsonify({"error": "Message not found"}),
            404
        )
    else:
        response = make_response(
            jsonify(message.to_dict()),
            200
        )

    return response



# Create a new message (POST request)
@app.route('/messages', methods=['POST'])
def create_message():
    data = request.get_json()
    if 'body' not in data or 'username' not in data:
        response = make_response(
            jsonify({"error": "Both 'body' and 'username' are required fields"}),
            400
        )
    else:
        message = Message(body=data['body'], username=data['username'])
        db.session.add(message)
        db.session.commit()

        response = make_response(
            jsonify(message.to_dict()),
            201
        )

    return response

# Update a message (PATCH request)
@app.route('/messages/<int:id>', methods=['PATCH'])
def update_message(id):
    data = request.get_json()
    message = db.session.get(Message, id)

    if message is None:
        response = make_response(
            jsonify({"error": "Message not found"}),
            404
        )
    else:
        if 'body' in data:
            message.body = data['body']
        db.session.commit()

        response = make_response(
            jsonify(message.to_dict()),
            200
        )

    return response
# Delete a message (DELETE request)
@app.route('/messages/<int:id>', methods=['DELETE'])
def delete_message(id):
    message = db.session.get(Message, id)

    if message is None:
        response = make_response(
            jsonify({"error": "Message not found"}),
            404
        )
    else:
        db.session.delete(message)
        db.session.commit()

        response = make_response(
            jsonify({"message": "Message deleted successfully"}),
            200
        )

    return response
if __name__ == '__main__':
    app.run(port=5555)
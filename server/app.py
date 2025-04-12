import os
from flask import Flask, request, make_response, jsonify
from flask_cors import CORS
from flask_migrate import Migrate

from models import db, Message

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE_URL = "sqlite:///" + os.path.join(BASE_DIR, "instance", "app.db")

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///app.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False


CORS(app)
migrate = Migrate(app, db)

db.init_app(app)

@app.route('/messages', methods=['GET'])
def messages():
    messages = Message.query.order_by(Message.created_at.asc()).all()
    messages_dict = [message.to_dict() for message in messages]
    return make_response(jsonify(messages_dict), 200)


@app.route('/messages', methods=['POST'])
def post_messages():
    data = request.get_json()
    if not data or 'body' not in data or 'username' not in data:
        return make_response(jsonify({"error": "Missing required fields: body and username"}), 400)
    try:
        new_message = Message(
            body=data['body'],
            username=data['username']
        )
        db.session.add(new_message)
        db.session.commit()
        
        return make_response(jsonify(new_message.to_dict()), 201)
    
    except Exception as e:
        db.session.rollback()
        return make_response(jsonify({"error":"Could not create message", "details":str(e)}), 500)

@app.route('/messages/<int:id>', methods=['PATCH'])
def patch_message(id):
    
    message = Message.query.get(id)
    if not message:
        return make_response(jsonify({"error": f"Message with id {id} not found"}), 404)

    data = request.get_json()

    if not data or 'body' not in data:
         return make_response(jsonify({"error": "Missing required field: body"}), 400)

    try:
        message.body = data['body'] 
        db.session.commit()

        return make_response(jsonify(message.to_dict()), 200) 

    except Exception as e:
        db.session.rollback()
        return make_response(jsonify({"error": "Could not update message", "details": str(e)}), 500)


@app.route('/messages/<int:id>', methods=['DELETE'])
def delete_message(id):
    
    message = Message.query.get(id)

    if not message:
        return make_response(jsonify({"error": f"Message with id {id} not found"}), 404)

    try:
        db.session.delete(message)
        db.session.commit()

        return make_response('', 204)

    except Exception as e:
        db.session.rollback()
        return make_response(jsonify({"error": "Could not delete message", "details": str(e)}), 500)


if __name__ == '__main__':
    
    instance_path = os.path.join(BASE_DIR, "instance")
    if not os.path.exists(instance_path):
        os.makedirs(instance_path)
        print(f"Created instance folder at: {instance_path}")

    app.run(port=5000, debug=True)
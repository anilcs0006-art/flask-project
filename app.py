import os
from flask import request, jsonify,Flask
from pymongo import MongoClient
from flask import render_template

app = Flask(__name__)

@app.route("/todo")
def todo_page():
    return render_template("todo.html")

mongo_uri = os.environ.get("MONGO_URL")

if not mongo_uri:
    raise RuntimeError("Please set the MONGO_URI environment variable")

client = MongoClient(mongo_uri, serverSelectionTimeoutMS=5000)
db = client["todo_database"]
todo_collection = db["todo_items"]


@app.route("/submittodoitem", methods=["POST"])
def submit_todo_item():
    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return jsonify({"error": "Request must contain JSON data"}), 400

    item_name = data.get("itemName", "").strip()
    item_description = data.get("itemDescription", "").strip()

    if not item_name or not item_description:
        return jsonify({
            "error": "Item Name and Item Description are required"
        }), 400

    try:
        result = todo_collection.insert_one({
            "itemName": item_name,
            "itemDescription": item_description
        })

        return jsonify({
            "message": "To-Do item saved successfully",
            "id": str(result.inserted_id)
        }), 201

    except Exception:
        app.logger.exception("Failed to save To-Do item")
        return jsonify({"error": "Unable to save item to database"}), 500

app.run(debug=True)

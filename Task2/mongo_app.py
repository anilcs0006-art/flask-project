
import os

from flask import Flask, render_template, request, redirect, url_for
from pymongo import MongoClient
from pymongo.errors import PyMongoError

app = Flask(__name__)

# Set your MongoDB Atlas URI as an environment variable.
MONGO_URI = os.environ.get("MONGO_URL")

client = None
collection = None

if MONGO_URI:
    try:
        client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
        client.admin.command("ping")

        db = client["form_database"]
        collection = db["submissions"]

    except PyMongoError:
        if client:
            client.close()
        client = None
        collection = None


@app.route("/", methods=["GET", "POST"])
def form():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip()
        message = request.form.get("message", "").strip()

        # Validate submitted fields
        if not name or not email or not message:
            return render_template(
                "form.html",
                error="All fields are required.",
                name=name,
                email=email,
                message=message
            ), 400

        if collection is None:
            return render_template(
                "form.html",
                error="Database is unavailable. Check your MongoDB Atlas configuration.",
                name=name,
                email=email,
                message=message
            ), 503

        try:
            collection.insert_one({
                "name": name,
                "email": email,
                "message": message
            })

            # Redirect only after successful insertion
            return redirect(url_for("success"))

        except PyMongoError:
            return render_template(
                "form.html",
                error="Failed to save data. Please try again.",
                name=name,
                email=email,
                message=message
            ), 500

    return render_template("form.html")


@app.route("/success")
def success():
    return render_template("success.html")


if __name__ == "__main__":
    app.run(debug=True)

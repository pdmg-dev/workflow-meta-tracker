import logging

from flask_login import current_user
from flask_socketio import emit

from app.extensions import db, socketio
from app.models.user import User

logging.basicConfig(level=logging.INFO)


@socketio.on("connect", namespace="/presence")
def handle_connect():
    logging.info("Socket.IO: Client connected to /presence")
    if current_user.is_authenticated:
        user = User.query.get(current_user.id)
        if user:
            user.is_online = True
            user.last_login = user.last_login or user.created_at  # fallback if needed
            db.session.commit()

            emit("user_online", {"user_id": user.id, "username": user.username}, broadcast=True)
            print(f"[Presence] {user.username} is now online")


@socketio.on("disconnect", namespace="/presence")
def handle_disconnect():
    logging.info("Socket.IO: Client disconnected to /presence")
    if current_user.is_authenticated:
        user = User.query.get(current_user.id)
        if user:
            user.is_online = False
            user.last_logout = db.func.now()
            db.session.commit()

            emit("user_offline", {"user_id": user.id, "username": user.username}, broadcast=True)
            print(f"[Presence] {user.username} went offline")

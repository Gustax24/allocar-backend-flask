from flask_jwt_extended import decode_token
from extensions.socketio import socketio
from domain.bookings.repository import get as get_booking
from extensions.db import db
from flask import request


def _is_member(user_id, booking_id):
    b = get_booking(booking_id)
    if not b:
        return False
    from domain.trips.models import Trip
    trip = db.session.get(Trip, b.trip_id)
    return str(user_id) in (str(b.passenger_id), str(trip.driver_id))

@socketio.on("join_booking")
def on_join_booking(data):
    # data: {"booking_id": "...", "token": "Bearer <jwt>"}
    token = (data or {}).get("token","").replace("Bearer ","").strip()
    booking_id = (data or {}).get("booking_id")
    try:
        j = decode_token(token)
        uid = j.get("sub")
        if _is_member(uid, booking_id):
            socketio.enter_room(request.sid, f"booking:{booking_id}")
            socketio.emit("room:joined", {"booking_id": booking_id}, to=request.sid)
        else:
            socketio.emit("error", {"message":"forbidden"})
    except Exception:
        socketio.emit("error", {"message":"invalid_token"})

@socketio.on("leave_booking")
def on_leave_booking(data):
    booking_id = (data or {}).get("booking_id")
    socketio.leave_room(request.sid, f"booking:{booking_id}")
    socketio.emit("room:left", {"booking_id": booking_id}, to=request.sid)

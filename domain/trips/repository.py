from datetime import datetime, timedelta, timezone
from sqlalchemy import and_, or_, func
from extensions.db import db
from .models import Trip, TripStop

def get(trip_id):
    return db.session.get(Trip, trip_id)

def create_trip(driver_id, payload) -> Trip:
    o = payload["origin"]; d = payload["destination"]
    t = Trip(
        driver_id=driver_id,
        origin_lat=o["lat"], origin_lon=o["lon"], origin_text=o["text"],
        destination_lat=d["lat"], destination_lon=d["lon"], destination_text=d["text"],
        departure_time=payload["departure_time"],
        arrival_eta=payload.get("arrival_eta"),
        price_per_seat=payload["price_per_seat"],
        seats_available=payload["seats_available"],
        luggage_policy=payload.get("luggage_policy"),
        rules=payload.get("rules"),
        allow_auto_accept=payload.get("allow_auto_accept", False),
        status=payload.get("status", "published"),
    )
    db.session.add(t)
    db.session.commit()
    return t

def update_trip(trip: Trip, **kwargs) -> Trip:
    for k, v in kwargs.items():
        setattr(trip, k, v)
    db.session.commit()
    return trip

def delete_trip(trip: Trip):
    db.session.delete(trip)
    db.session.commit()

def add_stops(trip_id, stops_payload):
    items = []
    for s in stops_payload:
        items.append(TripStop(
            trip_id=trip_id,
            order=s["order"],
            lat=s["lat"],
            lon=s["lon"],
            label=s["label"],
            pickup_allowed=s.get("pickup_allowed", True),
            dropoff_allowed=s.get("dropoff_allowed", True),
        ))
    db.session.bulk_save_objects(items)
    db.session.commit()
    return items

def list_stops(trip_id):
    return db.session.query(TripStop).filter(TripStop.trip_id == trip_id).order_by(TripStop.order.asc()).all()

def list_my_trips(driver_id, status=None):
    q = db.session.query(Trip).filter(Trip.driver_id == driver_id)
    if status:
        q = q.filter(Trip.status == status)
    return q.order_by(Trip.departure_time.desc()).all()

# Haversine (km) expression
def _haversine(lat1, lon1, lat2, lon2):
    return 6371 * 2 * func.asin(
        func.sqrt(
            func.pow(func.sin(func.radians(lat2 - lat1) / 2), 2)
            + func.cos(func.radians(lat1))
            * func.cos(func.radians(lat2))
            * func.pow(func.sin(func.radians(lon2 - lon1) / 2), 2)
        )
    )

def search_trips(params):
    q = db.session.query(Trip).filter(Trip.status == "published")

    if "date" in params and params["date"]:
        start = datetime.combine(params["date"], datetime.min.time(), tzinfo=timezone.utc)
        end = datetime.combine(params["date"], datetime.max.time(), tzinfo=timezone.utc)
        q = q.filter(Trip.departure_time >= start, Trip.departure_time <= end)

    if params.get("seats"):
        q = q.filter(Trip.seats_available >= int(params["seats"]))

    if params.get("price_min") is not None:
        q = q.filter(Trip.price_per_seat >= params["price_min"])
    if params.get("price_max") is not None:
        q = q.filter(Trip.price_per_seat <= params["price_max"])

    # filtrage par distance autour du point de départ et d'arrivée demandés
    radius = float(params.get("radius_km", 50.0))
    from_lat, from_lon = float(params["from_lat"]), float(params["from_lon"])
    to_lat, to_lon = float(params["to_lat"]), float(params["to_lon"])

    # distance départ
    dist_from = _haversine(from_lat, from_lon, Trip.origin_lat, Trip.origin_lon)
    # distance arrivée
    dist_to = _haversine(to_lat, to_lon, Trip.destination_lat, Trip.destination_lon)

    q = q.add_columns(dist_from.label("d_from"), dist_to.label("d_to")) \
         .filter(dist_from <= radius, dist_to <= radius) \
         .order_by(dist_from.asc(), dist_to.asc(), Trip.departure_time.asc())

    # retourne uniquement Trip (et non les colonnes ajoutées)
    return [row[0] for row in q.limit(200).all()]

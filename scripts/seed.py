from app import app
from extensions.db import db
from common.security import hash_password
from domain.users.models import User
from domain.vehicles.models import Vehicle
from domain.trips.models import Trip
from domain.bookings.models import Booking, BookingEvent
from domain.wallet.models import Wallet
from datetime import datetime, timedelta, timezone
from decimal import Decimal

def ensure_user(email, password, first_name, last_name, role="user", phone=None):
    u = db.session.query(User).filter(User.email == email).first()
    if u:
        return u
    u = User(
        email=email, phone=phone,
        password_hash=hash_password(password),
        first_name=first_name, last_name=last_name, role=role
    )
    db.session.add(u); db.session.commit()
    return u

def ensure_vehicle(user_id, plate, make="Toyota", model="Yaris", color="white", seats_total=4, comfort="standard"):
    from domain.vehicles.models import Vehicle
    v = db.session.query(Vehicle).filter(Vehicle.plate_number == plate).first()
    if v: return v
    v = Vehicle(
        user_id=user_id, plate_number=plate, make=make, model=model,
        color=color, seats_total=seats_total, comfort_level=comfort, verified=True
    )
    db.session.add(v); db.session.commit()
    return v

def create_trip(driver_id, o_lat, o_lon, o_text, d_lat, d_lon, d_text, dep_offset_hours=24, price=6000, seats=3):
    t = Trip(
        driver_id=driver_id,
        origin_lat=o_lat, origin_lon=o_lon, origin_text=o_text,
        destination_lat=d_lat, destination_lon=d_lon, destination_text=d_text,
        departure_time=datetime.now(timezone.utc) + timedelta(hours=dep_offset_hours),
        arrival_eta=None,
        price_per_seat=Decimal(str(price)),
        seats_available=seats,
        luggage_policy="1 valise cabine",
        rules="Non-fumeur",
        allow_auto_accept=True,
        status="published"
    )
    db.session.add(t); db.session.commit()
    return t

def create_booking(trip, passenger_id, seats=1, status="accepted"):
    amount = Decimal(str(trip.price_per_seat)) * seats
    b = Booking(trip_id=trip.id, passenger_id=passenger_id, seats=seats, amount_total=amount, status=status)
    db.session.add(b); db.session.commit()
    db.session.add(BookingEvent(booking_id=b.id, from_status=None, to_status=status, by="system", meta={"seed": True}))
    db.session.commit()
    return b

def ensure_wallet(user_id):
    from domain.wallet.models import Wallet
    w = db.session.query(Wallet).filter(Wallet.user_id == user_id).first()
    if not w:
        w = Wallet(user_id=user_id, balance=Decimal("0"), currency="XOF")
        db.session.add(w); db.session.commit()
    return w

def run():
    with app.app_context():
        # (Optionnel) pour un MVP sans migrations, décommente la ligne suivante :
        # db.create_all()

        # Admin
        admin = ensure_user("admin@allocar.ci", "admin123", "Admin", "AlloCar", role="admin", phone="+2250100000001")

        # Drivers
        d1 = ensure_user("driver1@allocar.ci", "driver123", "Aline", "Kouassi", role="user", phone="+2250100000002")
        d2 = ensure_user("driver2@allocar.ci", "driver123", "Moussa", "Traoré", role="user", phone="+2250100000003")

        # Passengers
        p1 = ensure_user("pass1@allocar.ci", "pass123", "Fatou", "Koné", role="user", phone="+2250100000004")
        p2 = ensure_user("pass2@allocar.ci", "pass123", "Yao", "N’Guessan", role="user", phone="+2250100000005")

        # Wallets
        for u in (admin, d1, d2, p1, p2):
            ensure_wallet(u.id)

        # Vehicles
        ensure_vehicle(d1.id, "ABJ-1001", make="Toyota", model="Corolla", color="bleu", seats_total=4, comfort="standard")
        ensure_vehicle(d2.id, "ABJ-1002", make="Hyundai", model="Accent", color="gris", seats_total=4, comfort="basic")

        # Trips (Abidjan ↔ Yamoussoukro / Bouaké)
        t1 = create_trip(
            d1.id, 5.3575, -4.0083, "Abidjan, Plateau",
            6.8190, -5.2760, "Yamoussoukro",
            dep_offset_hours=24, price=6000, seats=3
        )
        t2 = create_trip(
            d2.id, 6.8190, -5.2760, "Yamoussoukro",
            7.6868, -5.0303, "Bouaké",
            dep_offset_hours=30, price=5000, seats=2
        )

        # Bookings (pré-créées)
        b1 = create_booking(t1, p1.id, seats=1, status="accepted")
        b2 = create_booking(t2, p2.id, seats=1, status="accepted")

        print("Seed terminé :")
        print("  Admin      : admin@allocar.ci / admin123")
        print("  Driver1    : driver1@allocar.ci / driver123")
        print("  Driver2    : driver2@allocar.ci / driver123")
        print("  Passenger1 : pass1@allocar.ci / pass123")
        print("  Passenger2 : pass2@allocar.ci / pass123")

if __name__ == "__main__":
    run()

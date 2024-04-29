from flask import request
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut
from ..const import IGNORE_MOVE
from ..user import userUtils
from app.db import conn
from psycopg2.extras import DictCursor


def _update_location_DB(id, long, lat):
    from ..socket import socket_service as socketServ

    user = userUtils.get_user(id)
    if not user:
        cursor.close()
        return

    with conn.cursor(cursor_factory=DictCursor) as cursor:
        if (
            not user["longitude"]
            or not user["latitude"]
            or IGNORE_MOVE
            < userUtils.get_distance(user["latitude"], user["longitude"], lat, long)
        ):
            # update location
            sql = 'UPDATE "User" SET "longitude" = %s, "latitude" = %s WHERE "id" = %s;'
            cursor.execute(sql, (long, lat, id))
            conn.commit()

            # (socket) 거리 업데이트
            socketServ.update_distance(id, long, lat)


# TODO [wrapper]에 통합


def update_location(f):
    def wrapper(*args, **kwargs):
        try:
            # TODO [JWT]
            id = 1
            # id = get_jwt_identity()['id']

            long = request.header.get("longitude")
            lat = request.header.get("latitude")

            if not long or not lat:
                ip_addr = request.remote_addr
                geolocator = Nominatim(user_agent="geoapiExercises")
                location = geolocator.geocode(ip_addr)

                if not location:
                    raise Exception("no location returned from geopy")

                long = location.longitude
                lat = location.latitude

            _update_location_DB(id, long, lat)

        except GeocoderTimedOut:
            print("Error: geocode failed due to timeout")

        except Exception as e:
            print(f"Error: while update_location on DB: {e}")

        return f(*args, **kwargs)

    return wrapper

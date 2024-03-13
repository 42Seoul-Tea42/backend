from flask_socketio import emit
from ..const import Status
from app.db import conn
from psycopg2.extras import DictCursor
from ..user.userUtils import get_distance

id_sid = dict()
# sid_id = dict() #나중에 disconnect시 sid_id 필요하면 다시 추가하기
id_match = dict()

#### alarm ####
def new_match(id, target_id):
    user_sid = id_sid.get(id, None)
    target_sid = id_sid.get(target_id, None)
    
    if user_sid:
        emit('new_match', {'target_id': target_id}, room=user_sid)
    if target_sid:
        emit('new_match', {'target_id': id}, room=target_sid)


def new_fancy(id, target_id):
    target_sid = id_sid.get(target_id, None)
    if target_sid:
        emit('new_match', {'target_id': id}, room=target_sid)
    

def new_history(id):
    user_sid = id_sid.get(id, None)
    if user_sid:
        emit('new_match', room=user_sid)
    

#### update ####
def update_distance(id, long, lat):
    cursor = conn.cursor(cursor_factory=DictCursor)
    for target_id in id_match[id]:
        target_sid = id_sid.get(target_id, None)
        if target_sid:
            
            sql = 'SELECT * FROM "User" WHERE "id" = %s;'
            cursor.execute(sql, (target_id, ))
            target = cursor.fetchone()
            if not target:
                continue
            
            emit('update_distance', { 'target_id': id,
                                    'distance': get_distance(lat, long, target['latitude'], target['longitude']),
                                    }, room=target_sid)
    cursor.close()
        

def update_status(id, target_id, status):
    target_sid = id_sid.get(target_id, None)
    if target_sid:
        emit('update_status', { 'target_id': id, 'status': status }, room=target_sid)


def unmatch(id, target_id):
    target_sid = id_sid.get(target_id, None)
    if target_sid:
        emit('unmatch', { 'target_id': id }, room=target_sid)


#### Utils ####
def check_status(target_id):
    if target_id in id_sid:
        return Status.ONLINE
    return Status.OFFLINE
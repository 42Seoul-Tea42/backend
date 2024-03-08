from flask_socketio import emit
from ..const import Status


id_sid = dict()
sid_id = dict()
id_friend = dict()

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
def update_location(id, target_id, longitude, latitude):
    target_sid = id_sid.get(target_id, None)
    if target_sid:
        emit('update_location', { 'target_id': id,
                                 'longitude': longitude,
                                 'latitude': latitude }, room=target_sid)
        

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
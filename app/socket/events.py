# from flask import request, emit
# from ..chat import chatUtils as chatUtils
# from . import socketService as socketServ
# from flask_jwt_extended import jwt_required

# from wsgi import socket_io


# @socket_io.on_error_default
# def default_error_handler(e):
#     print(f"[SocketIO Error] {request.path}: ", exc_info=e)


# @socket_io.on("connect")
# def handle_connect():
#     socket_uid = request.sid
#     print("On: connected")
#     print("Socket UID:", socket_uid)
#     emit("new_fancy", broadcast=True)


# @socket_io.on("send_message")
# def handle_connec222t():
#     print("????")
#     emit("send_message", broadcast=True)


# # #### connect && disconnect ####
# # # @jwt_required()
# # @socket_io.on("connect")
# # def handle_connect():
# #     # id = get_jwt_identity()
# #     # [JWT] delete below
# #     id = 1
# #     user_sid = request.sid
# #     socketServ.handle_connect(id, user_sid)


# # @socket_io.on("disconnect")
# # def handle_disconnect():
# #     user_sid = request.sid
# #     socketServ.handle_disconnect(user_sid)


# # # #### chat ####
# # @socket_io.on("send_message")
# # def send_message(data):
# #     user_sid = request.sid
# #     print("            asdfasdfasdfasadfasfadsfsdfsfasfadffasfadf")
# #     emit("new_fancy", data, broadcast=True)
# #     # socketServ.send_message(data, user_sid)


# # @socket_io.on("read_message")
# # def read_message(data):
# #     user_sid = request.sid
# #     socketServ.read_message(data, user_sid)

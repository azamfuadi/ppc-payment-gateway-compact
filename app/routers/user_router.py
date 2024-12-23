from app import app
from app.controllers import user_controller
from flask import Blueprint, request

users_blueprint = Blueprint("users_router", __name__)

@app.route("/admin/login", methods=["POST"])
def requestToken():
    params = request.json
    return user_controller.generateToken(**params)

@app.route("/user/admininsertnojtwneeded123", methods=["POST"])
def addData():
    params = request.json
    return user_controller.insertUser(**params)

@app.route("/user/insert", methods=["POST"])
def addDataWithInvitation():
    params = request.json
    return user_controller.insertUserByInvitation(**params)

@app.route("/user/resetpass", methods=["POST"])
def resetPass():
    params = request.json
    return user_controller.generateNewPass(**params)

@app.route("/admin/emailinvitation", methods=["POST"])
def emailInvitation():
    params = request.json
    return user_controller.emailInvitation(**params)

@app.route("/user/update", methods=["POST"])
def changeData():
    params = request.json
    return user_controller.updateUser(**params)

@app.route("/admins", methods=["GET"])
def showAllUsers():
    return user_controller.showAllAdmins()

@app.route("/user/delete", methods=["POST"])
def deleteData():
    params = request.json
    return user_controller.deleteUser(**params)
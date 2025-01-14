from flask import request, render_template, jsonify, redirect
from app import app
from app.controllers import all_controller, paypay_controller
from app.controllers.all_controller import token_required
from flask import request, Blueprint

allroute_blueprint = Blueprint("all_router", __name__)


# @app.errorhandler(404)
# def page_not_found(error):
#     return render_template('error.html', mssg="page not found"), 404

@app.route('/admin/setting', methods=['GET'])
def adminSetting():
    return all_controller.getAdminSetting()


@app.route('/admin/setting/logo', methods=['GET'])
def companyLogo():
    return all_controller.getCompanyLogo()


@app.route('/user/list', methods=['GET'])
def userList():
    return all_controller.getUserList()


@app.route("/transaction/list/<string:user>", methods=["GET"])
def userTransactionList(user):
    return all_controller.getUserTransactionListDetailed(user)


@app.route('/transaction/list', methods=['GET'])
def transactionList():
    return all_controller.getTransactionList()


@app.route('/transaction/monthly', methods=['GET'])
def transactionMonthly():
    return all_controller.getTransactionMonthly()


@app.route('/admin/setting/update', methods=['PUT'])
def adminUpdate():
    req = request.form
    if 'company_logo' not in request.files:
        file = ''
    else:
        file = request.files['company_logo']
    return all_controller.updateAdminSetting(file, **req)


@app.route('/topup/', methods=['GET'])
def promptUser():
    user = request.args.get('user')
    lang = request.args.get('lang')
    return all_controller.generateToken(user, lang)


@app.route('/payment/')
@token_required
def verify():
    token = request.args.get('t')
    lang = request.args.get('lang')
    return all_controller.userTopUp(token, lang)


@app.route('/pagetopup/', methods=['GET'])
def promptPageUser():
    user = request.args.get('user')
    lang = request.args.get('lang')
    return all_controller.generatePageToken(user, lang)


@app.route('/paymentpage/')
@token_required
def verifyPage():
    token = request.args.get('t')
    lang = request.args.get('lang')
    return all_controller.userTopUpPage(token, lang)


@app.route('/paypay/', methods=['GET', 'POST'])
def paypay():
    req = request.json
    amount = req['amount']
    user = req['user']
    lang = req['lang']
    return paypay_controller.paymentPaypay(float(amount), user, lang)


@app.route('/check/<merch_id>/<lang>', methods=['GET', 'OPTIONS'])
def check(merch_id, lang):
    return paypay_controller.paypayCheck(merch_id, lang)


# @app.route('/btclient', methods=['GET'])
# def getBTClientToken():
#     return paypal_controller.generate_client_token()


# @app.route('/paypal/', methods=['GET', 'POST'])
# def paypal():
#     # req = request.json
#     # amount = req['amount']
#     # user = req['user']
#     # nonce_from_the_client = req["payment_method_nonce"]
#     amount = request.form["amount"]
#     user = request.form["user"]
#     method = request.form["method"]
#     nonce_from_the_client = request.form["payment_method_nonce"]
#     return paypal_controller.paymentPayPal(str(amount), user, method, nonce_from_the_client)


# @app.route('/checkouts/<transaction_id>/<payment_method>', methods=['GET'])
# def checkouts(transaction_id, payment_method):
#     return paypal_controller.paypal_checkout(transaction_id, payment_method)

@app.route('/api/update-papercut-settings', methods=["POST"])
def updatePaperCutSettingsAPI():
  if len(request.form) > 0:
    primary_server =  request.form["primary_server"]
    auth_token = request.form["auth_token"]
    response = all_controller.setPaperCutDefaultConfig(primary_server, auth_token)
    message = response['message']
    api_response = {
        'message' : message,
        'response': response
    }
    return jsonify(api_response), 200
  
@app.route('/api/get-papercut-settings', methods=["GET"])
def getPaperCutSettings():
  papercut_config = all_controller.getPaperCutDefaultConfig()
  return jsonify(papercut_config), 200

@app.route('/api/get-papercut-payment-settings', methods=["GET"])
def getPaperCutPaymentSettings():
  papercut_config = all_controller.getPaperCutPaymentConfig()
  return jsonify(papercut_config), 200


@app.route('/invoicedownload/<transaction_id>/<lang>', methods=['GET'])
def invoiceDownload(transaction_id, lang):
    return all_controller.generateInvoice(transaction_id, lang)


# @app.route('/paypalv2', methods=['GET', 'POST'])
# def paypalv2():
#     req = request.json
#     amount = req['amount']
#     user = req['user']
#     method = req['method']
#     lang = req['lang']
#     return paypalRestAPI_controller.create_order(amount, user, method, lang)


# @app.route('/paypalv2_token', methods=['GET', 'POST'])
# def paypalv2_token():
#     return paypalRestAPI_controller.generate_access_token()


# @app.route('/paypalv2_check/', methods=['GET', 'POST'])
# def paypalv2_check():
#     token = request.args.get('token')
#     return paypalRestAPI_controller.checkPayPal_v2(token)

@app.route('/papercut/config', methods=['GET'])
def papercut_config():
    return all_controller.getPaperCutPaymentConfig()

    
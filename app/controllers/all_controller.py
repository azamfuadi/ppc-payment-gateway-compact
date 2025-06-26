from app import key, app, mail
import xmlrpc.client
import paypayopa
import jwt
from flask_jwt_extended import *
from flask import render_template, redirect, jsonify, request, make_response, send_from_directory
# from app.models.credential_model import credentials
# from app.models.transaction_model import transaction
from sqlalchemy import func, desc
import uuid
import datetime
from functools import wraps
import os
from werkzeug.utils import secure_filename
from threading import Thread
import requests

from flask_mail import Message
import pdfkit

ru = u'\u30EB'

def makeClient(api_key, api_secret, merchant_id):
    client = paypayopa.Client(
        auth=(api_key, api_secret), production_mode=False)
    client.set_assume_merchant(merchant_id)
    return client


def makeProxy(papercutserver):
    host = papercutserver+"/rpc/api/xmlrpc"
    proxy = xmlrpc.client.ServerProxy(host)
    return proxy

# ==================function to send email asynchronusly


def async_send_mail(app, msg):
    with app.app_context():
        mail.send(msg)


def send_mail(subject, recipient, template, **kwargs):
    msg = Message(
        subject, sender=app.config['MAIL_DEFAULT_SENDER'], recipients=[recipient])
    msg.html = render_template(template, **kwargs)
    thr = Thread(target=async_send_mail, args=[app, msg])
    thr.start()
    return thr


# def generateInvoice(transaction_id, lang):
#     trans = session.query(transaction).filter(
#         transaction.MerchantPaymentID == transaction_id).first()
#     adminSetting = session.query(credentials).first()
#     proxy = makeProxy(adminSetting.Primary_Server_Address)
#     auth = adminSetting.auth
#     email = proxy.api.getUserProperty(auth, trans.Account, 'email')
#     fullname = proxy.api.getUserProperty(auth, trans.Account, 'full-name')
#     company_detail = {
#         "logo": "http://192.168.11.51:5000/admin/setting/logo",
#         "name": adminSetting.company_name,
#         "email": adminSetting.company_email,
#         "phone": adminSetting.company_phone,
#         "address": adminSetting.company_address,
#     }
#     user_detail = {
#         "username": trans.Account,
#         "fullname": fullname,
#         "email": email
#     }
#     transaction_detail = {
#         "id": transaction_id,
#         "time": trans.Time,
#         "method": trans.Method,
#         "amount": trans.Amount,
#         "points": trans.Point,
#         "conversion": trans.Point/trans.Amount,
#     }

#     # config = pdfkit.configuration(
#     #     wkhtmltopdf='E:\\programs\\wkhtmltopdf\\bin\\wkhtmltopdf.exe')
#     config = pdfkit.configuration(
#         wkhtmltopdf='C:\\Program Files\\wkhtmltopdf\\bin\\wkhtmltopdf.exe')
#     if lang == 'en':
#         html = render_template("receipt.html", company=company_detail,
#                                user=user_detail, transaction=transaction_detail)
#     else:
#         html = render_template("receiptjp.html", company=company_detail,
#                                user=user_detail, transaction=transaction_detail)

#     pdf = pdfkit.from_string(html, False, configuration=config)

#     response = make_response(pdf)
#     response.headers["Content-Type"] = "application/pdf"
#     response.headers["Content-Disposition"] = "inline; filename=Papercut Points Invoice.pdf"
#     return response


# ==================controller for admin setting

# def getAdminSetting():
#     adminSetting = session.query(credentials).first()
#     response = {
#         'id': adminSetting.id,
#         'PayPay_API_KEY': adminSetting.PayPay_API_KEY,
#         'PayPay_API_SECRET': adminSetting.PayPay_API_SECRET,
#         'PayPay_MERCHANT_ID': adminSetting.PayPay_MERCHANT_ID,
#         'PayPal_Client_Id': adminSetting.PayPal_Client_Id,
#         'PayPal_Secret': adminSetting.PayPal_Secret,
#         'BT_ENVIRONMENT': adminSetting.BT_ENVIRONMENT,
#         'BT_MERCHANT_ID': adminSetting.BT_MERCHANT_ID,
#         'BT_PUBLIC_KEY': adminSetting.BT_PUBLIC_KEY,
#         'BT_PRIVATE_KEY': adminSetting.BT_PRIVATE_KEY,
#         'BT_APP_SECRET_KEY': adminSetting.BT_APP_SECRET_KEY,
#         "company_name": adminSetting.company_name,
#         "company_email": adminSetting.company_email,
#         "company_phone": adminSetting.company_phone,
#         "company_address": adminSetting.company_address,
#         "company_logo": adminSetting.company_logo,
#         'multiplier': adminSetting.multiplier,
#         'min_input': adminSetting.min_input,
#         'max_input': adminSetting.max_input,
#         'auth': adminSetting.auth,
#         'primary_server': adminSetting.Primary_Server_Address,
#         'mssg1': adminSetting.mssg,
#         'mssg2': adminSetting.mssg2,
#         'mssg_JP': adminSetting.mssg_JP,
#         'mssg2_JP': adminSetting.mssg2_JP,
#         'main_message': adminSetting.main_message,
#         'colour': adminSetting.colour,
#     }
#     session.close()
#     response = jsonify(response)
#     response.headers.add('Access-Control-Allow-Origin', '*')
#     return response


# def getCompanyLogo():
#     adminSetting = session.query(credentials).first()
#     companyLogo = adminSetting.logo_file
#     company_logo = adminSetting.company_logo
#     filename = os.path.join(app.config['UPLOAD_FOLDER'], company_logo)
#     print(filename)
#     session.close()
#     return send_from_directory(os.path.join(app.config['UPLOAD_FOLDER']), company_logo)
#     # return send_file(io.BytesIO(companyLogo),mimetype='image')


# def getTransactionList():
#     # transactions = session.query(transaction).all()
#     transactions = session.query(transaction).order_by(desc(transaction.Time))
#     all_transaction = []
#     for items in transactions:
#         trans = {
#             'id': items.id,
#             'time': items.Time,
#             'merchantPaymentID': items.MerchantPaymentID,
#             'account': items.Account,
#             'method': items.Method,
#             'amount': items.Amount,
#             'point': items.Point,
#         }
#         all_transaction.append(trans)
#     response = {
#         'transactions': all_transaction,
#     }
#     session.close()
#     response = jsonify(response)
#     response.headers.add('Access-Control-Allow-Origin', '*')
#     return response


# def getTransactionMonthly():
#     # transactions = session.query(transaction).all()
#     transactions = session.query(transaction.id, func.month(transaction.Time).label(
#         'month'), func.sum(transaction.Amount).label(
#         'totalAmount'), func.sum(transaction.Point).label(
#         'totalPoint')).group_by(func.month(transaction.Time))
#     months = []
#     totalAmounts = []
#     totalPoints = []
#     for items in transactions:
#         datetime_object = datetime.datetime.strptime(str(items.month), "%m")
#         full_month_name = datetime_object.strftime("%B")
#         months.append(full_month_name)
#         totalAmounts.append(items.totalAmount)
#         totalPoints.append(items.totalPoint)
#     response = {
#         'months': months,
#         'totalAmounts': totalAmounts,
#         'totalPoints': totalPoints,
#     }
#     session.close()
#     response = jsonify(response)
#     response.headers.add('Access-Control-Allow-Origin', '*')
#     return response


# def getUserList():
#     adminSetting = session.query(credentials).first()
#     proxy = makeProxy(adminSetting.Primary_Server_Address)
#     allUser = []
#     listUsers = proxy.api.listUserAccounts(adminSetting.auth, 0, 1000)
#     for user in listUsers:
#         sum_transactions = session.query(func.sum(transaction.Amount).label(
#             'totalAmount')).filter(transaction.Account == user)
#         if sum_transactions[0].totalAmount == None:
#             totalPurchase = 0
#         else:
#             totalPurchase = sum_transactions[0].totalAmount
#         trans = {
#             'account': user,
#             'email': proxy.api.getUserProperty(adminSetting.auth, user, 'email'),
#             'totalPurchase': totalPurchase,
#             'balance': proxy.api.getUserProperty(adminSetting.auth, user, 'balance'),
#         }
#         allUser.append(trans)
#     response = {
#         'users': allUser,
#     }
#     session.close()
#     response = jsonify(response)
#     response.headers.add('Access-Control-Allow-Origin', '*')
#     return response


# def getUserTransactionListDetailed(user):
#     transactions = session.query(transaction.id, func.max(transaction.Time).label('lastTime'), transaction.Method, func.sum(
#         transaction.Amount).label('totalAmount')).filter(transaction.Account == user).group_by(transaction.Method)
#     # sum_transactions = session.query(func.sum(transaction.Amount).label(
#     #     'totalAmount')).filter(transaction.Account == user)
#     allTransaction = []
#     for items in transactions:
#         trans = {
#             'id': items.id,
#             'method': items.Method,
#             'lastTime': items.lastTime,
#             'totalAmount': items.totalAmount,
#         }
#         allTransaction.append(trans)
#     print(transactions)
#     # if sum_transactions[0].totalAmount == None:
#     #     totalPurchase = 0
#     # else:
#     #     totalPurchase = sum_transactions[0].totalAmount
#     response = {
#         # 'totalPurchase': totalPurchase,
#         'transaction': allTransaction,
#     }
#     print("Sum transactions :", transactions)
#     session.close()
#     response = jsonify(response)
#     response.headers.add('Access-Control-Allow-Origin', '*')
#     return response

def getPaperCutPaymentConfig():
    # adminSetting = session.query(credentials).first()
    # proxy = makeProxy(adminSetting.Primary_Server_Address)
    proxy = makeProxy(app.config['PAPERCUT_SERVER'])
    yenPointRatio = proxy.api.getConfigValue(app.config['PAPERCUT_AUTH_TOKEN'], "payment-gateway.integration.yen-point-ratio")
    maximumPurchase = proxy.api.getConfigValue(app.config['PAPERCUT_AUTH_TOKEN'], "payment-gateway.integration.maximum-purchase")
    minimumPurchase = proxy.api.getConfigValue(app.config['PAPERCUT_AUTH_TOKEN'], "payment-gateway.integration.minimum-purchase")
    paypayEnabled = proxy.api.getConfigValue(app.config['PAPERCUT_AUTH_TOKEN'], "payment-gateway.integration.paypay.enabled")
    if yenPointRatio != '':
        yenPointRatio = float(yenPointRatio)
    if maximumPurchase != '':
        maximumPurchase = float(maximumPurchase)
    if minimumPurchase != '':
        minimumPurchase = float(minimumPurchase)
    paymentRelatedConfigs = {
        'yenPointRatio': yenPointRatio,
        'maximumPurchase': maximumPurchase,
        'minimumPurchase': minimumPurchase,
        'paypayEnabled': paypayEnabled

    }
    
    return paymentRelatedConfigs

def getPayPayPaymentConfig():
    # adminSetting = session.query(credentials).first()
    # proxy = makeProxy(adminSetting.Primary_Server_Address)
    proxy = makeProxy(app.config['PAPERCUT_SERVER'])
    paypayAPIKey = proxy.api.getConfigValue(app.config['PAPERCUT_AUTH_TOKEN'], "payment-gateway.integration.paypay.api-key")
    paypayAPISecret = proxy.api.getConfigValue(app.config['PAPERCUT_AUTH_TOKEN'], "payment-gateway.integration.paypay.api-secret")
    paypayMerchantId = proxy.api.getConfigValue(app.config['PAPERCUT_AUTH_TOKEN'], "payment-gateway.integration.paypay.merchant-id")
    paypayRelatedConfigs = {
        'paypayAPIKey': paypayAPIKey,
        'paypayAPISecret': paypayAPISecret,
        'paypayMerchantId': paypayMerchantId,
    }
    
    return paypayRelatedConfigs

def getPaperCutDefaultConfig():
    paperCutServer = app.config['PAPERCUT_SERVER']
    paperCutAuthToken = app.config['PAPERCUT_AUTH_TOKEN']
    paperCutDefaultConfigs = {
        'paperCutServer': paperCutServer,
        'paperCutAuthToken': paperCutAuthToken,
    }
    
    return paperCutDefaultConfigs
    

def setPaperCutDefaultConfig(primary_server, auth_token):
    app.config.update(
        PAPERCUT_SERVER=primary_server,
        PAPERCUT_AUTH_TOKEN=auth_token
    )
    response = {
        # 'totalPurchase': totalPurchase,
        'message': 'Success updating PaperCut Default Configuration',
        'messagejp': 'PaperCut のデフォルト設定の更新に成功しました',
        'code': '00'
    }
    return response

def setPaperCutPaymentConfig(yentoPoint, minimumPurchase, maximumPurchase, paypayEnabled):
    # adminSetting = session.query(credentials).first()
    # proxy = makeProxy(adminSetting.Primary_Server_Address)
    proxy = makeProxy(app.config['PAPERCUT_SERVER'])
    proxy.api.setConfigValue(app.config['PAPERCUT_AUTH_TOKEN'], "payment-gateway.integration.yen-point-ratio", yentoPoint)
    proxy.api.setConfigValue(app.config['PAPERCUT_AUTH_TOKEN'], "payment-gateway.integration.maximum-purchase", maximumPurchase)
    proxy.api.setConfigValue(app.config['PAPERCUT_AUTH_TOKEN'], "payment-gateway.integration.minimum-purchase", minimumPurchase)
    proxy.api.setConfigValue(app.config['PAPERCUT_AUTH_TOKEN'], "payment-gateway.integration.paypay.enabled", paypayEnabled)
    response = {
        # 'totalPurchase': totalPurchase,
        'message': 'Success updating PaperCut Top-Up Transaction Configuration',
        'messagejp': 'PaperCut のトップアップ取引設定の更新に成功しました',
        'code': '00'
    }
    return response

def setPaypayConfig(paypayAPIKey, paypayAPISecret, paypayMerchantId):
    # adminSetting = session.query(credentials).first()
    # proxy = makeProxy(adminSetting.Primary_Server_Address)
    proxy = makeProxy(app.config['PAPERCUT_SERVER'])
    proxy.api.setConfigValue(app.config['PAPERCUT_AUTH_TOKEN'], "payment-gateway.integration.paypay.api-key", paypayAPIKey)
    proxy.api.setConfigValue(app.config['PAPERCUT_AUTH_TOKEN'], "payment-gateway.integration.paypay.api-secret", paypayAPISecret)
    proxy.api.setConfigValue(app.config['PAPERCUT_AUTH_TOKEN'], "payment-gateway.integration.paypay.merchant-id", paypayMerchantId)
    response = {
        # 'totalPurchase': totalPurchase,
        'message': 'Success updating PayPay integration settings',
        'messagejp': 'PayPay の接続設定の更新に成功しました',
        'code': '00'
    }
    return response
    

ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg'])


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.args.get('t')
        if not token:
            return jsonify({'message': 'Token is missing'}), 403
        try:
            data = jwt.decode(token, key, algorithms=['HS256'])
        except jwt.ExpiredSignatureError:
            return jsonify({'message': 'Token expired, log in again'}), 403
        except jwt.InvalidTokenError:
            return jsonify({'message': 'Invalid token. Please log in again.'}), 403

        return f(*args, **kwargs)
    return decorated


def generateToken(user, lang):
    # adminSetting = session.query(credentials).first()
    # proxy = makeProxy(adminSetting.Primary_Server_Address)
    proxy = makeProxy(app.config['PAPERCUT_SERVER'])
    auth = app.config['PAPERCUT_AUTH_TOKEN']
    if proxy.api.isUserExists(auth, user) is True:
        expires = datetime.timedelta(hours=2)
        expires_refresh = datetime.timedelta(days=3)
        access_token = create_access_token(
            user, fresh=True, expires_delta=expires)
        data = jwt.encode({
            "data": user,
            "token_access": access_token
        }, key)
        if lang == 'jp':
            return redirect("{}/{}".format('/payment', ('?t='+data+'&lang=jp')))
        else:
            return redirect("{}/{}".format('/payment', ('?t='+data+'&lang=en')))
    else:
        response = jsonify({'message': 'User Invalid'}), 403
        response.headers.add('Access-Control-Allow-Origin', '*')
        return response
    
def generateAndRedirect(user, lang):
    # adminSetting = session.query(credentials).first()
    # proxy = makeProxy(adminSetting.Primary_Server_Address)
    proxy = makeProxy(app.config['PAPERCUT_SERVER'])
    auth = app.config['PAPERCUT_AUTH_TOKEN']
    if proxy.api.isUserExists(auth, user) is True:
        expires = datetime.timedelta(hours=2)
        expires_refresh = datetime.timedelta(days=3)
        access_token = create_access_token(
            user, fresh=True, expires_delta=expires)
        data = jwt.encode({
            "data": user,
            "token_access": access_token
        }, key)
        if lang == 'jp':
            return redirect("{}/{}".format('/topup-page', ('?t='+data+'&lang=jp')))
        else:
            return redirect("{}/{}".format('/topup-page', ('?t='+data+'&lang=en')))
    else:
        response = jsonify({'message': 'User Invalid'}), 403
        response.headers.add('Access-Control-Allow-Origin', '*')
        return response


def userTopUp(token, lang):
    tokens = jwt.decode(token, key, algorithms=['HS256'])
    user = tokens['data']
    access_token = tokens['token_access']
    if user == None:
        return jsonify({'message': 'User Invalid'}), 403
    else:
        if lang == 'jp':
            data = {
                'user': user,
                'jwt': access_token,
                'link': 'http://192.168.11.51:3000/userpage/jp?token='+access_token
            }
            response = jsonify(data)
            response.headers.add('Access-Control-Allow-Origin', '*')
            return response
        else:
            data = {
                'user': user,
                'jwt': access_token,
                'link': 'http://192.168.11.51:3000/userpage?token='+access_token
            }
            response = jsonify(data)
            response.headers.add('Access-Control-Allow-Origin', '*')
            return response


def generatePageToken(user, lang):
    # adminSetting = session.query(credentials).first()
    # proxy = makeProxy(adminSetting.Primary_Server_Address)
    proxy = makeProxy(app.config['PAPERCUT_SERVER'])
    auth = app.config['PAPERCUT_AUTH_TOKEN']
    if proxy.api.isUserExists(auth, user) is True:
        expires = datetime.timedelta(hours=2)
        expires_refresh = datetime.timedelta(days=3)
        access_token = create_access_token(
            user, fresh=True, expires_delta=expires)
        data = jwt.encode({
            "data": user,
            "token_access": access_token
        }, key)
        if lang == 'jp':
            return redirect("{}/{}".format('/paymentpage', ('?t='+data+'&lang=jp')))
        else:
            return redirect("{}/{}".format('/paymentpage', ('?t='+data+'&lang=en')))
    else:
        response = jsonify({'message': 'User Invalid'}), 403
        response.headers.add('Access-Control-Allow-Origin', '*')
        return response


def userTopUpPage(token, lang):
    tokens = jwt.decode(token, key, algorithms=['HS256'])
    user = tokens['data']
    access_token = tokens['token_access']
    if user == None:
        return jsonify({'message': 'User Invalid'}), 403
    else:
        if lang == 'jp':
            return redirect('http://192.168.11.51:3000/userpage/jp?token='+access_token)
        else:
            return redirect('http://192.168.11.51:3000/userpage?token='+access_token)

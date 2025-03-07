from app import app
from flask_jwt_extended import *
from flask import render_template, redirect, jsonify, request, flash
# from app.models.credential_model import credentials
# from app.models.transaction_model import transaction
from app.controllers.all_controller import makeProxy, makeClient, send_mail, getPayPayPaymentConfig, getPaperCutPaymentConfig
from sqlalchemy import func
import uuid
import polling
import datetime


def is_correct_response(resp):
    print(resp)
    return resp


def fetch_payment_status(client, merchant_id):
    resp = client.Code.get_payment_details(merchant_id)
    if (resp['data'] == 'None'):
        return {
            'error': 'true'
        }

    return resp['data']['status']


def fetch_payment_details(client, merchant_id):
    d = dict()
    resp = client.Code.get_payment_details(merchant_id)
    if (resp['data'] == 'None'):
        return {
            'error': 'true'
        }
    d['status'] = resp['data']['status']
    d['user'] = resp['data']['orderItems'][0]['name']
    d['amount'] = resp['data']['amount']['amount']
    d['paymentId'] = resp['data']['paymentId']
    return d


def paymentPaypay(amount, user, lang):
    # adminSetting = session.query(credentials).first()
    # client = makeClient(adminSetting.PayPay_API_KEY,
    #                     adminSetting.PayPay_API_SECRET, adminSetting.PayPay_MERCHANT_ID)
    papercutPaymentConfig = getPaperCutPaymentConfig()
    paypayPaymentConfig = getPayPayPaymentConfig()
    client = makeClient(paypayPaymentConfig.paypayAPIKey,
                        paypayPaymentConfig.paypayAPISecret, paypayPaymentConfig.paypayMerchantId)
    merchantPaymentId = uuid.uuid4().hex
    print(client)

    if amount < papercutPaymentConfig.minimumPurchase or amount > papercutPaymentConfig.maximumPurchase:
        if amount < papercutPaymentConfig.minimumPurchase:
            error = "Top up amount should be more than or equal with the Minimum Purchase (" + str(
                papercutPaymentConfig.minimumPurchase) + ")"
        else:
            error = "Top up amount should be less than or equal with the Maximum Purchase (" + str(
                papercutPaymentConfig.maximumPurchase) + ")"
        response = {
            'status': 'error',
            'message': error
        }
        response = jsonify(response)
        response.headers.add('Access-Control-Allow-Origin', '*')
        return response
    proxy = makeProxy(app.config['PAPERCUT_SERVER'])
    auth = app.config['PAPERCUT_AUTH_TOKEN']
    # proxy.api.getUserAccountBalance(auth,user)
    # print(proxy.api.getUserAccountBalance(auth,user))
    if proxy.api.isUserExists(auth, user):
        host_url = request.host_url
        FRONTEND_PATH = host_url+"check"
        qr = {
            "merchantPaymentId": merchantPaymentId,
            "codeType": "ORDER_QR",
            "redirectUrl": "{}/{}/{}".format(FRONTEND_PATH, merchantPaymentId, lang),
            "redirectType": "WEB_LINK",
            "orderDescription": "Papercutポイントの追加購入",
            "orderItems": [{
                "name": (user),
                "category": "Credit",
                "quantity": 1,
                "productId": "00001",
                "unitPrice": {
                    "amount": int(amount),
                    "currency": "JPY"
                }
            }],
            "amount": {
                "amount": int(amount),
                "currency": "JPY"
            },
        }

        response = client.Code.create_qr_code(qr)
        qrcode = (response['data']['url'])
        response = {
            'status': 'success',
            'paypaylink': qrcode,
            "merchantPaymentId": merchantPaymentId,
            "orderDescription": "Papercutポイントの追加購入",
            "orderItems": [{
                "name": (user),
                "category": "Credit",
                "quantity": 1,
                "productId": "00001",
                "unitPrice": {
                    "amount": int(amount),
                    "currency": "JPY"
                }
            }],
            "amount": {
                "amount": int(amount),
                "currency": "JPY"
            },
        }
        # session.close()
        response = jsonify(response)
        response.headers.add('Access-Control-Allow-Origin', '*')
        return response
    else:
        response = {
            'status': 'user not found',
            'message': 'User not exist in papercut',
        }
        # session.close()
        response = jsonify(response)
        response.headers.add('Access-Control-Allow-Origin', '*')
        return response
    
def redirectToPaypay(amount, user, lang):
    # adminSetting = session.query(credentials).first()
    # client = makeClient(adminSetting.PayPay_API_KEY,
    #                     adminSetting.PayPay_API_SECRET, adminSetting.PayPay_MERCHANT_ID)
    papercutPaymentConfig = getPaperCutPaymentConfig()
    paypayPaymentConfig = getPayPayPaymentConfig()
    client = makeClient(paypayPaymentConfig['paypayAPIKey'],
                        paypayPaymentConfig['paypayAPISecret'], paypayPaymentConfig['paypayMerchantId'])
    merchantPaymentId = uuid.uuid4().hex
    print(client)

    if int(amount) < int(papercutPaymentConfig['minimumPurchase']) or int(amount) > int(papercutPaymentConfig['maximumPurchase']):
        if int(amount) < int(papercutPaymentConfig['minimumPurchase']):
            error = "Top up amount should be more than or equal with the Minimum Purchase (" + str(
                papercutPaymentConfig['minimumPurchase']) + ")"
        else:
            error = "Top up amount should be less than or equal with the Maximum Purchase (" + str(
                papercutPaymentConfig['maximumPurchase']) + ")"
        response = {
            'status': 'error',
            'message': error
        }
        response = jsonify(response)
        response.headers.add('Access-Control-Allow-Origin', '*')
        return response
    proxy = makeProxy(app.config['PAPERCUT_SERVER'])
    auth = app.config['PAPERCUT_AUTH_TOKEN']
    # proxy.api.getUserAccountBalance(auth,user)
    # print(proxy.api.getUserAccountBalance(auth,user))
    if proxy.api.isUserExists(auth, user):
        host_url = request.host_url
        FRONTEND_PATH = host_url+"check"
        qr = {
            "merchantPaymentId": merchantPaymentId,
            "codeType": "ORDER_QR",
            "redirectUrl": "{}/{}/{}".format(FRONTEND_PATH, merchantPaymentId, lang),
            "redirectType": "WEB_LINK",
            "orderDescription": "Papercutポイントの追加購入",
            "orderItems": [{
                "name": (user),
                "category": "Credit",
                "quantity": 1,
                "productId": "00001",
                "unitPrice": {
                    "amount": int(amount),
                    "currency": "JPY"
                }
            }],
            "amount": {
                "amount": int(amount),
                "currency": "JPY"
            },
        }

        response = client.Code.create_qr_code(qr)
        qrcode = (response['data']['url'])
        response = {
            'status': 'success',
            'paypaylink': qrcode,
            "merchantPaymentId": merchantPaymentId,
            "orderDescription": "Papercutポイントの追加購入",
            "orderItems": [{
                "name": (user),
                "category": "Credit",
                "quantity": 1,
                "productId": "00001",
                "unitPrice": {
                    "amount": int(amount),
                    "currency": "JPY"
                }
            }],
            "amount": {
                "amount": int(amount),
                "currency": "JPY"
            },
        }
        # session.close()
        # response = jsonify(response)
        # response.headers.add('Access-Control-Allow-Origin', '*')
        # return response
        return redirect(qrcode)
    else:
        response = {
            'status': 'user not found',
            'message': 'User not exist in papercut',
        }
        # session.close()
        response = jsonify(response)
        response.headers.add('Access-Control-Allow-Origin', '*')
        return response


def paypayCheck(merch_id, lang):
    # adminSetting = session.query(credentials).first()
    # redirect_url = adminSetting.Primary_Server_Address+'/app?service=page/UserSummary'
    redirect_url = app.config['PAPERCUT_SERVER']+'/app?service=page/UserSummary'
    papercutPaymentConfig = getPaperCutPaymentConfig()
    paypayPaymentConfig = getPayPayPaymentConfig()
    client = makeClient(paypayPaymentConfig['paypayAPIKey'],
                        paypayPaymentConfig['paypayAPISecret'], paypayPaymentConfig['paypayMerchantId'])
    multiplier = float(papercutPaymentConfig['yenPointRatio'])
    try:
        polling.poll(
            lambda: fetch_payment_status(
                client, merch_id) == 'COMPLETED' or fetch_payment_status(client, merch_id) == 'FAILED',
            check_success=is_correct_response,
            step=2,
            timeout=240)
        payment_details = fetch_payment_details(client, merch_id)
        if (payment_details['status'] == 'COMPLETED'):
            # record = session.query(transaction).filter(
            #     transaction.MerchantPaymentID == merch_id).first()
            # if record == None:
                user = payment_details['user']
                print(user)
                amount = float(payment_details['amount'])
                print(amount)
                credit = amount*multiplier
                proxy = makeProxy(app.config['PAPERCUT_SERVER'])
                auth = app.config['PAPERCUT_AUTH_TOKEN']
                prev_balance = proxy.api.getUserAccountBalance(auth, user)
                proxy.api.adjustUserAccountBalance(
                    auth, user, credit, "PayPayによるポイント追加, 注文ID :"+str(merch_id))
                balance = proxy.api.getUserAccountBalance(auth, user)
                # newTransaction = transaction(
                #     Time=str(datetime.datetime.now()),
                #     MerchantPaymentID=merch_id, Account=user,
                #     Method='PayPay',
                #     Amount=amount,
                #     Point=credit
                # )
                # session.add(newTransaction)
                # session.commit()
                curr_balance = proxy.api.getUserAccountBalance(auth, user)
                email = proxy.api.getUserProperty(auth, user, 'email')
                if lang == 'en':
                    send_mail("Papercut Points Purchase Success Notification", email, 'mail/payment_succeed.html', payment_id=merch_id,
                              payment_method="PayPay",  multiplier=multiplier, amount=amount, prev_points=prev_balance, curr_points=curr_balance)
                    body = render_template('alert/success.html', balance=balance)
                else:
                    send_mail("ポイント購入成功連絡", email, 'mail/payment_succeedjp.html', payment_id=merch_id, payment_method="PayPay",
                              multiplier=multiplier, amount=amount, prev_points=prev_balance, curr_points=curr_balance)
                    body = render_template('alert/successjp.html', balance=balance)
                # session.close()
                return (body, 500, {("Refresh", "5; url={}".format(redirect_url))})
            # else:
            #     if lang == 'en':
            #         body = render_template('alert/error.html', mssg="Repeat Transaction. Point charge has been cancelled. The screen will change to Papercut user interface after 5 seconds")
            #     else:
            #         body = render_template('alert/errorjp.html', mssg="もう一度購入する。ポイント追加をキャンセルします。5秒後PaperCut ユーザインタフェースへ移動します。")

            #     # session.close()
            #     return (body, 500, {("Refresh", "5; url={}".format(redirect_url))})
        else:
            if redirect_url is None:
                # session.close()
                return "Cancelled. Please close this tab/window and return to PaperCut"
            else:
                if lang == 'en':
                    body = render_template('alert/error.html', mssg="API issue, incomplete transaction. Point charge has been cancelled. The screen will change to Papercut user interface after 5 seconds")
                else:
                    body = render_template('alert/errorjp.html', mssg="API問題、購入失敗。ポイント追加をキャンセルします。5秒後PaperCut ユーザインタフェースへ移動します。")
                # session.close()
                return (body, 500, {("Refresh", "5; url={}".format(redirect_url))})
    except:
        if lang == 'en':
            body = render_template('alert/error.html', mssg="API issue, incomplete transaction. Point charge has been cancelled. The screen will change to Papercut user interface after 5 seconds")
        else:
            body = render_template('alert/errorjp.html', mssg="API問題、購入失敗。ポイント追加をキャンセルします。5秒後PaperCut ユーザインタフェースへ移動します。")
        # session.close()
        return (body, 500, {("Refresh", "5; url={}".format(redirect_url))})

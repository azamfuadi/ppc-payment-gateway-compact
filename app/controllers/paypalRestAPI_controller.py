from app import session, key
from flask_jwt_extended import *
from flask import render_template, redirect, jsonify, request, flash
from app.models.credential_model import credentials
from app.models.transaction_model import transaction
from sqlalchemy import func
import datetime
import braintree
from app.controllers.all_controller import makeProxy, send_mail
import requests
import json

# use https://api.sandbox.paypal.com for production


def generate_access_token(client_id, secret):
    headers = {
        "Content-Type": "application/x-www-form-urlencoded"
    }

    data = {
        "grant_type": "client_credentials"
    }
    response = requests.post('https://api-m.sandbox.paypal.com/v1/oauth2/token',
                             headers=headers, auth=(client_id, secret), data=data)

    if response.status_code == 200:
        return response.json()['access_token']
    else:
        raise Exception("Access token generation failed with status code: {} and message: {}".format(
            response.status_code, response.text))


def create_order(amount, user, method, lang):
    adminSetting = session.query(credentials).first()
    access_token = generate_access_token(
        adminSetting.PayPal_Client_Id, adminSetting.PayPal_Secret)
    host_url = request.host_url
    return_url, cancel_url = host_url+'paypalv2_check', host_url+'paypalv2_check'
    headers = {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer ' + access_token
    }

    data = {
        "intent": "CAPTURE",
        "purchase_units": [{
            "reference_id": user+'_'+lang,
            "amount": {
                "value": amount,
                "currency_code": 'JPY'
            },
        }, ],
        "application_context": {
            "user_action": 'PAY_NOW',
            "payment_method_selected": method,
            "return_url": return_url,
            "cancel_url": cancel_url
        },
    }
    # data = {
    #     "intent": "CAPTURE",
    #     "purchase_units": [ {
    #         "reference_id": "d9f80740-38f0-11e8-b467-0ed5f89f718b",
    #         "amount": { "currency_code": "USD", "value": "100.00" }
    #         } ],
    #     "payment_source": { "paypal": {
    #         "experience_context": {
    #             "payment_method_preference": "IMMEDIATE_PAYMENT_REQUIRED",
    #             "payment_method_selected": "PAYPAL",
    #             "brand_name": "EXAMPLE INC",
    #             "locale": "en-US",
    #             "landing_page": "LOGIN",
    #             "shipping_preference": "SET_PROVIDED_ADDRESS",
    #             "user_action": "PAY_NOW",
    #             "return_url": "https://example.com/returnUrl",
    #             "cancel_url": "https://example.com/cancelUrl" }
    #             } }
    # }

    response = requests.post(
        'https://api-m.sandbox.paypal.com/v2/checkout/orders', headers=headers, data=json.dumps(data))

    if response.status_code == 201:
        data = json.loads(response.content)
        id = data['id']
        links = data['links'][1]['href']
        response = jsonify({
            'id': id,
            'links': links,
            'host_url': host_url,
        })
        response.headers.add('Access-Control-Allow-Origin', '*')
        return response
    else:
        raise Exception("Order creation failed with status code: {} and message: {}".format(
            response.status_code, response.text))


def checkPayPal_v2(id):
    adminSetting = session.query(credentials).first()
    access_token = generate_access_token(
        adminSetting.PayPal_Client_Id, adminSetting.PayPal_Secret)

    headers = {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer ' + access_token
    }

    response = requests.get(
        'https://api-m.sandbox.paypal.com/v2/checkout/orders/'+id, headers=headers)

    if response.status_code == 200:
        data = json.loads(response.content)
        id = data['id']
        status = data['status']
        amount = data['purchase_units'][0]['amount']['value']
        user, lang = (data['purchase_units'][0]['reference_id']).split('_')
        if status == "APPROVED":
            response = requests.post(
                "https://api.sandbox.paypal.com/v2/checkout/orders/"+id+"/capture", headers=headers)
            capture_data = json.loads(response.content)
            capture_status = capture_data['status']
            if capture_status == 'COMPLETED':
                adminSetting = session.query(credentials).first()
                redirect_url = adminSetting.Primary_Server_Address+'/app?service=page/UserSummary'
                multiplier = adminSetting.multiplier
                record = session.query(transaction).filter(
                    transaction.MerchantPaymentID == id).first()
                if record == None:
                    credit = int(amount)*int(multiplier)
                    proxy = makeProxy(adminSetting.Primary_Server_Address)
                    auth = adminSetting.auth
                    prev_balance = proxy.api.getUserAccountBalance(auth, user)
                    payment_method = 'PayPal'
                    proxy.api.adjustUserAccountBalance(
                        auth, user, float(credit), "PayPalによるポイント追加, 注文ID :"+str(id))
                    newTransaction = transaction(
                        Time=str(datetime.datetime.now()),
                        MerchantPaymentID=id,
                        Account=user,
                        Method=payment_method,
                        Amount=amount,
                        Point=credit
                    )
                    session.add(newTransaction)
                    session.commit()
                    response = {
                        'status': 'success',
                        'message': 'Success top up papercut points using ' + payment_method,
                        'user': user,
                        'redirect': redirect_url,
                        'amount': amount
                    }
                    balance = proxy.api.getUserAccountBalance(auth, user)
                    curr_balance = proxy.api.getUserAccountBalance(auth, user)
                    email = proxy.api.getUserProperty(auth, user, 'email')
                    if lang == 'en':
                        send_mail("Papercut Points Purchase Success Notification", email, 'mail/payment_succeed.html', payment_id=id,
                                  payment_method="PayPal",  multiplier=float(multiplier), amount=float(amount), prev_points=prev_balance, curr_points=curr_balance)
                        body = render_template('alert/success.html', balance=balance)
                    else:
                        send_mail("ポイント購入成功連絡", email, 'mail/payment_succeedjp.html', payment_id=id, payment_method="PayPal",
                                  multiplier=float(multiplier), amount=float(amount), prev_points=prev_balance, curr_points=curr_balance)
                        body = render_template('alert/successjp.html', balance=balance)
                    session.close()
                    return (body, 500, {("Refresh", "5; url={}".format(redirect_url))})
                else:
                    if lang == 'en':
                        body = render_template('alert/error.html', mssg="Repeat Transaction. Point charge has been cancelled. The screen will change to Papercut user interface after 5 seconds")
                    else:
                        body = render_template('alert/errorjp.html', mssg="もう一度購入する。ポイント追加をキャンセルします。5秒後PaperCut ユーザインタフェースへ移動します。")
                    session.close()
                    return (body, 500, {("Refresh", "5; url={}".format(redirect_url))})
            else:
                if lang == 'en':
                    body = render_template('alert/error.html', mssg="API issue, incomplete transaction. Point charge has been cancelled. The screen will change to Papercut user interface after 5 seconds")
                else:
                    body = render_template('alert/errorjp.html', mssg="API問題、購入失敗。ポイント追加をキャンセルします。5秒後PaperCut ユーザインタフェースへ移動します。")
                session.close()
                return (body, 500, {("Refresh", "5; url={}".format(redirect_url))})
        else:
            if lang == 'en':
                body = render_template('alert/error.html', mssg="API issue, incomplete transaction. Point charge has been cancelled. The screen will change to Papercut user interface after 5 seconds")
            else:
                body = render_template('alert/errorjp.html', mssg="API問題、購入失敗。ポイント追加をキャンセルします。5秒後PaperCut ユーザインタフェースへ移動します。")
            session.close()
            return (body, 500, {("Refresh", "5; url={}".format(redirect_url))})
    else:
        raise Exception("Order creation failed with status code: {} and message: {}".format(
            response.status_code, response.text))

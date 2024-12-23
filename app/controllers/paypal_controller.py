from app import session, key
from flask_jwt_extended import *
from flask import render_template, redirect, jsonify, request, flash, url_for
from app.models.credential_model import credentials
from app.models.transaction_model import transaction
from sqlalchemy import func
import datetime
import braintree
from app.controllers.all_controller import makeProxy, send_mail


def makeGateway():
    adminSetting = session.query(credentials).first()
    gateway = braintree.BraintreeGateway(
        braintree.Configuration(
            environment=adminSetting.BT_ENVIRONMENT,
            merchant_id=adminSetting.BT_MERCHANT_ID,
            public_key=adminSetting.BT_PUBLIC_KEY,
            private_key=adminSetting.BT_PRIVATE_KEY,
            app_secret_key=adminSetting.BT_APP_SECRET_KEY
        )
    )
    session.close()
    return gateway


def generate_client_token():
    gateway = makeGateway()
    client_token = gateway.client_token.generate()
    return jsonify({'client_token': client_token})


def transact(options):
    gateway = makeGateway()
    return gateway.transaction.sale(options)


def paymentPayPal(amount, user, method, payment_method_nonce):
    result = transact({
        'amount': amount,
        'payment_method_nonce': payment_method_nonce,
        "customer": {
            "first_name": user,
        },
        'options': {
            "submit_for_settlement": True
        }
    })

    if result.is_success or result.transaction:
        return redirect(url_for('checkouts', transaction_id=result.transaction.id, payment_method=method))
    else:
        err_mess = []
        for x in result.errors.deep_errors:
            mess = 'Error : ' + x.code + ': ' + x.message
            err_mess.append(mess)
        return jsonify(err_mess)


def find_transaction(id):
    gateway = makeGateway()
    return gateway.transaction.find(id)


TRANSACTION_SUCCESS_STATUSES = [
    braintree.Transaction.Status.Authorized,
    braintree.Transaction.Status.Authorizing,
    braintree.Transaction.Status.Settled,
    braintree.Transaction.Status.SettlementConfirmed,
    braintree.Transaction.Status.SettlementPending,
    braintree.Transaction.Status.Settling,
    braintree.Transaction.Status.SubmittedForSettlement
]


def paypal_checkout(transaction_id, payment_method):
    adminSetting = session.query(credentials).first()
    redirect_url = adminSetting.Primary_Server_Address+'/app?service=page/UserSummary'
    transactions = find_transaction(transaction_id)
    multiplier = adminSetting.multiplier
    if transactions.status in TRANSACTION_SUCCESS_STATUSES:
        record = session.query(transaction).filter(
            transaction.MerchantPaymentID == transaction_id).first()
        if record == None:
            amount = float(transactions.amount)
            user = transactions.customer['first_name']
            credit = amount*multiplier
            proxy = makeProxy(adminSetting.Primary_Server_Address)
            auth = adminSetting.auth
            prev_balance = proxy.api.getUserAccountBalance(auth, user)
            if payment_method == 'PayPal':
                proxy.api.adjustUserAccountBalance(
                    auth, user, credit, "PayPalによるポイント追加, 注文ID :"+str(transaction_id))
            elif payment_method == 'Card':
                proxy.api.adjustUserAccountBalance(
                    auth, user, credit, "Cardによるポイント追加, 注文ID :"+str(transaction_id))
            newTransaction = transaction(
                Time=str(datetime.datetime.now()),
                MerchantPaymentID=transaction_id,
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
            curr_balance = proxy.api.getUserAccountBalance(auth, user)
            email = proxy.api.getUserProperty(auth, user, 'email')
            send_mail("Papercut Points Purchase Succeed", email, 'mail/payment_succeed.html', payment_id=transaction_id,
                      payment_method=payment_method,  multiplier=multiplier, amount=amount, prev_points=prev_balance, curr_points=curr_balance)
            session.close()
            return jsonify(response)
        else:
            response = {
                'status': 'failed',
                'message': 'Failed top up papercut points using ' + payment_method,
                'user': user,
                'redirect': redirect_url,
                'amount': amount
            }
            session.close()
            return jsonify(response)
    else:
        response = {
            'status': 'failed',
            'message': 'Failed top up papercut points using ' + payment_method,
            'user': user,
            'redirect': redirect_url,
            'amount': amount
        }
        session.close()
        return jsonify(response)


def emailTest(transaction_id):
    trans = session.query(transaction).filter(
        transaction.MerchantPaymentID == transaction_id).first()
    adminSetting = session.query(credentials).first()
    proxy = makeProxy(adminSetting.Primary_Server_Address)
    auth = adminSetting.auth
    email = proxy.api.getUserProperty(auth, trans.Account, 'email')
    prev_balance = proxy.api.getUserAccountBalance(auth, trans.Account)
    curr_balance = int(prev_balance) + int(trans.Point)
    multiplier = trans.Point/trans.Amount
    if (email != ""):
        send_mail("Papercut Points Purchase Succeed", email, 'mail/payment_succeed.html', payment_id=transaction_id,
                  payment_method=trans.Method,  multiplier=multiplier, amount=trans.Amount, prev_points=prev_balance, curr_points=curr_balance)
        response = {
            'email': email,
            'status': "Email sent to user's registered email"
        }
    else:
        response = {
            'email': email,
            'status': "Email not sent because user don't have an email registered"
        }
    return jsonify(response)

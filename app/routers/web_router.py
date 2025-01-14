from flask import request, render_template, jsonify, redirect, url_for
from app import app
from app.controllers import all_controller, paypay_controller
from app.controllers.all_controller import token_required, makeProxy
from flask import request, Blueprint
from urllib.request import urlopen
from urllib.error import *

webroute_blueprint = Blueprint("web_router", __name__)


# @app.errorhandler(404)
# def page_not_found(error):
#     return render_template('error.html', mssg="page not found"), 404


@app.route('/')
def wrongUrl():
    return("Please log into PaperCut and set top up your account from there")


@app.route("/settings-page")
def settingPage():
    papercut_config = all_controller.getPaperCutDefaultConfig()
    if app.config['PAPERCUT_SERVER'] != '':
        payment_config = all_controller.getPaperCutPaymentConfig()
    else :
        payment_config = {}
    message_request = request.args.get('message')
    topup_message_request = request.args.get('topup_message')
    message = ''
    topup_message = ''
    if message_request is not None:
        message = message_request
    if topup_message_request is not None:
        topup_message = topup_message_request
    language = 'en'
    localization = request.args.get('lang')
    if localization is not None:
        language = localization
    if language == 'en':
        return render_template("settings/setting.html", paymentConfig=payment_config, papercutConfig = papercut_config, message=message, topup_message=topup_message)
    else: 
        return render_template("settings/settingjp.html", paymentConfig=payment_config, papercutConfig = papercut_config, message=message, topup_message=topup_message)

@app.route('/update-papercut-settings', methods=["POST"])
def updatePaperCutSettings():
  if len(request.form) > 0:
    primary_server =  request.form["primary_server"]
    auth_token = request.form["auth_token"]
    language = 'en'
    localization = request.form['lang']
    if localization is not None:
        language = localization
    try:
        response = urlopen(primary_server)
    except HTTPError as e:
        message = ''
        if language == 'en':
            message = 'Cannot connect to PaperCut Primary Server'
        else: 
            message = 'PaperCut プライマリ サーバーに接続できません'
        return redirect(url_for('settingPage', lang=language, message=message))
    except URLError as e:
        message = ''
        if language == 'en':
            message = 'Cannot connect to PaperCut Primary Server'
        else: 
            message = 'PaperCut プライマリ サーバーに接続できません'
        return redirect(url_for('settingPage', lang=language, message=message))
        # return {'message': 'Cannot connect to PaperCut Primary Server, Page Not Found', 'code': '01'}
    
    try:
        proxy = makeProxy(primary_server)
        listUsers = proxy.api.listUserAccounts(auth_token, 0, 10)
    except Exception as e:
        message = ''
        if language == 'en':
            message = 'Connected to PaperCut Primary Server, but wrong Auth Token'
        else: 
            message = 'PaperCut プライマリ サーバーに接続しましたが、認証トークンが間違っています'
        return redirect(url_for('settingPage', lang=language, message=message))
        
    response = all_controller.setPaperCutDefaultConfig(primary_server, auth_token)
    message = ''
    if language == 'en':
        message = response['message']
    else: 
        message = response['messagejp']
    return redirect(url_for('settingPage', lang=language, message=message))

@app.route('/update-topup-settings', methods=["POST"])
def updateTopUpSettings():
  if len(request.form) > 0:
    yen_to_point =  request.form["yen_to_point"]
    minimum_purchase = request.form["minimum_purchase"]
    maximum_purchase = request.form["maximum_purchase"]
    paypay_enabled = ''
    if request.form.get('paypay_enabled') == 'Y':
        paypay_enabled = 'Y'
    else:
        paypay_enabled = 'N'
    language = 'en'
    localization = request.form['lang']
    if localization is not None:
        language = localization
    try:
        response = all_controller.setPaperCutPaymentConfig(yen_to_point, minimum_purchase, maximum_purchase, paypay_enabled)
        topup_message = ''
        if language == 'en':
            topup_message = response['message']
        else: 
            topup_message = response['messagejp']
        
        return redirect(url_for('settingPage', lang=language, message='', topup_message=topup_message))
    except Exception as e:
        if language == 'en':
            topup_message = 'An error occured. Please check your connection.'
        else: 
            topup_message = 'エラーが発生しました。接続を確認してください'
        return redirect(url_for('settingPage', lang=language, message='', topup_message=topup_message))
    
    
    
    
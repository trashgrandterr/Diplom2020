import json
import os
import sys
import re
import requests
import boto3
from datetime import datetime
import general as gn
import aws_db as db_manager
import datetime




# here = os.path.dirname(os.path.realpath(__file__))
# sys.path.append(os.path.join(here, "./vendored"))

TOKEN = os.environ['TOKEN']
BASE_URL = "https://api.telegram.org/bot{}".format(TOKEN)
YOUR_PHONE = os.environ['YOUR_PHONE']
YOUR_GOV_PASS = os.environ['YOUR_GOV_PASS']
RECEIPTS_TABLE = os.environ['RECEIPTS_TABLE']
USERS_TABLE = os.environ['USERS_TABLE']
dynamodbCli = boto3.client('dynamodb')

def mainFunc(event, context):
    print("Starting")
    data = json.loads(event["body"])
    url_send_message = BASE_URL + "/sendMessage"
    url_send_document = BASE_URL + "/sendDocument"
    chat_id = data["message"]["chat"]["id"]
    userId = data["message"]["from"]["username"]
    message_text = data["message"]["text"]
    
    if "start" in message_text:
        first_user_exists = db_manager.getUserDB('1')
        if first_user_exists:
            is_user_approved = db_manager.getUserDB(userId)
            if is_user_approved: 
                user_info = {'working': 1, 'in_Trip': 0}
                db_manager.updateUserDB(userId, user_info)
        else:
            db_manager.addUserDB('1', {'access' : userId})

    user_privileges = db_manager.getUserDB(userId)
    if user_privileges['access'] == userId:
        if (message_text[0:7] == "Добавить"):
            user_to_dd = message_text[9:]
            user_info = {'working': 0, 'in_Trip': 0}
            db_manager.addUserDB(userId, user_info)

            response = {"text": "Пользователя добавили", "chat_id": chat_id}
            requests.post(url_send_message, response)
        
        if (message_text[0:12] == "Заблокировать"):
            user_to_dd = message_text[14:]
            user_info = {'working': 0, 'in_Trip': 0}
            db_manager.addUserDB(userId, user_info)

            response = {"text": "Пользователя добавили", "chat_id": chat_id}
            requests.post(url_send_message, response)
        
        if (message_text[0:4] == "Отчет"):
            user_id = message_text[6:]
            x = datetime.datetime.now
            date = x.strftime("%x")
            receipts = db_manager.getReceiptDB(user_id, date)
            report = gn.generatereport(user_id, date, receipts)
            response = {"text": "The record is {}".format(receipts), "chat_id": chat_id, 'document': report}
            requests.post(url_send_document, response)

        
        if (message_text[0:5] == "Отчеты"):
            user_id = message_text[7:]
            threeReceipts = db_manager.getReceiptThreeDB(user_id)
            for receipts in threeReceipts:
                x = datetime.datetime.now
                date = x.strftime("%x")
                receipts = db_manager.getReceiptDB(user_id, date)
                report = gn.generatereport(user_id, date, receipts)
                response = {"text": "The record is {}".format(receipts), "chat_id": chat_id, 'document': report}
                requests.post(url_send_document, response)
            

    if user_privileges['working'] == 1:
        if "photo" in data["message"]:
            receipt_json = gn.get_receipt_data(data)
            if (receipt_json):
                receipt_purchases = receipt_json["document"]["receipt"]["items"]
                receipt_id = receipt_json["document"]["receipt"]["kktRegId"]
                date = receipt_json["document"]["receipt"]["dateTime"]
                date = date.replace("-", "")
                
                db_manager.addReceiptDB(userId, date, receipt_purchases)
                response = {"text": "Чек был сохранен.", "chat_id": chat_id}
                requests.post(url_send_message, response)
            else:
                response = {"text": "Чек еще не был обработан налоговой. Мы его добавим, когда это произойдет.", "chat_id": chat_id}
                db_manager.addReceiptDB(userId, '0', data["message"]["photo"])
                requests.post(url_send_message, response)

        if (data['check'] == 'event'):
            receipts = db_manager.getReceiptDB(userId, '0')
            for num in range(0, 10):
                for receipt in receipts:
                    receipt_purchases = receipt_json["document"]["receipt"]["items"]
                    receipt_id = receipt_json["document"]["receipt"]["kktRegId"]
                    date = receipt_json["document"]["receipt"]["dateTime"]
                    date = date.replace("-", "")
                    db_manager.addReceiptDB(userId, date, receipt_purchases)
                    db_manager.deleteReceiptDB(userId, num)


        if ("text" in data["message"]):
            text = data["message"]["text"]
            if text.startswith("Отчет:"):
                user_id = message_text[7:]
                x = datetime.datetime.now
                date = x.strftime("%x")
                receipts = db_manager.getReceiptDB(user_id, date)
                report = gn.generatereport(user_id, date, receipts)
                response = {"text": "The record is {}".format(receipts), "chat_id": chat_id, 'document': report}
                requests.post(url_send_document, response)

            if text.startswith("Оценить:"):
                trip_path = text[9:]
                gn.calcualte_cost(trip_path)

            if text.startswith("Начать поездку"):
                update_user = {'working': 1, 'new_inTrip': 1}
                receipts: db_manager.updateUserDB(userId, update_user)

                response = {"text": "Поездка началась.", "chat_id": chat_id}
                requests.post(url_send_message, response)

            if text.startswith("Оценить"):
                if (db_manager.getUserDB(userId)['new_inTrip'] == 1):
                    trip_path = text[9:]
                    gn.calcualte_cost(trip_path)

                response = {"text": "Поездка началась.", "chat_id": chat_id}
                requests.post(url_send_message, response)

            if text.startswith("Закончить поездку"):
                update_user = {'working': 1, 'new_inTrip': 0}
                receipts: db_manager.updateUserDB(userId, update_user)

                response = {"text": "Поездка закончилась.", "chat_id": chat_id}
                requests.post(url_send_message, response)
            
           
        

    print("End of the Function.")






#     {"ok":true,"result":[
# {"update_id":834488323,
# "message":{"message_id":77,"from":{"id":207777314,"is_bot":false,"first_name":"Maxim","last_name":"Gavrilov","username":"grandterr","language_code":"en"},"chat":{"id":207777314,"first_name":"Maxim","last_name":"Gavrilov","username":"grandterr","type":"private"},"date":1586544370,"text":"dsds"}}, 
# {"update_id":834488324,
# "message":{"message_id":78,"from":{"id":207777314,"is_bot":false,"first_name":"Maxim","last_name":"Gavrilov","username":"grandterr","language_code":"en"},"chat":{"id":207777314,"first_name":"Maxim","last_name":"Gavrilov","username":"grandterr","type":"private"},"date":1586544375,"photo":[{"file_id":"AgACAgIAAxkBAANOXpC-96ykofKj-qnxeqyjr5JlBz8AAl-xMRsiWIlI5mUFLkDLRksKDwWSLgADAQADAgADbQAD-BwAAhgE","file_unique_id":"AQADCg8Fki4AA_gcAAI","file_size":14633,"width":320,"height":200},{"file_id":"AgACAgIAAxkBAANOXpC-96ykofKj-qnxeqyjr5JlBz8AAl-xMRsiWIlI5mUFLkDLRksKDwWSLgADAQADAgADeAAD-RwAAhgE","file_unique_id":"AQADCg8Fki4AA_kcAAI","file_size":80655,"width":800,"height":500},{"file_id":"AgACAgIAAxkBAANOXpC-96ykofKj-qnxeqyjr5JlBz8AAl-xMRsiWIlI5mUFLkDLRksKDwWSLgADAQADAgADeQAD9hwAAhgE","file_unique_id":"AQADCg8Fki4AA_YcAAI","file_size":189256,"width":1280,"height":800}]}}]}

#"message":{"message_id":107,"from":{"id":207777314,"is_bot":false,"first_name":"Maxim","last_name":"Gavrilov","username":"grandterr","language_code":"en"},"chat":{"id":207777314,"first_name":"Maxim","last_name":"Gavrilov","username":"grandterr","type":"private"},"date":1586598634,"photo":[{"file_id":"AgACAgIAAxkBAANrXpGS6qETTxBYsnU6Cmnv0uYb93cAAlauMRsiWJFIfo40FUtgXQMCAQKSLgADAQADAgADbQAD2yEAAhgE","file_unique_id":"AQADAgECki4AA9shAAI","file_size":10591,"width":320,"height":200},{"file_id":"AgACAgIAAxkBAANrXpGS6qETTxBYsnU6Cmnv0uYb93cAAlauMRsiWJFIfo40FUtgXQMCAQKSLgADAQADAgADeAAD3CEAAhgE","file_unique_id":"AQADAgECki4AA9whAAI","file_size":54892,"width":800,"height":500},{"file_id":"AgACAgIAAxkBAANrXpGS6qETTxBYsnU6Cmnv0uYb93cAAlauMRsiWJFIfo40FUtgXQMCAQKSLgADAQADAgADeQAD3SEAAhgE","file_unique_id":"AQADAgECki4AA90hAAI","file_size":129692,"width":1280,"height":800}]}

import boto3
import os

RECEIPTS_TABLE = os.environ['RECEIPTS_TABLE']
USERS_TABLE = os.environ['USERS_TABLE']
dataStore = boto3.client('dataStore')

def addUserDB(userId, item):
    done = dataStore.put_item(
        TableName = USERS_TABLE,
        Item={
            'userId': {'S': str(userId) },
            'items': {'S': str(item)}
        }
    )
    return done

def getUserDB(user_id):
    is_user_approved = dataStore.get_item(
            TableName = USERS_TABLE,
            Key={
                'userId': {'S': str(user_id)},
            }
        )
    return is_user_approved

def updateUserDB(userId, user_info):
    new_working = user_info['working']
    new_inTrip = user_info['in_Trip']
    done = dataStore.update_item(
            TableName = USERS_TABLE,
            Key={
                'userId': {'S': str(userId) },
            },
            UpdateExpression = "set working = :r, in_Trip=:p",
            ExpressionAttributeValues = {
                ":r": new_working,
                ":p": new_inTrip
            },
            ReturnValues = "UPDATE_NEW"
        )
    return done
        


def getReceiptDB(userId, date):
    report = dataStore.get_item(
            TableName = RECEIPTS_TABLE,
            Key={
                'userId': {'S': str(userId) },
                'date': {'S': str(date)}
            }
        )
    return report

def getReceiptThreeDB(userId):
    report = dataStore.get_item(
            TableName = RECEIPTS_TABLE,
            Key={
                'userId': {'S': str(userId) },
            },
            ProjectionExpression = "DateTimeUtc",
            KeyConditionExpression = "key = :keyValue and DateTimeUtc &gt;= :dt",
            ExpressionAttributeValues = 'Dictionary&lt;string, AttributeValue&gt',
            ScanIndexForward = False,
            ConsistentRead = False,
            Limit = 3,
        )
    return report

def addReceiptDB(userId, date, item):
    done = dataStore.put_item(
        TableName = RECEIPTS_TABLE,
        Item={
            'userId': {'S': str(userId) },
            'date': {'S': str(date)},
            'items': {'S': str(item)}
        }
    )
    return done

def updateReceiptDB(userId, date, receiptDate, receipt):
    done = dataStore.update_item(
            TableName = RECEIPTS_TABLE,
            Key={
                'userId': {'S': str(userId) },
                'date': {'S': str(date)}
            },
            UpdateExpression = 'SET #ri = list_append(#ri, :vals)',
            ExpressionAttributeNames = '{"#ri": ' + receiptDate + '}',
            ExpressionAttributeValues = {
                ':v': receipt
            },
            ReturnValues = "ALL_NEW"
        )
    return done 

def deleteReceiptDB(userId, date):
    done = dataStore.delete_item(
            TableName = RECEIPTS_TABLE,
            Key={
                'userId': {'S': str(userId) },
                'date': {'S': str(date)}
            }
        )
    return done

import boto3
import os

RECEIPTS_TABLE = os.environ['RECEIPTS_TABLE']
USERS_TABLE = os.environ['USERS_TABLE']
dynamodbCli = boto3.client('dynamodb')

def addUserDB(userId, item):
    done = dynamodbCli.put_item(
        TableName = USERS_TABLE,
        Item={
            'userId': {'S': str(userId) },
            'items': {'S': str(item)}
        }
    )
    return done

def getUserDB(user_id):
    is_user_approved = dynamodbCli.get_item(
            TableName = USERS_TABLE,
            Key={
                'userId': {'S': str(user_id)},
            }
        )
    return is_user_approved

def updateUserDB(userId, user_info):
    new_working = user_info['working']
    new_inTrip = user_info['in_Trip']
    done = dynamodbCli.update_item(
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
    report = dynamodbCli.get_item(
            TableName = RECEIPTS_TABLE,
            Key={
                'userId': {'S': str(userId) },
                'date': {'S': str(date)}
            }
        )
    return report

def getReceiptThreeDB(userId):
    report = dynamodbCli.get_item(
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
    done = dynamodbCli.put_item(
        TableName = RECEIPTS_TABLE,
        Item={
            'userId': {'S': str(userId) },
            'date': {'S': str(date)},
            'items': {'S': str(item)}
        }
    )
    return done

def updateReceiptDB(userId, date, receiptDate, receipt):
    done = dynamodbCli.update_item(
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
    done = dynamodbCli.delete_item(
            TableName = RECEIPTS_TABLE,
            Key={
                'userId': {'S': str(userId) },
                'date': {'S': str(date)}
            }
        )
    return done

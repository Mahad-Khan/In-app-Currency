import boto3
from boto3 import resource
from botocore.exceptions import ClientError
import logging
import config


class User:
    """Encapsulates an Amazon DynamoDB table of User data."""
    def __init__(self, dyn_resource):
        """
        :param dyn_resource: A Boto3 DynamoDB resource.
        """
        self.dyn_resource = dyn_resource
        self.table = None
        
    def exists(self, table_name):
        """
        Determines whether a table exists. As a side effect, stores the table in
        a member variable.
        :param table_name: The name of the table to check.
        :return: True when the table exists; otherwise, False.
        """
        try:
            table = self.dyn_resource.Table(table_name)
            table.load()
            exists = True
        except ClientError as err:
            if err.response['Error']['Code'] == 'ResourceNotFoundException':
                exists = False
            else:
                logger.error(
                    "Couldn't check for existence of %s. Here's why: %s: %s",
                    table_name,
                    err.response['Error']['Code'], err.response['Error']['Message'])
                raise
        else:
            self.table = table
        return exists
    
    def create_table(self, table_name):
        """
        Creates an Amazon DynamoDB table that can be used to store movie data.
        The table uses the release year of the movie as the partition key and the
        title as the sort key.
        :param table_name: The name of the table to create.
        :return: The newly created table.
        """
        try:
            self.table = self.dyn_resource.create_table(
        TableName=table_name,
        KeySchema=[
            {
                'AttributeName': 'email',
                'KeyType': 'HASH'
            }
        ],
        AttributeDefinitions=[
            {
                'AttributeName': 'email',
                'AttributeType': 'S'
            },
        ],
        ProvisionedThroughput={
            'ReadCapacityUnits': 5,
            'WriteCapacityUnits': 5
        }
    )
            self.table.wait_until_exists()
        except ClientError as err:
            logger.error(
                "Couldn't create table %s. Here's why: %s: %s", table_name,
                err.response['Error']['Code'], err.response['Error']['Message'])
            raise
        else:
            return self.table
        
    
    def get_user(self, email):
        """
        Gets user data from the table.

        :param email: The email of the user.
        :return: The data about the requested user.
        """
        try:
            response = self.table.get_item(Key={'email': email})
        except ClientError as err:
            logger.error(
                "Couldn't get user %s from table %s. Here's why: %s: %s",
                email, self.table.name,
                err.response['Error']['Code'], err.response['Error']['Message'])
            raise
        else:
            if response.get('Item') == None:
                return "user not found"
            else:
                return response["Item"]
            
    def add_user(self, data):
        """
        Adds a new user to the table.
        :param data: The data of the user.
        """
        try:
            self.table.put_item(
                Item= {
                'first_name' : data['first_name'],
                'last_name' : data['last_name'],
                'email' : data['email'],
                'password' : data['password']})
        
        except ClientError as err:
            logger.error(
                "Couldn't add user %s to table %s. Here's why: %s: %s",
                data['email'], self.table.name,
                err.response['Error']['Code'], err.response['Error']['Message'])
            raise
        

class Wallet:
    """Encapsulates an Amazon DynamoDB table of Wallet data."""
    def __init__(self, dyn_resource):
        """
        :param dyn_resource: A Boto3 DynamoDB resource.
        """
        self.dyn_resource = dyn_resource
        self.table = None
        
    def exists(self, table_name):
        """
        Determines whether a table exists. As a side effect, stores the table in
        a member variable.
        :param table_name: The name of the table to check.
        :return: True when the table exists; otherwise, False.
        """
        try:
            table = self.dyn_resource.Table(table_name)
            table.load()
            exists = True
        except ClientError as err:
            if err.response['Error']['Code'] == 'ResourceNotFoundException':
                exists = False
            else:
                logger.error(
                    "Couldn't check for existence of %s. Here's why: %s: %s",
                    table_name,
                    err.response['Error']['Code'], err.response['Error']['Message'])
                raise
        else:
            self.table = table
        return exists
    
    def create_table(self, table_name):
        """
        Creates an Amazon DynamoDB table that can be used to store movie data.
        The table uses the release year of the movie as the partition key and the
        title as the sort key.
        :param table_name: The name of the table to create.
        :return: The newly created table.
        """
        try:
            self.table = self.dyn_resource.create_table(
        TableName=table_name,
        KeySchema=[
            {
                'AttributeName': 'email',
                'KeyType': 'HASH'
            }
        ],
        AttributeDefinitions=[
            {
                'AttributeName': 'email',
                'AttributeType': 'S'
            },
        ],
        ProvisionedThroughput={
            'ReadCapacityUnits': 5,
            'WriteCapacityUnits': 5
        }
    )
            self.table.wait_until_exists()
        except ClientError as err:
            logger.error(
                "Couldn't create table %s. Here's why: %s: %s", table_name,
                err.response['Error']['Code'], err.response['Error']['Message'])
            raise
        else:
            return self.table
        
    
    def get_balance(self, email):
        """
         Gets user balance from the table.
        :param email: The email of the user.
        :return: The balance of the requested user.
        """
        try:
            response = self.table.get_item(Key={'email': email})
        except ClientError as err:
            logger.error(
                "Couldn't get user %s from table %s. Here's why: %s: %s",
                email, self.table.name,
                err.response['Error']['Code'], err.response['Error']['Message'])
            raise
        else:
            if response.get('Item') == None:
                data = {"email": email, "balance": 0}
                self.add_amount(data)
                return data['balance']
            else:
                return response["Item"]['balance']
            
    def add_amount(self, data):
        """
         Adds balance to the table.
        :param data: The balance of the user.
        """
        try:
            self.table.put_item(
                Item= {
                'email' : data['email'],
                'balance' : data['balance']})
        
        except ClientError as err:
            logger.error(
                "Couldn't add user %s to table %s. Here's why: %s: %s",
                data['email'], self.table.name,
                err.response['Error']['Code'], err.response['Error']['Message'])
            raise
            
                    
    def update_balance(self, data):
        """
         Updates balance of the in the table.
        :param data: The email and balance of the user.
        :return: The fields that were updated, with their new values.
        """
        try:
            balance = self.get_balance(data['email'])
            balance += data['amount']
            response = self.table.update_item(
                Key={'email': data['email']},
                UpdateExpression="set balance=:b",
                ExpressionAttributeValues={
                    ':b': balance},
                ReturnValues="UPDATED_NEW")
        except ClientError as err:
            logger.error(
                "Couldn't update movie %s in table %s. Here's why: %s: %s",
                title, self.table.name,
                err.response['Error']['Code'], err.response['Error']['Message'])
            raise
        else:
            print("response['Attributes']", response['Attributes'])
            return response['Attributes']
        
    def pay_amount(self, data):
        """
         Updates balance of the in the table.
        :param data: The email and balance of the user.
        :return: The fields that were updated, with their new values.
        """
        try:
            balance = self.get_balance(data['email'])
            if balance < data['amount']:
                return "not enough balance"
            balance -= data['amount']
            response = self.table.update_item(
                Key={'email': data['email']},
                UpdateExpression="set balance=:b",
                ExpressionAttributeValues={
                    ':b': balance},
                ReturnValues="UPDATED_NEW")
        except ClientError as err:
            logger.error(
                "Couldn't update movie %s in table %s. Here's why: %s: %s",
                title, self.table.name,
                err.response['Error']['Code'], err.response['Error']['Message'])
            raise
        else:
            return response['Attributes']
    

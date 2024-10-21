import json
import boto3
from boto3.dynamodb.conditions import Key
from datetime import datetime
from botocore.exceptions import ClientError  # Correct import for ClientError
import logging


dynamodb = boto3.resource('dynamodb')
logger = logging.getLogger()
logger.setLevel(logging.INFO)

def lambda_handler(event, context):
    http_method = event['httpMethod']
    path = event['path']
    
    # Route the requests based on method and path for QUIZ SECTION
    if path == "/quiz" and http_method == "POST":                        
        return create_quiz(event)
    elif path == "/quiz" and http_method == "PUT":                   
        return update_quiz(event)
    elif path == "/quiz" and http_method == "GET":                   
        return list_quizzes(event)
    elif path.startswith("/quiz/") and http_method == "GET":   
        return get_quiz(event)
    elif path.startswith("/quiz/") and http_method == "DELETE":      
        return delete_quiz(event)
    

# Route the requests based on method and path for QUESTION SECTION
    elif path == "/question" and http_method == "POST":
        return add_question(event)
    elif path.startswith("/question/") and http_method == "GET":
        return get_question(event) 
    elif path == "/question" and http_method=="PUT":
        return update_question(event)
    elif path.startswith("/question/") and http_method == "DELETE":
        return delete_question(event)
    


# Route the requests based on method and path for USER SECTION   
    elif path == "/user/start" and http_method == "POST":
        return start_quiz(event)
    elif path == "/user/submit" and http_method == "PUT":
        return submit_quiz(event)
    else:
        return {
            'statusCode': 400,
            'body': json.dumps('Unsupported route')
        }


# Function to get current timestamp
def get_current_timestamp():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


# Functions for each operation, organized by perspective
def create_quiz(event):
    data = json.loads(event['body'])
    table = dynamodb.Table('QuizBS')
    item = {
        'quiz_id': data['quiz_id'],
        'title': data['title'],
        'description': data['description'],
        'teacher_id': data['teacher_id'],
        'teacher_name': data['teacher_name'],
        'created_at': get_current_timestamp(),
        'updated_at': get_current_timestamp()
    }
    table.put_item(Item=item)
    return {
        'statusCode': 200,
        'body': json.dumps('Quiz created successfully')
    }

def update_quiz(event):
    data = json.loads(event['body'])
    table = dynamodb.Table('QuizBS')
    response = table.update_item(
        Key={'quiz_id': data['quiz_id']},
        UpdateExpression="set title=:t, description=:d, updated_at=:u",
        ExpressionAttributeValues={
            ':t': data['title'],
            ':d': data['description'],
            ':u': get_current_timestamp()
        },
        ReturnValues="UPDATED_NEW"
    )
    return {
        'statusCode': 200,
        'body': json.dumps('Quiz updated successfully')
    }

def list_quizzes(event):
    table = dynamodb.Table('QuizBS')
    response = table.scan()  # Fetches all items from the table; consider using Query if possible with specific attributes
    quizzes = response.get('Items', [])
    
    return {
        'statusCode': 200,
        'body': json.dumps(quizzes)
    }

def get_quiz(event):
    quiz_id = event['pathParameters']['id']  # Assuming path is /quiz/{id}
    table = dynamodb.Table('QuizBS')
    response = table.get_item(
        Key={'quiz_id': quiz_id}
    )
    quiz = response.get('Item')
    
    if quiz:
        return {
            'statusCode': 200,
            'body': json.dumps(quiz)
        }
    else:
        return {
            'statusCode': 404,
            'body': json.dumps('Quiz not found')
        }


    

def delete_quiz(event):  # New delete function
    quiz_id = event['pathParameters']['id']  # Assuming path is /quiz/{id}
    table = dynamodb.Table('QuizBS')
    
    # Attempt to delete the quiz with the given quiz_id
    response = table.delete_item(
        Key={'quiz_id': quiz_id},
        ConditionExpression="attribute_exists(quiz_id)"  # Ensures the quiz exists before deleting
    )
    
    return {
        'statusCode': 200,
        'body': json.dumps(f'Quiz {quiz_id} deleted successfully')
    }

def add_question(event):
    data = json.loads(event['body'])
    table = dynamodb.Table('QuestionBS')
    item = {
        'question_id': data['question_id'],
        'quiz_id': data['quiz_id'],
        'question_text': data['question_text'],
        'options': data['options'],
        'correct_option': data['correct_option'],
        'created_at': get_current_timestamp()
    }
    table.put_item(Item=item)
    return {
        'statusCode': 200,
        'body': json.dumps('Question added successfully')
    }

def get_question(event):
    quiz_id = event['pathParameters']['quiz_id']
    question_id = event['pathParameters']['question_id']
    table = dynamodb.Table('QuestionBS')
    try:
        response = table.get_item(
            Key={
                'quiz_id': quiz_id,
                'question_id': question_id
            }
        )
        if 'Item' in response:
            return {'statusCode': 200, 'body': json.dumps(response['Item'])}
        else:
            return {'statusCode': 404, 'body': json.dumps('Question not found')}
    except Exception as e:
        return {'statusCode': 400, 'body': json.dumps(str(e))}



def update_question(event):
    try:
        # Parse the request body
        data = json.loads(event['body'])
        
        # Extract quiz_id and question_id from the request body
        quiz_id = data['quiz_id']
        question_id = data['question_id']

        # Access the Question Table
        table = dynamodb.Table('QuestionBS')
        
        # Update the question in DynamoDB
        response = table.update_item(
            Key={
                'quiz_id': quiz_id,
                'question_id': question_id
            },
            UpdateExpression="set question_text = :q, options = :o, correct_option = :c",
            ExpressionAttributeValues={
                ':q': data['question_text'],
                ':o': data['options'],
                ':c': data['correct_option']
            },
            ReturnValues="UPDATED_NEW"
        )
        
        return {
            'statusCode': 200,
            'body': json.dumps('Question updated successfully')
        }
    
    except Exception as e:
        return {
            'statusCode': 400,
            'body': json.dumps(f"Error: {str(e)}")
        }


def delete_question(event):
    quiz_id = event['pathParameters']['quiz_id']
    question_id = event['pathParameters']['question_id']
    table = dynamodb.Table('QuestionBS')
    try:
        response = table.delete_item(
            Key={
                'quiz_id': quiz_id,
                'question_id': question_id
            }
        )
        return {'statusCode': 200, 'body': json.dumps('Question deleted successfully')}
    except Exception as e:
        return {'statusCode': 400, 'body': json.dumps(str(e))}
    
    

def start_quiz(event):
    data = json.loads(event['body'])
    table = dynamodb.Table('UserBS')
    item = {
        'user_id': data['user_id'],
        'quiz_id': data['quiz_id'],
        'status': 'in progress',
        'score': 0,
        'attempted_at': get_current_timestamp(),
        'submitted_at': '',
        'time_taken': 0
    }
    table.put_item(Item=item)
    return {
        'statusCode': 200,
        'body': json.dumps('Quiz started successfully')
    }

def submit_quiz(event):
    data = json.loads(event['body'])
    table = dynamodb.Table('UserBS')
    response = table.update_item(
        Key={
            'user_id': data['user_id'],
            'quiz_id': data['quiz_id']
        },
        UpdateExpression='SET status = :status, score = :score, submitted_at = :submitted_at, time_taken = :time_taken',
        ExpressionAttributeValues={
            ':status': 'completed',
            ':score': data['score'],
            ':submitted_at': get_current_timestamp(),
            ':time_taken': data['time_taken']
        },
        ReturnValues="UPDATED_NEW"
    )
    return {
        'statusCode': 200,
        'body': json.dumps('Quiz submitted successfully')
    }


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
    elif path == "/user" and http_method == "POST":
        return create_user(event)
    elif path == "/user/start" and http_method == "POST":
        return start_quiz(event)
    elif path == "/user/submit" and http_method == "PUT":
        return submit_quiz(event)
    elif path == "/user" and http_method == "GET":
        return list_users(event)
    else:
        return {
           'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'OPTIONS,POST,GET,PUT',
                'Access-Control-Allow-Headers': 'Content-Type',
            },
            'body': json.dumps('Unsupported route')
        }

# Function to get current timestamp
def get_current_timestamp():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

# Functions for each operation, organized by perspective

#QUIZ
def create_quiz(event):
    try:
        # Parse incoming data
        data = json.loads(event['body'])
        
        # Define the DynamoDB table
        table = dynamodb.Table('QQBS')
        
        # Insert main quiz item
        quiz_item = {
            'PK': data['PK'],               # Quiz identifier
            'SK': data['SK'],               # Static metadata identifier
            'teacher_id': data['teacher_id'],
            'title': data['title'],
            'description': data['description'],
            'created_at': get_current_timestamp(),
            'updated_at': get_current_timestamp()
        }
        table.put_item(Item=quiz_item)
        
        # Insert each question as a separate item linked to the quiz
        for question in data['questions']:
            question_item = {
                'PK': data['PK'],            # Same as quiz PK to group items
                'SK': question['SK'],        # Unique question SK
                'question_text': question['question_text'],
                'options': question['options'],
                'correct_option': question['correct_option'],
                'created_at': get_current_timestamp()
            }
            table.put_item(Item=question_item)

        # Return success response
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'  # CORS Header
            },
            'body': json.dumps({'success': True, 'message': 'Quiz and questions created successfully'})
        }
    
    except Exception as e:
        # Return error response
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({'success': False, 'message': f"Error creating quiz: {str(e)}"})
        }

def list_quizzes(event):
    table = dynamodb.Table('QQBS')
    response = table.scan()  # Fetches all items from the table; consider using Query if possible with specific attributes
    quizzes = response.get('Items', [])
    
    return {
        'statusCode': 200,
        'body': json.dumps(quizzes)
    }
    
def get_quiz(event):
    try:
        # Extract quiz_id from the path parameters
        quiz_id = event['pathParameters']['quiz_id']  # Assuming the API path is /quiz/{quiz_id}
        table = dynamodb.Table('QQBS')

        # Construct the primary key for retrieval
        pk_value = f"QUIZ#{quiz_id}"  # This constructs the PK

        # Fetch the quiz item from DynamoDB
        response = table.get_item(
            Key={
                'PK': pk_value,  # Use the correctly formatted PK
                'SK': 'META'     # Assuming SK is 'META' for quiz metadata
            }
        )
        quiz = response.get('Item')

        if quiz:
            # Fetch associated questions for this quiz
            questions = fetch_questions_for_quiz(quiz_id)  # Fetch questions if necessary
            quiz['questions'] = questions  # Add questions to the quiz response
            return {
                'statusCode': 200,
                'body': json.dumps(quiz)
            }
        else:
            return {
                'statusCode': 404,
                'body': json.dumps('Quiz not found')
            }
    except KeyError:
        return {
            'statusCode': 400,
            'body': json.dumps('Missing quiz ID in the request')
        }
        
def delete_quiz(event):
    # Check if pathParameters and id are present
    if 'pathParameters' not in event or 'quiz_id' not in event['pathParameters']:
        return {
            'statusCode': 400,
            'body': json.dumps('Missing quiz ID in path parameters.')
        }
    # Extract the quiz_id from the path parameters
    quiz_id = event['pathParameters']['quiz_id']  # Assuming the API path is /quiz/{quiz_id}
    table = dynamodb.Table('QQBS')
    # Construct the primary key values
    pk_value = f"QUIZ#{quiz_id}"  # Create the PK from quiz_id
    sk_value = "META"  # Assuming you are deleting the metadata item
    try:
        # Attempt to delete the quiz with the given PK and SK
        response = table.delete_item(
            Key={
                'PK': pk_value,
                'SK': sk_value
            },
            ConditionExpression="attribute_exists(PK)"  # Ensure the item exists before deleting
        )
        return {
            'statusCode': 200,
            'body': json.dumps(f'Quiz {quiz_id} deleted successfully')
        }
    except ClientError as e:
        # Handle specific client errors
        if e.response['Error']['Code'] == 'ConditionalCheckFailedException':
            return {
                'statusCode': 404,
                'body': json.dumps('Quiz not found or already deleted.')
            }
        return {
            'statusCode': 500,
            'body': json.dumps(f'Error deleting quiz: {str(e)}')
        }

#QUESTION
def get_question(event):
    # Extract quiz_id and question_id from path parameters
    quiz_id = event['pathParameters']['quiz_id']  # e.g., 'ai'
    question_id = event['pathParameters']['question_id']  # e.g., 'python_q1'
    table = dynamodb.Table('QQBS')  # Replace with your actual table name
    # Construct the primary key for the question
    pk_value = f'QUIZ#{quiz_id}'  # Partition key for the quiz
    sk_value = f'Q#{question_id}'  # Sort key for the specific question
    try:
        # Retrieve the specific question using both PK and SK
        response = table.get_item(
            Key={
                'PK': pk_value,
                'SK': sk_value
            }
        )
        
        if 'Item' in response:
            return {
                'statusCode': 200,
                'body': json.dumps(response['Item'])  # Return the question details
            }
        else:
            return {
                'statusCode': 404,
                'body': json.dumps('Question not found')
            }
    except Exception as e:
        return {
            'statusCode': 400,
            'body': json.dumps(str(e))  # Return error message
        }

def fetch_questions_for_quiz(quiz_id):
    table = dynamodb.Table('QQBS')
    
    # Construct the PK for the quiz
    pk_value = f"QUIZ#{quiz_id}"

    # Query to find questions associated with the quiz
    response = table.query(
        KeyConditionExpression=Key('PK').eq(pk_value) & Key('SK').begins_with('Q#')
    )
    
    questions = response.get('Items', [])  # Get the list of questions
    return questions

def add_question(event):
    data = json.loads(event['body'])
    table = dynamodb.Table('QQBS')
    item = {
        'PK': data['quiz_id'],                # Partition Key
        'SK': data['question_id'],             # Sort Key
        'question_text': data['question_text'],
        'options': data['options'],
        'correct_option': data['correct_option'],
        'created_at': get_current_timestamp()
    }
    table.put_item(Item=item)
    return {
        'statusCode': 200,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*',  # Allow all domains for CORS
            'Access-Control-Allow-Methods': 'POST, OPTIONS',  # Specify allowed methods
            'Access-Control-Allow-Headers': 'Content-Type'  # Specify allowed headers
        },
        'body': json.dumps('Question added successfully')
    }

def delete_question(event):
    # Extract quiz_id and question_id from the path parameters
    quiz_id = event['pathParameters']['quiz_id']
    question_id = event['pathParameters']['question_id']

    # Define the table resource
    table = dynamodb.Table('QQBS')

    # Construct the keys based on the table's structure
    pk_value = f"QUIZ#{quiz_id}"  # Primary key
    sk_value = f"Q#{question_id}"  # Sort key

    try:
        # Attempt to delete the question
        response = table.delete_item(
            Key={
                'PK': pk_value,
                'SK': sk_value
            },
            ConditionExpression="attribute_exists(PK)"  # Ensures the question exists
        )

        # Return success response
        return {
            'statusCode': 200,
            'body': json.dumps('Question deleted successfully'),
            'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*',  # Allow all domains for CORS
            'Access-Control-Allow-Methods': 'DELETE, OPTIONS',  # Specify allowed methods
            'Access-Control-Allow-Headers': 'Content-Type'  # Specify allowed headers
        },
        }

    except ClientError as e:
        # Check if the error is because the item does not exist
        if e.response['Error']['Code'] == 'ConditionalCheckFailedException':
            return {
                'statusCode': 404,
                'body': json.dumps('Question not found')
            }
        else:
            # Return any other errors
            return {
                'statusCode': 400,
                'body': json.dumps(str(e))
            }

    
#USER

def create_user(event):
    table = dynamodb.Table('UserBS')
    """Function to create a new user profile."""
    try:
        data = json.loads(event['body'])
        user_id = data.get('user_id')

        if not user_id:
            return {
                'headers': {
                    'Access-Control-Allow-Origin': '*',
                    'Access-Control-Allow-Methods': 'OPTIONS,POST,GET,PUT',
                    'Access-Control-Allow-Headers': 'Content-Type',
                },
                'body': json.dumps({'error': 'User ID is required'})
            }

        # Put item in DynamoDB
        table.put_item(Item={
            'PK': f'USER#{user_id}',
            'SK': 'PROFILE',
            'name': user_id,
            'created_at': event['requestContext']['requestTime']
        })

        return {
            'statusCode': 200,
             'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'OPTIONS,POST,GET,PUT',
                'Access-Control-Allow-Headers': 'Content-Type',
            },
            'body': json.dumps({'message': 'User created successfully'})
        }
    
    except ClientError as e:
        return {
             'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'OPTIONS,POST,GET,PUT',
                'Access-Control-Allow-Headers': 'Content-Type',
            },
            'body': json.dumps({'error': str(e)})
        }
    except json.JSONDecodeError:
        return {
            'statusCode': 400,
           'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'OPTIONS,POST,GET,PUT',
                'Access-Control-Allow-Headers': 'Content-Type',
            },
            'body': json.dumps({'error': 'Invalid JSON format'})
        }
def list_users(event):
    # Initialize a DynamoDB client
    table = dynamodb.Table('UserBS')
    # Scan the table to get all users
    response = table.scan()
    users = response.get('Items', [])
    
    # Extract user IDs
    user_ids = [user['user_id'] for user in users]  # List comprehension to get user IDs

    # Return the response with user IDs
    return {
        'statusCode': 200,
        'body': json.dumps(user_ids)
    }
    
def start_quiz(event):
    data = json.loads(event['body'])
    user_id = data['user_id']
    quiz_id = data['quiz_id']
    
    # Define the DynamoDB table for quizzes
    quiz_table = dynamodb.Table('QQBS')
    
    # Check if the quiz exists
    response = quiz_table.get_item(
        Key={
            'PK': quiz_id,  # Use the correct PK format for your quiz
            'SK': 'META'    # Assuming SK for the metadata
        }
    )
    
    if 'Item' not in response:
        return {
            'statusCode': 404,
            'body': json.dumps('Quiz not found')
        }

    # Proceed to create user quiz entry if quiz exists
    user_table = dynamodb.Table('UserBS')
    item = {
        'user_id': user_id,
        'quiz_id': quiz_id,
        'status': 'in progress',
        'score': 0,
        'attempted_at': get_current_timestamp(),
        'submitted_at': '',
        'time_taken': 0
    }
    user_table.put_item(Item=item)
    
    return {
        'statusCode': 200,
        'body': json.dumps('Quiz started successfully')
    }

def submit_quiz(event):
    logger.info("Starting submit_quiz function.")
    
    try:
        # Parse incoming data
        data = json.loads(event['body'])
        user_id = data.get('user_id')
        quiz_id = data.get('quiz_id')
        score = data.get('score')
        time_taken = data.get('time_taken')
        
        # Log data for debugging
        logger.info(f"Parsed Data - User ID: {user_id}, Quiz ID: {quiz_id}, Score: {score}, Time Taken: {time_taken}")
        
        if not all([user_id, quiz_id, time_taken]) or score is None:
            raise ValueError("One or more required fields are missing or null")


        # Define the DynamoDB table for users
        table = dynamodb.Table('UserBS')
        
        # Update user quiz submission details
        response = table.update_item(
            Key={
                'user_id': user_id,
                'quiz_id': quiz_id
            },
            UpdateExpression='SET #s = :status, #sc = :score, submitted_at = :submitted_at, time_taken = :time_taken',
            ExpressionAttributeNames={
                '#s': 'status',
                '#sc': 'score'
            },
            ExpressionAttributeValues={
                ':status': 'completed',
                ':score': score,
                ':submitted_at': get_current_timestamp(),
                ':time_taken': time_taken
            },
            ReturnValues="UPDATED_NEW"
        )
        
        logger.info("DynamoDB update successful.")
        return {
            'statusCode': 200,
            'body': json.dumps('Quiz submitted successfully')
        }
    
    except ClientError as e:
        logger.error(f"DynamoDB ClientError: {e.response['Error']['Message']}")
        return {
            'statusCode': 500,
            'body': json.dumps(f"DynamoDB error: {e.response['Error']['Message']}")
        }
    except ValueError as ve:
        logger.error(f"Validation Error: {str(ve)}")
        return {
            'statusCode': 400,
            'body': json.dumps(f"Bad request: {str(ve)}")
        }
    except Exception as e:
        logger.error(f"General Error: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps(f'Internal server error: {str(e)}')
        }
import app  # Import your Lambda function file if it's named app.py

def test_lambda():
    event = {
        'httpMethod': 'DELETE',
        'path': '/question/python/python_q1',
        'headers': {
            'Content-Type': 'application/json'
        }
    }
    # Mock context
    context = {}
    
    response = app.lambda_handler(event, context)
    print('Response:', response)

if __name__ == "__main__":
    test_lambda()

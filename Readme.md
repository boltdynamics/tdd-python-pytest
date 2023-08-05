# Test Driven Development (TDD) with Python

### Prerequisites

- Python 3
- Poetry (for managing Python environments)

### Initialize a Poetry project

Run `poetry init` to initialize a Poetry project in guided mode. This will create a pyproject.toml and install the following python packages in the virtual environment:

- pytest (for running unit tests)
- pytest-cov (for generating coverage reports)
- pytest-mock (for mocking dependencies in unit tests)

### 3 rules of TDD

- ***RED*** -> write a test that fails.
- ***GREEN*** -> implement the test-supporting functionality to pass the test.
- ***REFACTOR*** -> improve the production code AND the tests to absolute perfection.

### AWS Rekognition App

For the purpose of demonstrating TDD, we will develop an AWS Rekognition app. The AWS Rekognition app will have,

- A `get_image_bytes()` takes an image path returns the image bytes.
- A `detect_labels()` returns a list of objects detected in the image.
- A `detect_celebrities()` returns a list of faces detected in the image.
- A `detect_text()` returns a list of text detected in the image.

### Define requirements for AWS Rekognition app

- `get_image_bytes()` function takes an image file path as an argument and returns the image bytes.
    - It should be able to read and return the bytes of an existing image file.
    - It should raise an exception when an invalid/non-existing image path is provided.

- `detect_labels()` function takes an image file path as an argument and returns a list of objects detected in the image.
    - It should return a list of labels in dict format.
    - It should catch the following exceptions and raise a retry exception when they occur:
        - ThrottlingException
        - InternalServerError

- `detect_text` function takes an image file path as an argument and returns a list of text detected in the image.
    - It should return a list of text detected in the image in dict format.
    - It should catch the following exceptions and raise a retry exception when they occur:
        - ThrottlingException
        - InternalServerError

- `detect_celebrities()` function takes an image file path as an argument and returns a list of celebrities detected in the image.
    - It should return a list of recognized celebrities and unknown people in dict format.
    - It should catch the following exceptions and raise a retry exception when they occur:
        - ThrottlingException
        - InternalServerError

### Starting development with TDD

1. Write a test for `get_image_bytes` function in `tests/test_rekognition.py` to validate function returns bytes. This is the ***RED*** step.

```python
import pytest
from rekognition import Rekognition
from botocore.exceptions import ClientError

rekognition = Rekognition()

def test_get_image_bytes_valid_image():
    """
    Test that the get_image_bytes method returns the bytes of an image file.
    """
    image_bytes = rekognition.get_image_bytes("src/images/city.jpg")

    assert isinstance(image_bytes, bytes)
    assert len(image_bytes) > 0
```

This will fail because the `get_image_bytes()` function is not implemented yet. Run `make test` to run the test.

2. Implement the test-supporting functionality to pass the test. For example, implement the `get_image_bytes()` function in `rekognition.py` to return the image bytes. This is the ***GREEN*** step.

```python
@staticmethod
def get_image_bytes(image_path):
    with open(image_path, "rb") as image_file:
        return image_file.read()
```

3. Also test for invalid/non-existing image path.

```python
def test_non_existing_image_path():
    """
    Test that the get_image_bytes method raises a FileNotFoundError when the image path is invalid.
    """
    image_path = "non_existing_image.jpg"

    with pytest.raises(FileNotFoundError):
        rekognition.get_image_bytes(image_path)
```

4. Write a test for `detect_labels()` function in `tests/test_rekognition.py` to validate function returns a list of labels in dict format. This is the ***RED*** step.

```python
def test_detect_labels(mocker):
    """
    Test that the detect_labels method returns a list of objects detected in an image.
    """
    mocker.patch.object(rekognition.rekognition_client, "detect_labels", return_value={"Labels": [
        {"Name": "Building", "Confidence": 99.9999771118164},
        {"Name": "City", "Confidence": 99.9999771118164}
    ]})

    labels = rekognition.detect_labels("src/images/city.jpg")

    assert isinstance(labels, list)
    assert len(labels) > 0

    assert labels[0]["Name"] == "Building"
    assert labels[0]["Confidence"] == 99.9999771118164
    assert labels[1]["Name"] == "City"
    assert labels[1]["Confidence"] == 99.9999771118164
```

This will fail because the `detect_labels()` function is not implemented yet. Run `make test` to run the test.

5. Implement the test-supporting functionality to pass the test. For example, implement the `detect_labels()` function in `rekognition.py` to return a list of labels in dict format. This is the ***GREEN*** step.

```python
def detect_labels(self, image_path):
    image_bytes = self.get_image_bytes(image_path)

    response = self.rekognition_client.detect_labels(Image={"Bytes": image_bytes})

    return response["Labels"]
```

6. Also test for `ThrottlingException` and `InternalServerError` exceptions.

```python
def test_detect_labels_retry(mocker):
    """
    Test that the detect_labels method retries when InternalServerErrorException  or ThrottlingException occurs.
    """
    mocker.patch.object(
        rekognition.rekognition_client,
        "detect_labels",
        side_effect=[
            ClientError(
                {
                    "Error": {
                        "Code": "InternalServerError",
                        "Message": "service is down",
                    }
                },
                "detect_labels",
            )
        ],
    )

    with pytest.raises(ClientError):
        error = rekognition.detect_labels("src/images/city.jpg")
        assert error["Error"]["Code"] == "InternalServerError"

    # throttling exception
    mocker.patch.object(
        rekognition.rekognition_client,
        "detect_labels",
        side_effect=[
            ClientError(
                {
                    "Error": {
                        "Code": "ThrottlingException",
                        "Message": "service is down",
                    }
                },
                "detect_labels",
            )
        ],
    )

    with pytest.raises(ClientError):
        error = rekognition.detect_labels("src/images/city.jpg")
        assert error["Error"]["Code"] == "ThrottlingException"
```

6. Write a test for `detect_text()` function in `tests/test_rekognition.py` to validate function returns a list of text detected in the image in dict format. This is the ***RED*** step.

```python
def test_detect_text(mocker):
    """
    Test that the detect_text method returns a list of text detected in an image.
    """
    mocker.patch.object(rekognition.rekognition_client, "detect_text", return_value={"TextDetections": [
        {"DetectedText": "Hello", "Confidence": 99.9999771118164},
        {"DetectedText": "World", "Confidence": 99.9999771118164}
    ]})

    text = rekognition.detect_text("src/images/city.jpg")

    assert isinstance(text, list)
    assert len(text) > 0

    assert text[0]["DetectedText"] == "Hello"
    assert text[0]["Confidence"] == 99.9999771118164
    assert text[1]["DetectedText"] == "World"
    assert text[1]["Confidence"] == 99.9999771118164
```

This will fail because the `detect_text()` function is not implemented yet. Run `make test` to run the test.

7. Implement the test-supporting functionality to pass the test. For example, implement the `detect_text()` function in `rekognition.py` to return a list of text detected in the image in dict format. This is the ***GREEN*** step.

```python
def detect_text(self, image_path):
    image_bytes = self.get_image_bytes(image_path)

    response = self.rekognition_client.detect_text(Image={"Bytes": image_bytes})

    return response["TextDetections"]
```

8. Write a test for `detect_celebrities()` function in `tests/test_rekognition.py` to validate function returns a list of recognized celebrities and unknown people in dict format. This is the ***RED*** step.

```python
def test_detect_celebrities(mocker):
    """
    Test that the detect_celebrities method returns a list of celebrities detected in an image.
    """
    mocker.patch.object(rekognition.rekognition_client, "recognize_celebrities", return_value={"CelebrityFaces": [
        {"Name": "Chris Hemsworth", "Urls": ['www.wikidata.org/wiki/Q54314', 'www.imdb.com/name/nm1165110'], "MatchConfidence": 99.9999771118164},
        {"Name": "Chris Evans", "Urls": ['www.wikidata.org/wiki/asdasd', 'www.imdb.com/name/2123213'], "MatchConfidence": 99.8}
    ]})

    celebrities = rekognition.detect_celebrities("src/images/city.jpg")

    assert isinstance(celebrities, list)
    assert len(celebrities) > 0

    assert celebrities[0]["Name"] == "Chris Hemsworth"
    assert celebrities[0]["Urls"] == ['www.wikidata.org/wiki/Q54314', 'www.imdb.com/name/nm1165110']
    assert celebrities[0]["MatchConfidence"] == 99.9999771118164
    assert celebrities[1]["Name"] == "Chris Evans"
    assert celebrities[1]["Urls"] == ['www.wikidata.org/wiki/asdasd', 'www.imdb.com/name/2123213']
    assert celebrities[1]["MatchConfidence"] == 99.8
```

This will fail because the `detect_celebrities()` function is not implemented yet. Run `make test` to run the test.

9. Implement the test-supporting functionality to pass the test. For example, implement the `detect_celebrities()` function in `rekognition.py` to return a list of recognized celebrities and unknown people in dict format. This is the ***GREEN*** step.

```python
def detect_celebrities(self, image_path):
    image_bytes = self.get_image_bytes(image_path)

    response = self.rekognition_client.recognize_celebrities(
        Image={"Bytes": image_bytes}
    )

    return response["CelebrityFaces"]
```

### Complex code is hard to read and maintain

The `complex_aws_interaction()` function below is hard to read and maintain. It is also hard to test the function because it has multiple dependencies. It is also hard to mock the dependencies in unit tests.

If you break down the functionality of this complex function, it is,
* Initializing AWS clients.
* Uploading a file to S3.
* Triggering a Lambda function.
* Retrieving the result from Lambda.
* Storing the result in DynamoDB.

```python
def complex_aws_interaction(bucket_name, file_path, lambda_function_name):
    # Initialize AWS clients
    s3_client = boto3.client("s3")
    lambda_client = boto3.client("lambda")
    dynamodb_client = boto3.client("dynamodb")

    # Upload the file to S3
    with open(file_path, "rb") as file:
        s3_client.upload_fileobj(file, bucket_name, file_path)

    # Trigger the Lambda function
    response = lambda_client.invoke(
        FunctionName=lambda_function_name,
        InvocationType="RequestResponse",
        Payload=f'{{"bucket": "{bucket_name}", "file_path": "{file_path}"}}',
    )

    # Retrieve the result from Lambda
    result = response["Payload"].read().decode("utf-8")

    # Store the result in DynamoDB
    dynamodb_client.put_item(
        TableName="ResultTable",
        Item={
            "BucketName": {"S": bucket_name},
            "FilePath": {"S": file_path},
            "Result": {"S": result},
        },
    )
```

Lets see what the test for this complex function could look like,

```python
# test data
bucket_name = "test-bucket"
file_path = "test_file.txt"
lambda_function_name = "test-lambda-function"
lambda_payload = f'{{"bucket": "{bucket_name}", "file_path": "{file_path}"}}'
lambda_result = '{"status": "success"}'


def test_complex_aws_interaction(mocker):
    boto3_client_mock = mocker.patch("boto3.client")

    # Call the complex_aws_interaction function
    complex_aws_interaction(bucket_name, file_path, lambda_function_name)

    # Assert that the file was uploaded to S3
    boto3_client_mock.return_value.upload_fileobj.assert_called_once()

    # Assert that the Lambda function was invoked with the correct parameters
    boto3_client_mock.return_value.invoke.assert_called_once_with(
        FunctionName=lambda_function_name,
        InvocationType="RequestResponse",
        Payload=lambda_payload,
    )

    # Assert that the result was stored in DynamoDB
    boto3_client_mock.return_value.put_item.assert_called_once_with(
        TableName="ResultTable",
        Item={
            "BucketName": {"S": bucket_name},
            "FilePath": {"S": file_path},
            "Result": {"S": lambda_result},
        },
    )
```

Even the test for this complex function is hard to read and maintain.

### Refactoring complex code

Lets refactor the `complex_aws_interaction()` function to make it more readable and maintainable.

```python
def complex_aws_interaction(bucket_name, file_path, lambda_function_name):
    # Initialize AWS clients
    s3_client = boto3.client("s3")
    lambda_client = boto3.client("lambda")
    dynamodb_client = boto3.client("dynamodb")

    # Upload the file to S3
    upload_file_to_s3(s3_client, file_path, bucket_name)

    # Trigger the Lambda function
    result = trigger_lambda_function(lambda_client, lambda_function_name, bucket_name, file_path)

    # Store the result in DynamoDB
    store_result_in_dynamodb(dynamodb_client, bucket_name, file_path, result)


def upload_file_to_s3(s3_client, file_path, bucket_name):
    with open(file_path, "rb") as file:
        s3_client.upload_fileobj(file, bucket_name, file_path)


def trigger_lambda_function(lambda_client, lambda_function_name, bucket_name, file_path):
    response = lambda_client.invoke(
        FunctionName=lambda_function_name,
        InvocationType="RequestResponse",
        Payload=f'{{"bucket": "{bucket_name}", "file_path": "{file_path}"}}',
    )

    return response["Payload"].read().decode("utf-8")


def store_result_in_dynamodb(dynamodb_client, bucket_name, file_path, result):
    dynamodb_client.put_item(
        TableName="ResultTable",
        Item={
            "BucketName": {"S": bucket_name},
            "FilePath": {"S": file_path},
            "Result": {"S": result},
        },
    )
```

Now the `complex_aws_interaction()` function is more readable and maintainable. It is also easier to test the function because it has fewer dependencies.

Lets see what the test for this refactored function could look like,

```python
# test data
bucket_name = "test-bucket"
file_path = "test_file.txt"
lambda_function_name = "test-lambda-function"
lambda_payload = f'{{"bucket": "{bucket_name}", "file_path": "{file_path}"}}'
lambda_result = '{"status": "success"}'
boto3_client_mock = mocker.patch("boto3.client")

def test_upload_file_to_s3(mocker):
    # Call the upload_file_to_s3 function
    upload_file_to_s3(boto3_client_mock, file_path, bucket_name)

    # Assert that the file was uploaded to S3
    boto3_client_mock.return_value.upload_fileobj.assert_called_once()


def test_trigger_lambda_function(mocker):
    # Call the trigger_lambda_function function
    trigger_lambda_function(boto3_client_mock, lambda_function_name, bucket_name, file_path)

    # Assert that the Lambda function was invoked with the correct parameters
    boto3_client_mock.return_value.invoke.assert_called_once_with(
        FunctionName=lambda_function_name,
        InvocationType="RequestResponse",
        Payload=lambda_payload,
    )


def test_store_result_in_dynamodb(mocker):
    # Call the store_result_in_dynamodb function
    store_result_in_dynamodb(boto3_client_mock, bucket_name, file_path, lambda_result)

    # Assert that the result was stored in DynamoDB
    boto3_client_mock.return_value.put_item.assert_called_once_with(
        TableName="ResultTable",
        Item={
            "BucketName": {"S": bucket_name},
            "FilePath": {"S": file_path},
            "Result": {"S": lambda_result},
        },
    )


def test_complex_aws_interaction(mocker):
    upload_file_to_s3_mock = mocker.patch("upload_file_to_s3")
    trigger_lambda_function_mock = mocker.patch("trigger_lambda_function")
    store_result_in_dynamodb_mock = mocker.patch("store_result_in_dynamodb")

    # Call the complex_aws_interaction function
    complex_aws_interaction(bucket_name, file_path, lambda_function_name)

    # Assert that the file was uploaded to S3
    upload_file_to_s3_mock.assert_called_once_with(boto3_client_mock, file_path, bucket_name)

    # Assert that the Lambda function was invoked with the correct parameters
    trigger_lambda_function_mock.assert_called_once_with(boto3_client_mock, lambda_function_name, bucket_name, file_path)

    # Assert that the result was stored in DynamoDB
    store_result_in_dynamodb_mock.assert_called_once_with(boto3_client_mock, bucket_name, file_path, lambda_result)
```

The test for the refactored function is also more readable and maintainable.

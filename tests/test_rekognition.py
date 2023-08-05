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


def test_non_existing_image_path():
    """
    Test that the get_image_bytes method raises a FileNotFoundError when the image path is invalid.
    """
    image_path = "non_existing_image.jpg"

    with pytest.raises(FileNotFoundError):
        rekognition.get_image_bytes(image_path)


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

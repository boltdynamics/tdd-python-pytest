import boto3
import os
import json

IMAGES_DIR = os.path.join(os.path.dirname(__file__), "images")


class Rekognition:
    """
    A wrapper class for the AWS Rekognition client.
    """

    def __init__(self):
        self.rekognition_client = boto3.client("rekognition")

    @staticmethod
    def get_image_bytes(image_path):
        """
        Returns the bytes of an image file.

        Args:
            image_path (str): The path to the image file.

        Returns:
            bytes: The bytes of the image file.
        """
        with open(image_path, "rb") as image_file:
            return image_file.read()

    def detect_labels(self, image_path):
        """
        Detects objects in an image.

        Args:
            image_path (str): The path to the image file.

        Returns:
            list: A list of objects detected in the image.
        """
        image_bytes = self.get_image_bytes(image_path)

        response = self.rekognition_client.detect_labels(Image={"Bytes": image_bytes})

        return response["Labels"]

    def detect_text(self, image_path):
        """
        Detects text in an image.

        Args:
            image_path (str): The path to the image file.

        Returns:
            list: A list of text detected in the image.
        """
        image_bytes = self.get_image_bytes(image_path)

        response = self.rekognition_client.detect_text(Image={"Bytes": image_bytes})

        return response["TextDetections"]

    def detect_celebrities(self, image_path):
        """
        Detects celebrities in an image.

        Args:
            image_path (str): The path to the image file.

        Returns:
            list: A list of celebrities detected in the image.
        """
        image_bytes = self.get_image_bytes(image_path)

        response = self.rekognition_client.recognize_celebrities(
            Image={"Bytes": image_bytes}
        )

        return response["CelebrityFaces"]


if __name__ == "__main__":
    rekognition = Rekognition()

    labels = rekognition.detect_labels(os.path.join(IMAGES_DIR, "large.jpg"))
    # print(json.dumps(labels, indent=4))
    for label in labels:
        print(f"Object: {label['Name']}, Confidence: {label['Confidence']}\n")

    celebrities = rekognition.detect_celebrities(
        os.path.join(IMAGES_DIR, "chris-thor.png")
    )
    # print(json.dumps(celebrities, indent=4))
    for celebrity in celebrities:
        print(f"Name: {celebrity['Name']}\n")
        print(f"Urls: {celebrity['Urls']}\n")
        print(f"MatchConfidence: {celebrity['MatchConfidence']}\n")

    text = rekognition.detect_text(os.path.join(IMAGES_DIR, "lifeisbeautiful.jpg"))
    # print(json.dumps(text, indent=4))
    for text_detection in text:
        print(f"Detected Text: {text_detection['DetectedText']}\n")

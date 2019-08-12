import hashlib
import boto3
from datetime import datetime

from botocore.exceptions import ClientError
from selenium import webdriver

from config import bucket_name as bk_name
from config import sender, recipient, region

url = "http://toronto.kdmid.ru/ru.aspx?lst=ru&it=/%D0%92%D1%8B%D0%B5%D0%B7%D0%B4%D0%BD%D0%BE%D0%B5%20%D0%BA%D0%BE%D0%BD%D1%81%D1%83%D0%BB%D1%8C%D1%81%D0%BA%D0%BE%D0%B5%20%D0%BE%D0%B1%D1%81%D0%BB%D1%83%D0%B6%D0%B8%D0%B2%D0%B0%D0%BD%D0%B8%D0%B5.aspx"


class Scraper:
    def __init__(self):
        self.url = url
        self.title = "ПОРЯДОК ПРОВЕДЕНИЯ ВЫЕЗДНЫХ ОБСЛУЖИВАНИЙ ПО ПАСПОРТНЫМ ВОПРОСАМ ГЕНЕРАЛЬНЫМ КОНСУЛЬСТВОМ РОССИЙСКОЙ ФЕДЕРАЦИИ В ТОРОНТО"
        self.driver = webdriver.Firefox()

    def get_content(self):
        self.driver.get(self.url)
        elem = self.driver.find_element_by_xpath("//div[./h1[text()='" + self.title + "']]")
        content = elem.text
        self.driver.close()
        return content


class S3Manager:
    def __init__(self):
        self.bucket_name = bk_name
        self.s3_client = boto3.client('s3')

    def upload_to_s3(self, file_name, dest_file):
        self.s3_client.upload_file(file_name, self.bucket_name, dest_file)

    def get_file(self, remote_file, dest_file):
        return self.s3_client.download_file(self.bucket_name, remote_file, dest_file)


class FileManager:
    def __init__(self):
        curr_datetime = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
        self.new_file_name = "{}.txt".format(curr_datetime)

    @staticmethod
    def __create_file__(file_name, text):
        with open(file_name, "w") as file:
            file.write(text)

    @staticmethod
    def read_file(file_name):
        with open(file_name, 'rb') as file:
            return file.read()

    @staticmethod
    def has_changed(previous, current):
        prev_ho = hashlib.sha3_256(previous)
        curr_ho = hashlib.sha3_256(current)
        return prev_ho.hexdigest() != curr_ho.hexdigest()

    def save_file(self, content):
        self.__create_file__(self.new_file_name, content)
        return self.new_file_name


class EmailSender:
    def __init__(self):
        self.sender = sender
        self.recipient = recipient

    def send_email(self):
        SUBJECT = "Page content changed"

        # The email body for recipients with non-HTML email clients.
        BODY_TEXT = ("Page content changed\r\n"
                     "check website: {}".format(url)
                     )

        # The HTML body of the email.
        BODY_HTML = """<html>
        <head></head>
        <body>
          <h1>Page content changed</h1>
          <p>check website:
            <a href='{}'>LINK</a>
        </body>
        </html>
                    """.format(url)

        # The character encoding for the email.
        CHARSET = "UTF-8"

        # Create a new SES resource and specify a region.
        client = boto3.client('ses', region_name=region)

        # Try to send the email.
        try:
            # Provide the contents of the email.
            response = client.send_email(
                Destination={
                    'ToAddresses': [
                        self.recipient,
                    ],
                },
                Message={
                    'Body': {
                        'Html': {
                            'Charset': CHARSET,
                            'Data': BODY_HTML,
                        },
                        'Text': {
                            'Charset': CHARSET,
                            'Data': BODY_TEXT,
                        },
                    },
                    'Subject': {
                        'Charset': CHARSET,
                        'Data': SUBJECT,
                    },
                },
                Source=self.sender,
            )
        # Display an error if something goes wrong.
        except ClientError as e:
            print(e.response['Error']['Message'])
        else:
            print("Email sent! Message ID:"),
            print(response['MessageId'])

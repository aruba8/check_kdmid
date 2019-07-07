
from scraper import Scraper, S3Manager, FileManager, EmailSender

scraper = Scraper()
content = scraper.get_content()
file_manager = FileManager()
file_name = file_manager.save_file(content)


s3 = S3Manager()

s3.get_file("latest.txt", "latest.txt")

latest_content = file_manager.read_file("latest.txt")
current_content = file_manager.read_file(file_name)
has_changed = file_manager.has_changed(latest_content, current_content)

s3.upload_to_s3(file_name, file_name)
s3.upload_to_s3(file_name, "latest.txt")

if has_changed:
    e = EmailSender()
    e.send_email()









import imaplib
import email
from email.header import decode_header
from dotenv import load_dotenv
import os
import re
import requests
import time

load_dotenv()

# variables
EMAIL_USERNAME = os.getenv("EMAIL_USERNAME")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")
WEBHOOK_URL = os.getenv("GOOGLE_CHAT_WEBHOOK")
label = "test"


def clean(text):
    # Replace all non-printable and special characters (like \r, \n, etc.) with a space
    return re.sub(r"\s+", " ", text).strip()


# Connect to Gmail's IMAP server
def fetch_unread_emails_primary_tab(username, password):
    # Connect to the server
    imap = imaplib.IMAP4_SSL("imap.gmail.com")

    try:
        # Login to the account
        imap.login(username, password)
        print("Logged in as", username)

        # Select the "Primary" inbox
        imap.select(mailbox="INBOX", readonly=False)
        print("Selected inbox (Primary)")

        # Search for unread emails in the "Primary" tab with the specified label
        status, messages = imap.search(None, f'X-GM-LABELS "{label}" UNSEEN')

        if status != "OK":
            print("No emails found!")
            return []

        # fetch ID of the emails
        email_ids = messages[0].split()

        email_dict = {}
        for email_id in email_ids:
            # Fetch the email by ID
            res, msg = imap.fetch(email_id, "(BODY.PEEK[])")

            for response_part in msg:
                if isinstance(response_part, tuple):
                    # Parse the email
                    msg = email.message_from_bytes(response_part[1])
                    # Decode the email subject
                    subject, encoding = decode_header(msg["Subject"])[0]
                    if isinstance(subject, bytes):
                        # If it's a bytes type, decode to str
                        subject = subject.decode(encoding if encoding else "utf-8")
                    cleaned_subject = clean(subject)
                    # Add subject and email ID to the dictionary
                    email_dict[cleaned_subject] = email_id.decode()
        return email_dict

    except imaplib.IMAP4.error as e:
        print("IMAP error:", e)
        return []
    finally:
        # Close the connection and logout
        imap.close()
        imap.logout()


def send_message_to_google_chat_space(email_dict):

    for subject, id in email_dict.items():
        # Create the payload
        payload = {
            "text": f"{subject}",
        #     "cards": [
        #         {
        #             "header": {
        #                 "title": "subject",
        #                 "subtitle": "Screenshot of email body",
        #             },
        #             "sections": [
        #                 {
        #                     "widgets": [
        #                         {
        #                             "image": {
        #                                 "imageUrl": f"data:image/png;base64,{encoded_image}",
        #                                 "onClick": {
        #                                     "openLink": {"url": "https://chat.google.com"},
        #                                 },
        #                             }
        #                         }
        #                     ]
        #                 }
        #             ],
        #         }
        #     ],
        }

        # Send the payload to the Google Chat webhook
        response = requests.post(
            WEBHOOK_URL, headers={"Content-Type": "application/json"}, json=payload
        )
        if response.status_code == 200:
            print(f"Posted to Google Chat: {subject}")
            print("Marking the mail as read...")
            mark_mail_as_read(id)
        else:
            print(f"Failed to post to Google Chat: {response.text}")
            failed_mail[subject] = id


def mark_mail_as_read(id):
    # Connect to the server
    imap = imaplib.IMAP4_SSL("imap.gmail.com")

    try:
        # Login to the account
        imap.login(EMAIL_USERNAME, EMAIL_PASSWORD)
        # print("Logged in as", EMAIL_USERNAME)

        # Select the "Primary" inbox
        imap.select(mailbox="INBOX", readonly=False)
        # print("Selected inbox (Primary)")

        # Mark the email as read
        imap.store(id, "+FLAGS", "\\Seen")
        print("Marked email as read")

    except imaplib.IMAP4.error as e:
        print("Email not marked as read")
        print("IMAP error:", e)
    finally:
        # Close the connection and logout
        imap.close()
        imap.logout()


# Fetch unread emails from Primary tab
if __name__ == "__main__":
    if not EMAIL_USERNAME or not EMAIL_PASSWORD:
        print("Please set EMAIL_USERNAME and EMAIL_PASSWORD in your .env file.")
    else:
        email_dict = fetch_unread_emails_primary_tab(EMAIL_USERNAME, EMAIL_PASSWORD)
        failed_mail = send_message_to_google_chat_space(email_dict)
        if failed_mail:
            print("Waiting for 1 minute before retrying to send failed emails...")
            time.sleep(60) # wait for 1 minute
            print("Retrying...")
            send_message_to_google_chat_space(failed_mail)
        # Open a file in write mode
        with open("unread_emails.txt", "w") as file:
            for subject, id in email_dict.items():
                # Write to file
                file.write(subject + "=" + id + "\n")

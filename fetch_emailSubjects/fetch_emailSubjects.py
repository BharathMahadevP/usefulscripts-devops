import imaplib
import email
from email.header import decode_header
from dotenv import load_dotenv
import os
import re
import requests

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

        subject_lines = []
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
                    # print("Subject:", subject)
                    cleaned_subject = clean(subject)
                    subject_lines.append(cleaned_subject)
        return subject_lines

    except imaplib.IMAP4.error as e:
        print("IMAP error:", e)
        return []
    finally:
        # Close the connection and logout
        imap.close()
        imap.logout()


def send_message_to_google_chat_space(messages):

    # for message in messages:
        # Create the payload
        payload = {
            "text": f"{messages}",
            # "cards": [
            #     {
            #         "header": {
            #             "title": "subject",
            #             "subtitle": "Screenshot of email body",
            #         },
            #         "sections": [
            #             {
            #                 "widgets": [
            #                     {
            #                         # "image": {
            #                         #     "imageUrl": f"data:image/png;base64,{encoded_image}",
            #                         #     "onClick": {
            #                         #         "openLink": {"url": "https://chat.google.com"},
            #                         #     },
            #                         # }
            #                     }
            #                 ]
            #             }
            #         ],
            #     }
            # ],
        }

        # Send the payload to the Google Chat webhook
        response = requests.post(
            WEBHOOK_URL, headers={"Content-Type": "application/json"}, json=payload
        )
        if response.status_code == 200:
            print(f"Posted to Google Chat: {messages}")
        else:
            print(f"Failed to post to Google Chat: {response.text}")

# Fetch unread emails from Primary tab
if __name__ == "__main__":
    if not EMAIL_USERNAME or not EMAIL_PASSWORD:
        print("Please set EMAIL_USERNAME and EMAIL_PASSWORD in your .env file.")
    else:
        unread_subjects = fetch_unread_emails_primary_tab(
            EMAIL_USERNAME, EMAIL_PASSWORD
        )
        # send_message_to_google_chat_space(unread_subjects[0])

        # Open a file in write mode
        with open("unread_emails.txt", "w") as file:
            i = 1
            for subject in unread_subjects:
                # Write to file
                file.write(str(i) + ": " + subject + "\n")
                i += 1

        # print("\nUnread email subjects have been saved to 'unread_emails.txt'")

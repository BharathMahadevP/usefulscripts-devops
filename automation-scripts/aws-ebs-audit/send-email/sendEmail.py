import smtplib
import os
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
from dotenv import load_dotenv
import configparser

load_dotenv()

# SMTP settings
SMTP_USERNAME = os.getenv("SMTP_ACCESS_KEY_ID")
SMTP_PASSWORD = os.getenv("SMTP_SECRET_ACCESS_KEY")
SMTP_SERVER = "email-smtp.us-east-1.amazonaws.com"
SMTP_PORT = 587  # Use 587 for TLS, or 465 for SSL

script_dir = os.path.dirname(os.path.abspath(__file__))
# Load config
config = configparser.ConfigParser()
config_path = os.path.join(script_dir, "config.conf")
config.read(config_path)

sender = config["Email_Details"]["sender_email"]
recipient = config["Email_Details"]["recipient_email"]
subject = config["Email_Details"]["subject"]


def sendMail(
    output_file,
    encryptedCOunt,
    unEncryptedCount,
    unattachedCount,
    attachedCount,
    totalCount,
    date,
    aws_account_id,
):
    if aws_account_id == "<Enter the account id of secondary aws account>":
        header = "Secondary AWS"
    elif aws_account_id == "<Enter the account id of primary aws account>":
        header = "Primary AWS"
    file_path = os.path.join(script_dir, output_file)
    # Email body (HTML)
    body_html = f"""
  <!DOCTYPE html>
  <html lang="en">
    <head>
      <meta charset="UTF-8" />
      <meta name="viewport" content="width=device-width, initial-scale=1.0" />
      <title>Email Body</title>
    </head>
    <body>
      <br />
      <table border="1" style="border-collapse: collapse; width: 60%">
        <thead>
          <th
            colspan="2"
            style="
              padding: 1.5%;
              border: 1px solid black;
              background-color: navy;
              color: white;
              width: 50%;
            "
          >
            {header}
          </th>
        </thead>
        <!-- <thead> -->
        <tr style="background-color: rgb(52, 52, 160); color: white">
          <th style="padding: 1%; border: 1px solid black">Category</th>
          <th style="padding: 1%; border: 1px solid black; text-align: center">
            Count
          </th>
        </tr>
        <!-- </thead> -->
        <tbody>
          <tr>
            <td style="padding: 1%; border: 1px solid black">
              Unattached Volumes
            </td>
            <td style="padding: 1%; border: 1px solid black; text-align: center">
              {unattachedCount}
            </td>
          </tr>
          <tr>
            <td style="padding: 1%; border: 1px solid black">
              Unencrypted Volumes
            </td>
            <td style="padding: 1%; border: 1px solid black; text-align: center">
              {unEncryptedCount}
            </td>
          </tr>
          <tr>
            <td style="padding: 1%; border: 1px solid black">
              Encrypted Volumes
            </td>
            <td style="padding: 1%; border: 1px solid black; text-align: center">
              {encryptedCOunt}
            </td>
          </tr>
          <tr>
            <td style="padding: 1%; border: 1px solid black">Total Volumes</td>
            <td style="padding: 1%; border: 1px solid black; text-align: center">
              {totalCount}
            </td>
          </tr>
        </tbody>
      </table>
    </body>
  </html>

  """

    # Create the email
    msg = MIMEMultipart()
    msg["Subject"] = subject + " | " + aws_account_id + " | " + date
    msg["From"] = sender
    msg["To"] = recipient

    msg.attach(MIMEText(body_html, "html"))

    # Add attachment
    with open(file_path, "rb") as file:
        part = MIMEApplication(file.read())
        part.add_header(
            "Content-Disposition",
            "attachment",
            filename=os.path.basename(file_path),
        )
        msg.attach(part)

    # Send the email via Amazon SES SMTP
    try:
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(SMTP_USERNAME, SMTP_PASSWORD)
            server.sendmail(sender, recipient, msg.as_string())
            print("Email sent successfully via SMTP!")

    except Exception as e:
        print("Failed to send email:", str(e))


if __name__ == "__main__":
    sendMail()
    print("Email sent successfully!")

import smtplib
import traceback


def send(content):
    try:
        smtp_server = "smtp.163.com"
        smtp_username = "itishsy@163.com"
        smtp_password = "KSEJTXDLZLXNBMMI"

        smtp = smtplib.SMTP(smtp_server, port=25)
        smtp.starttls()
        smtp.login(smtp_username, smtp_password)

        from_email = "itishsy@163.com"
        to_email = "huangshouyi@nfstone.com"
        subject = "Signal"
        body = content

        message = f"From: {from_email}\nTo: {to_email}\nSubject: {subject}\n\n{body}"

        smtp.sendmail(from_email, to_email, message)

        smtp.quit()
    except Exception as e:
        traceback.print_exc()
    return False


if __name__ == '__main__':
    send("hello")

import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

def send_forgot_password_email(request,token,email, type):
    subject='Your forgot Password link from StudyBuddy'
    domain=request.META['HTTP_HOST']
    mail_content=f'Hi,click on the link to change your password {domain}/{type}/{token}'
    msg = MIMEMultipart()
    msg["Subject"]=subject
    msg["From"]="sudskhokhar1@zohomail.in"
    msg["To"]=email
    msg.attach(MIMEText(mail_content, 'plain'))
    # server=smtplib.SMTP('smtp.gmail.com', 587)
    server=smtplib.SMTP("smtp.zoho.in", 587)
    server.starttls()
    server.login("sudskhokhar1@zohomail.in","c5UYRM2Wex01")
    text = msg.as_string()
    server.sendmail("sudskhokhar1@zohomail.in", email, text)
    server.quit()
    return True

def account_activation_email(request,token,uidb64, email):
    subject='Your email verification mail from StudyBuddy'
    domain=request.META['HTTP_HOST']
    mail_content=f'Welcome, please click on the link to verify your email {domain}/activate/{uidb64}/{token}/'
    msg = MIMEMultipart()
    msg["Subject"]=subject
    msg["From"]="sudskhokhar1@zohomail.in"
    msg["To"]=email
    msg.attach(MIMEText(mail_content, 'plain'))
    # server=smtplib.SMTP('smtp.gmail.com', 587)
    server=smtplib.SMTP("smtp.zoho.in", 587)
    server.starttls()
    server.login("sudskhokhar1@zohomail.in","c5UYRM2Wex01")
    text = msg.as_string()
    server.sendmail("sudskhokhar1@zohomail.in", email, text)
    server.quit()
    return True
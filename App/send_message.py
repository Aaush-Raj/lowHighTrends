#This file contains all Message sender of Telegram Bots and Email.
import requests
import smtplib
TOKEN = "5660485616:AAEJAVoxdZXXnDnWsipDf4btsFFeHmA1tuc"
grp_chat_id = -711731122      
def send_msg(msg):
    print(msg)
    grp_chat_url = f"https://api.telegram.org/bot{TOKEN}/sendMessage?chat_id={grp_chat_id}&text={msg}"
    # print(requests.get(grp_chat_url).json())


# send_msg("THIS IS A TEST MESSAGE, PLEASE IGNORE")

def send_email(user_gmail_id,client_code,username,msg):
    my_gmail_id = 'rajaayush8340@gmail.com'
    server = smtplib.SMTP('smtp.gmail.com',587)
    server.starttls()
    server.login(my_gmail_id,'itniothmjervqxge')
    subject = "Margin Shortfall in cliend id:",client_code,"user id:",username
    body = msg
    msg = f'Subject: {subject}\n\n{body}'

    server.sendmail(my_gmail_id,user_gmail_id,msg)
    print('mail sent')

# send_email('aayushcontactinfo@gmai.com',101,"AAUSH","TESTING SCHEDULER")
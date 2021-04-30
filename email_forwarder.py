#!/usr/bin/env python
# -*- coding: utf-8 -*-

import imaplib
import smtplib
import email
import re
import logging
import datetime

logging.basicConfig(format='%(levelname)-4s [%(asctime)s]  %(message)s', level=logging.INFO)


def forward_emails(
        username,
        password,
        imap_server,
        imap_port,
        smtp_server,
        smtp_port,
        common_address,
        staff_address
):
    """ Transparent e-mail forwarding from common_address to staff_address.
    You need enter username and password for common_address and specify imap- and smtp-servers.
    It works on mail servers with SSL support (like a Yandex.Mail and Gmail).

    """

    imap = imaplib.IMAP4_SSL(imap_server, imap_port)
    imap.login(username, password)
    imap.select('INBOX')
    status, response = imap.search('INBOX', '(UNSEEN)')
    unread_msg_nums = response[0].split()
    logging.info('Connected to IMAP server {0}. Count of new messages: {1}'.format(imap_server, len(unread_msg_nums)))
    status, response = imap.search(None, '(UNSEEN)')
    unread_msg_nums = response[0].split()
    for email_id in unread_msg_nums:
        resp = imap.fetch(email_id, '(RFC822)')
        response = resp[1][0][1]
        msg = email.message_from_string(response)
        sender = msg['from'].split()[-1]
        sender_address = re.sub(r'[<>]', '', sender)
        # Replace sender and recipient addresses.
        msg.replace_header("From", sender_address)
        msg.replace_header("To", staff_address)
        # Send modified message.
        smtp = smtplib.SMTP_SSL(smtp_server, smtp_port)
        smtp.login(username, password)
        smtp.sendmail(common_address, staff_address, msg.as_string())
        smtp.quit()
        logging.info('Message from {0} successfully forwarded to {1}'.format(sender_address, staff_address))
    # Mark all messages as unread.
    for email_id in unread_msg_nums:
        imap.store(email_id, '+FLAGS', '\Seen')
    logging.info('All messages are marked as unread.')


if __name__ == '__main__':
    # For example, we can transparent forward messages depending on the time and day of the week.
    current_week_day = datetime.date.today().weekday()
    current_hour = datetime.datetime.now().time().hour
    # All new messages from 19.00 Friday until 22.00 Sunday forwarded from contact@domain.tld to mary@domain.tld
    if current_week_day == 4:
        if current_hour in [19, 20, 21, 22, 23]:
            forward_emails(
                'contact@domain.tld',
                'secret',
                'imap.yandex.ru',
                993,
                'smtp.yandex.ru',
                465,
                'contact@domain.tld',
                'mary@domain.tld'
            )
    elif current_week_day == 5:
        forward_emails(
                'contact@domain.tld',
                'secret',
                'imap.yandex.ru',
                993,
                'smtp.yandex.ru',
                465,
                'contact@domain.tld',
                'mary@domain.tld'
            )
    elif current_week_day == 6:
        if current_hour in range(22):
            # test
            forward_emails(
                'contact@domain.tld',
                'secret',
                'imap.yandex.ru',
                993,
                'smtp.yandex.ru',
                465,
                'contact@domain.tld',
                'mary@domain.tld'
            )

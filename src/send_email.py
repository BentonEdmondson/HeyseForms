import sys
sys.path.append('/Users/kfliu/src/HeyseForms/src')
from sheets_api import sheets
from redmail import gmail


def setup():
    gmail.username = 'heyseform@gmail.com' # Your Gmail address
    gmail.password = '' #Application Password

    gmail.set_template_paths(
        html="templates",
        text="",
    )

def supervisor_reminder():
    email_list = sheets.get_supervisor_email_list()
    for email in email_list:
        one_list = [email]
        gmail.send(
            subject="Intern Reflection Review Reminder",
            receivers=one_list,
            html_template='supervisor_email.html'
        )

if __name__ == '__main__':
    setup()
    supervisor_reminder()

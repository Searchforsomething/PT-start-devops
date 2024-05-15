import logging
import re
import paramiko
import os
import psycopg2

from dotenv import load_dotenv
from telegram import Update, ForceReply
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, ConversationHandler



host = os.getenv('RM_HOST')
port = os.getenv('RM_PORT')
username = os.getenv('RM_USER')
password = os.getenv('RM_PASSWORD')
TOKEN = os.getenv('TOKEN')

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect(hostname=host, username=username, password=password, port=port)

phoneNumberList = []
emailList = []

connection = psycopg2.connect(user=os.getenv('DB_USER'),
                                  password=os.getenv('DB_PASSWORD'),
                                  host=os.getenv('DB_HOST'),
                                  port=os.getenv('DB_PORT'),
                                  database=os.getenv('DB_DATABASE'))

# Подключаем логирование
logging.basicConfig(
    filename='logfile.txt', format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)

logger = logging.getLogger(__name__)


def start(update: Update, context):
    user = update.effective_user
    update.message.reply_text(f'Привет {user.full_name}!')


def echo(update: Update, context):
    update.message.reply_text(update.message.text)


def main():

    # Создайте программу обновлений и передайте ей токен вашего бота
    updater = Updater(TOKEN, use_context=True)

    # Получаем диспетчер для регистрации обработчиков
    dp = updater.dispatcher

    # Регистрируем обработчики команд
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("help", helpCommand))
    dp.add_handler(CommandHandler("get_release", getRelease))
    dp.add_handler(CommandHandler("get_uname", getUname))
    dp.add_handler(CommandHandler("get_uptime", getUptime))
    dp.add_handler(CommandHandler("get_df", getDf))
    dp.add_handler(CommandHandler("get_free", getFree))
    dp.add_handler(CommandHandler("get_w", getW))
    dp.add_handler(CommandHandler("get_auths", getAuth))
    dp.add_handler(CommandHandler("get_critical", getCritical))
    dp.add_handler(CommandHandler("get_ps", getPs))
    dp.add_handler(CommandHandler("get_mpstat", getMpstat))
    dp.add_handler(CommandHandler("get_ss", getSs))
    dp.add_handler(CommandHandler("get_apt_list", getAptList))
    dp.add_handler(CommandHandler("get_services", getServices))
    dp.add_handler(CommandHandler("get_repl_logs", getReplLogs))
    dp.add_handler(CommandHandler("get_emails", getEmails))
    dp.add_handler(CommandHandler("get_phone_numbers", getPhoneNumbers))
    dp.add_handler(convHandlerFindPhoneNumbers)
    dp.add_handler(convHandlerFindEmails)
    dp.add_handler(convHandlerVerifyPassword)


    # Регистрируем обработчик текстовых сообщений
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, echo))

    # Запускаем бота
    updater.start_polling()

    # Останавливаем бота при нажатии Ctrl+C
    updater.idle()


def findPhoneNumbersCommand(update: Update, context):
    update.message.reply_text('Введите текст для поиска телефонных номеров: ')

    return 'findPhoneNumbers'


def findEmailsCommand(update: Update, context):
    update.message.reply_text('Введите текст для поиска email адресов: ')

    return 'findEmails'


def verifyPasswordCommand(update: Update, context):
    update.message.reply_text('Введите пароль: ')

    return 'verifyPassword'


def helpCommand(update: Update, context):
    update.message.reply_text('/find_email - найти Email\n' + \
            '/find_phone_number - найти номер телефона\n' + \
            '/verify_password - проверка сложности пароля\n' + \
            'Сбор информации о системе:\n' + \
            '/get_release - релиз\n/get_uname - архитектура процессора, имя хоста системы и версия ядра\n' + \
            '/get_uptime - время работы\n' + \
            '/get_df - Сбор информации о состоянии файловой системы\n' + \
            '/get_free - Сбор информации о состоянии оперативной памяти\n' + \
            '/get_mpstat - Сбор информации о производительности системы\n' + \
            '/get_w - Сбор информации о работающих в данной системе пользователях\n' + \
            'Сбор логов\n' + \
            '/get_auths - Последние 10 входов в систему\n' + \
            '/get_critical - Последние 5 критических событий\n' + \
            '/get_critical - Сбор информации о запущенных процессах\n' + \
            '/get_ss - Сбор информации об используемых портах\n' + \
            '/get_apt_list - Сбор информации об установленных пакетах\n' + \
            "/get_apt_list [имя пакета] - Сбор информации об указанном пакете\n" + \
            '/get_services - Сбор информации о запущенных сервисах' + \
            'База данных\n' + \
            '/get_repl_logs - данные репликации и логи\n' + \
            '/get_emails - показать список email из БД\n' + \
            '/get_phone_numbers - показать список номеров телефонов из БД\n')


def findPhoneNumbers(update: Update, context):
    global phoneNumberList
    user_input = update.message.text  # Получаем текст, содержащий(или нет) номера телефонов

    phoneNumRegex = re.compile(r'(?:\+7|8)[\s\-]?\(?\d{3}\)?[\s\-]?\d{3}[\s\-]?\d{2}[\s\-]?\d{2} ?')

    phoneNumberList = phoneNumRegex.findall(user_input)  # Ищем номера телефонов

    if not phoneNumberList:  # Обрабатываем случай, когда номеров телефонов нет
        update.message.reply_text('Телефонные номера не найдены')
        return ConversationHandler.END  # Завершаем выполнение функции

    phoneNumbers = ''  # Создаем строку, в которую будем записывать номера телефонов
    for i in range(len(phoneNumberList)):
        phoneNumbers += f'{i + 1}. {phoneNumberList[i]}\n'  # Записываем очередной номер
    phoneNumbers += "Хотите добавить эти номера в базу данных? (Y/N)"
    update.message.reply_text(phoneNumbers)  # Отправляем сообщение пользователю

    return 'addNumberToDb'


def findEmails(update: Update, context):
    global emailList
    user_input = update.message.text  # Получаем текст

    emailRegex = re.compile(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}')

    emailList = emailRegex.findall(user_input)  # Ищем email адреса

    if not emailList:  # Обрабатываем случай, когда email адресов нет
        update.message.reply_text('email адреса не найдены')
        return ConversationHandler.END # Завершаем выполнение функции

    emails = ''  # Создаем строку, в которую будем записывать адреса
    for i in range(len(emailList)):
        emails += f'{i + 1}. {emailList[i]}\n'  # Записываем очередной адрес
    emails += "Хотите добавить эти email адреса в базу данных? (Y/N)"
    update.message.reply_text(emails)  # Отправляем сообщение пользователю
    return 'addEmailToDb'


def verifyPassword(update: Update, context):
    user_input = update.message.text  # Получаем текст

    passwordRegex = re.compile(r'(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[!@#$%^&*()]).{8,}')

    if not passwordRegex.match(user_input):  # пароль лёгкий
        update.message.reply_text('Пароль простой')
        return ConversationHandler.END # Завершаем выполнение функции

    update.message.reply_text('Пароль сложный')  # Отправляем сообщение пользователю
    return ConversationHandler.END  # Завершаем работу обработчика диалога


def getRelease(update: Update, context):
    stdin, stdout, stderr = client.exec_command('lsb_release -a')
    release_info = stdout.read().decode('utf-8')

    update.message.reply_text(release_info)
    return ConversationHandler.END  # Завершаем работу обработчика диалога


def getUname(update: Update, context):
    stdin, stdout, stderr = client.exec_command('uname -a')
    release_info = stdout.read().decode('utf-8')

    update.message.reply_text(release_info)
    return ConversationHandler.END


def getUptime(update: Update, context):
    stdin, stdout, stderr = client.exec_command('uptime')
    release_info = stdout.read().decode('utf-8')

    update.message.reply_text(release_info)
    return ConversationHandler.END


def getDf(update: Update, context):
    stdin, stdout, stderr = client.exec_command('df')
    release_info = stdout.read().decode('utf-8')

    update.message.reply_text(release_info)
    return ConversationHandler.END


def getFree(update: Update, context):
    stdin, stdout, stderr = client.exec_command('free')
    release_info = stdout.read().decode('utf-8')

    update.message.reply_text(release_info)
    return ConversationHandler.END


def getW(update: Update, context):
    stdin, stdout, stderr = client.exec_command('who')
    release_info = stdout.read().decode('utf-8')

    update.message.reply_text(release_info)
    return ConversationHandler.END


def getAuth(update: Update, context):
    stdin, stdout, stderr = client.exec_command('last -10')
    release_info = stdout.read().decode('utf-8')

    update.message.reply_text(release_info)
    return ConversationHandler.END


def getCritical(update: Update, context):
    stdin, stdout, stderr = client.exec_command('journalctl -n 5 -p crit')
    release_info = stdout.read().decode('utf-8')

    update.message.reply_text(release_info)
    return ConversationHandler.END  # Завершаем работу обработчика диалога


def getPs(update: Update, context):
    stdin, stdout, stderr = client.exec_command('ps aux')

    chunk_size = 4096
    while True:
        chunk = stdout.channel.recv(chunk_size).decode('utf-8')
        if not chunk:
            break
        update.message.reply_text(chunk)

    return ConversationHandler.END  # Завершаем работу обработчика диалога


def getMpstat(update: Update, context):
    stdin, stdout, stderr = client.exec_command('mpstat')
    release_info = stdout.read().decode('utf-8')

    update.message.reply_text(release_info)
    return ConversationHandler.END  # Завершаем работу обработчика диалога


def getSs(update: Update, context):
    stdin, stdout, stderr = client.exec_command('ss -tuln')
    release_info = stdout.read().decode('utf-8')

    update.message.reply_text(release_info)
    return ConversationHandler.END  # Завершаем работу обработчика диалога


def getPhoneNumbers(update: Update, context):
    global connection
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM phoneNumber;")
    data = cursor.fetchall()
    message = ''
    for row in data:
        message += f'{row[0]}. {row[1]}\n'
    update.message.reply_text(message)
    return ConversationHandler.END  # Завершаем работу обработчика диалога


def getEmails(update: Update, context):
    global connection
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM emails;")
    data = cursor.fetchall()
    message = ''
    for row in data:
        message += f'{row[0]}. {row[1]}\n'
    update.message.reply_text(message)
    return ConversationHandler.END  # Завершаем работу обработчика диалога


def getAptList(update: Update, context):
    text = update.message.text
    text = text.replace('/get_apt_list ', '')
    if text != '':
        command = f'dpkg -l | grep {text}'
        stdin, stdout, stderr = client.exec_command(command)
    else:
        stdin, stdout, stderr = client.exec_command('dpkg -l')

    chunk_size = 4096
    while True:
        chunk = stdout.channel.recv(chunk_size).decode('utf-8')
        if not chunk:
            break
        update.message.reply_text(chunk)

    return ConversationHandler.END  # Завершаем работу обработчика диалога


def getServices(update: Update, context):
    stdin, stdout, stderr = client.exec_command('systemctl list-units --type=service')
    chunk_size = 4096
    while True:
        chunk = stdout.channel.recv(chunk_size).decode('utf-8')
        if not chunk:
            break
        update.message.reply_text(chunk)
    return ConversationHandler.END  # Завершаем работу обработчика диалога


def getReplLogs(update: Update, context):
  
    #for docker
    #stdin, stdout, stderr = client.exec_command('docker logs -n 30 db_image')
  
    #for ansible
    stdin, stdout, stderr = client.exec_command("cat /var/log/postgresql/postgresql-14-main.log")
  
    chunk_size = 4096
    while True:
        #for ansible
        chunk = stdout.read(chunk_size).decode('utf-8')
      
        #for docker
        #chunk = stderr.read(chunk_size).decode('utf-8')
      
        if not chunk:
            break
        update.message.reply_text(chunk)
    return ConversationHandler.END  # Завершаем работу обработчика диалога


def addEmailToDb(update: Update, context):
    global emailList
    user_input = update.message.text
    global connection
    cursor = connection.cursor()
    if user_input == 'Y':
        for email in emailList:
            cursor.execute(f"INSERT INTO emails (email) VALUES ('{email}');")
        update.message.reply_text("Данные добавлены в базу данных!")
    elif user_input == 'N':
        update.message.reply_text("Хорошо, удачного дня!")
    else:
        update.message.reply_text("Непохоже ни на Y, ни на N")
    return ConversationHandler.END


def addNumberToDb(update: Update, context):
    global phoneNumberList
    user_input = update.message.text
    global connection
    cursor = connection.cursor()
    if user_input == 'Y':
        for number in phoneNumberList:
            cursor.execute(f"INSERT INTO phoneNumber (phoneNumber) VALUES ('{number}');")
        update.message.reply_text("Данные добавлены в базу данных!")
    elif user_input == 'N':
        update.message.reply_text("Хорошо, удачного дня!")
    else:
        update.message.reply_text("Непохоже ни на Y, ни на N")
    return ConversationHandler.END


convHandlerFindPhoneNumbers = ConversationHandler(
        entry_points=[CommandHandler('find_phone_number', findPhoneNumbersCommand)],
        states={
            'findPhoneNumbers': [MessageHandler(Filters.text & ~Filters.command, findPhoneNumbers)],
            'addNumberToDb': [MessageHandler(Filters.text & ~Filters.command, addNumberToDb)]
        },
        fallbacks=[]
    )


convHandlerFindEmails = ConversationHandler(
        entry_points=[CommandHandler('find_email', findEmailsCommand)],
        states={
            'findEmails': [MessageHandler(Filters.text & ~Filters.command, findEmails)],
            'addEmailToDb': [MessageHandler(Filters.text & ~Filters.command, addEmailToDb)]
        },
        fallbacks=[]
    )


convHandlerVerifyPassword = ConversationHandler(
        entry_points=[CommandHandler('verify_password', verifyPasswordCommand)],
        states={
            'verifyPassword': [MessageHandler(Filters.text & ~Filters.command, verifyPassword)],
        },
        fallbacks=[]
    )



if __name__ == '__main__':
    main()

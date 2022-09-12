import os
from datetime import datetime

from library_ssh import open_ssh_client, sent_autorize_ssh_command, sent_ssh_command, sftp_put

user = 'tech'
password = 'tech123'
port = 22

files = os.listdir('files')  # получение списка файлов в каталоге files для отправки на хост по sftp

with open('hosts.txt', 'r') as hosts:  # получение списка хостов из файла hosts.txt
    for host in hosts.readlines():  # цикл по списку хостов в файле hosts.txt
        host = host.rstrip()

        # создание файла с ответами хоста
        f_out = open('logs/' + host, 'a')
        f_out.write(3 * '\n' + str(datetime.today()) + '\n')

        response = os.system("ping -c 1 " + host)  # проверка доступности хоста

        if response == 0:  # если хост доступен, открываем подключение к клиенту
            client = open_ssh_client(host, user, password, port)  # подключение к хосту по ssh

            print(host + ' ' + str(datetime.today()))

            # отправка всех файлов по sftp из каталога files
            # будут загружены в каталог sftp_files домашнюю директорию пользователя
            sent_ssh_command('mkdir sftp_files', client, f_out)  # отправка команды на хост
            for file in files:
                file = file.rstrip()
                sftp_put(client, src='files/' + file, dst='sftp_files/' + file)

            with open('commands.txt', 'r') as commands:  # получение списка команд из файла commands.txt
                for command in commands.readlines():  # выполнение списка команд на хосте
                    command = command.rstrip()  # удаление служебных символов из команды перед отправкой
                    if command[:4] == 'sudo' or command[:2] == 'su':
                        sent_autorize_ssh_command(command, password,
                                                  client, f_out)  # отправка команды требующей авторизации на хост
                    else:
                        sent_ssh_command(command, client, f_out)  # отправка команды на хост
            client.close()

        else:  # если хост не доступен, пишем в лог запись
            f_out.write('host is down\n')

        f_out.write('\n' + str(datetime.today()) + '\n')
        f_out.close()

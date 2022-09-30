import os
from datetime import datetime

from library_ssh import *

user = open('user.txt', 'r').readline()  # логин для подключения берется из файла user.txt
password = open('password.txt', 'r').readline()  # пароль (в явном виде) для подключения берется из файла password.txt
# удаление пароля из файла
with open('password.txt', 'w') as f:
    f.write('')
# проверка на считывание пустого файла с паролем
if not password:
    sys.exit('Не введен пароль подключения!\nВведите пароль от УЗ в файл password.txt.')

port = 22  # ssh-порт

files = os.listdir('files')  # получение списка файлов в каталоге files для отправки на хост по sftp

with open('hosts.txt', 'r') as hosts:  # получение списка хостов из файла hosts.txt
    for host in hosts.readlines():  # цикл по списку хостов в файле hosts.txt
        host = host.rstrip()

        # создание файла с ответами хоста
        f_out = open('log/' + host + '.txt', 'a')
        f_out.write(3 * '\n' + 'start ' + str(datetime.today()) + '\n')

        response = os.system("ping -n 1 -4 " + host + ' > nul')  # проверка доступности хоста

        if response == 0:  # если хост доступен, открываем подключение к клиенту
            print(host + ' ' + str(datetime.today()))

            client = open_ssh_client(host, user, password, port)  # подключение к хосту по ssh

            # загрузка файлов из папки files по sftp на хост в папку ~/sftp_files/
            sent_files(client, files, f_out, password)

            # запуск команд из файла commands.txt на хосте
            run_command_list(client, password, f_out)

            # удаление загруженных файлов на хосте
            sent_ssh_command('rm -rf sftp_files', client, f_out)
            client.close()

        else:  # если хост не доступен, пишем в лог запись
            f_out.write('host is down\n')

        f_out.write('\n' + 'end ' + str(datetime.today()) + '\n')
        f_out.close()

# end

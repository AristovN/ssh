import sys

import paramiko


def sent_ssh_command(command, client, f_out):  # отправка команды на хост
    stdin, stdout, stderr = client.exec_command(command)
    # вывод ответа от хоста
    print_result_command(command, stdout, f_out)

    return


def print_result_command(command, stdout, f_out):  # печать результата команды
    # print(command + ' >\t' + "".join((stdout.readlines())))
    f_out.write(command + ' >\t' + "".join((stdout.readlines())))


def sent_autorize_ssh_command(command, password, client,
                              f_out):  # отправка команды с необходимой авторизации (sudo)
    # открытие сессии для отправки потока
    session = client.get_transport().open_session()
    session.set_combine_stderr(True)
    session.get_pty()
    # отправка команды на хост
    session.exec_command(command)
    # запись пароля и отправка
    stdin = session.makefile('wb', -1)
    stdin.write(password + '\n')
    stdin.flush()
    # получение и редактирование ответа от хоста
    #stdout = str(session.makefile('rb', -1).read().decode("utf-8"))
    stdout = str(session.makefile('rb', -1).read().decode('cp1251', 'replace'))
    stdout = stdout[stdout.find(':') + 3:]
    # print(command + ' >\t' + str(stdout))
    f_out.write(command + ' >\t' + str(stdout))

    return


def open_ssh_client(host, user, password, port):  # открытие ssh
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(hostname=host, username=user, password=password, port=port)
    # использование потока команд
    client.invoke_shell()

    return client


def sftp_put(client, src,
             dst):  # отправка 1 файла по sftp. множественная отправка и отправка каталогов не поддерживается sftp
    sftp = client.open_sftp()
    sftp.put(src, dst)  # отправка файла
    sftp.close()

    return

def run_command_list(client, password, f_out):
    with open('commands.txt', 'r') as commands:  # получение списка команд из файла commands.txt
        for command in commands.readlines():  # выполнение списка команд на хосте
            command = command.rstrip()  # удаление служебных символов из команды перед отправкой

            if command[:4] == 'sudo':
                sent_autorize_ssh_command(command, password, client,
                                          f_out)  # отправка команды требующей авторизации на хост
            elif command[:2] == 'su':
                sys.exit("Использование команды su запрещено! Нужно изменить отправляемый скрипт. \nРабота программы прервана.")
            else:
                sent_ssh_command(command, client, f_out)  # отправка команды на хост

def sent_files(client, files, f_out, password):
    # отправка всех файлов по sftp из каталога files
    # будут загружены в каталог sftp_files домашнюю директорию пользователя
    sent_ssh_command('mkdir sftp_files', client, f_out)  # отправка команды на хост
    for file in files:
        file = file.rstrip()
        sftp_put(client, src='files/' + file, dst='sftp_files/' + file)
    sent_autorize_ssh_command('sudo chmod +x sftp_files/*', password, client, f_out)

import subprocess
import time

scripts = ['vonovia.py', 'altona.py', 'fluwog.py', 'mein_scraper.py', 'mein_sender.py']
processes = []
stop_count = 0

# Запуск всех скриптов
for script in scripts:
    process = subprocess.Popen(['python', script])
    processes.append(process)
    print(f'Started script: {script}')

# Проверка состояния скриптов каждые 25 секунд
while True:
    for process in processes:
        if process.poll() is not None:
            # Скрипт завершился, перезапускаем его
            print(f'Script {process.args} stopped. Restarting...')
            new_process = subprocess.Popen(['python', process.args[1]])
            processes.remove(process)
            processes.append(new_process)
            stop_count += 1

    if stop_count == 0:
        print('All scripts running fine')

    stop_count = 0  # Сброс счетчика остановленных скриптов
    time.sleep(25)

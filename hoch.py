import subprocess
import time

scripts = ['altona.py', 'fluwog.py', 'mein_scraper.py', 'mein_sender.py']
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
            # Скрипт завершился, завершаем все остальные процессы
            for p in processes:
                p.terminate()
            stop_count += 1
            print(f'Script {process.args} stopped')

    if stop_count == 0:
        print('All scripts running fine')

    time.sleep(25)

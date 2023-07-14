import subprocess
import time

scripts = ['altona.py', 'fluwog.py', 'mein_scraper.py', 'mein_sender.py']
processes = []

# Запуск всех скриптов
for script in scripts:
    process = subprocess.Popen(['python', script])
    processes.append(process)

# Проверка состояния скриптов каждые 25 секунд
while True:
    for process in processes:
        if process.poll() is not None:
            # Скрипт завершился, завершаем все остальные процессы
            for p in processes:
                p.terminate()
            break
    time.sleep(25)

import asyncio
import subprocess
import iterm2
import os
import time

# Конфиг
SSH_PORT = "your_port"
SSH_HOST = "your_host"
SSH_USER = "your_user"

# Проверка, идет ли уже туннель на нужный порт
def is_ssh_running():
    try:
        output = subprocess.check_output(
            ["lsof", "-i", f":{SSH_PORT}"],
            stderr=subprocess.DEVNULL
        )
        return b"ssh" in output
    except subprocess.CalledProcessError:
        return False

# Проверка доступности хоста через ping
def is_host_reachable():
    try:
        subprocess.check_output(["ping", "-c", "1", SSH_HOST], stderr=subprocess.DEVNULL)
        return True
    except subprocess.CalledProcessError:
        return False

# Уведомление через osascript
def notify(title, message):
    subprocess.run([
        "osascript", "-e",
        f'display notification "{message}" with title "{title}"'
    ])

# Запуск SSH туннеля
def start_ssh_tunnel():
    try:
        subprocess.Popen(
            ["ssh", "-D", SSH_PORT, "-N", "-f", f"{SSH_USER}@{SSH_HOST}"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        notify("SSH Tunnel", f"Туннель установлен на порт {SSH_PORT}")
    except Exception as e:
        notify("SSH Tunnel Error", f"Не удалось установить туннель: {str(e)}")

# Основной запуск
async def main(connection):
    if is_ssh_running():
        notify("SSH Tunnel", f"Уже запущен на порту {SSH_PORT}")
        return

    if not is_host_reachable():
        notify("SSH Tunnel", f"Хост {SSH_HOST} недоступен по сети")
        return

    notify("SSH Tunnel", f"Устанавливаю соединение с {SSH_HOST}...")
    start_ssh_tunnel()

    # Проверка через 10 секунд — поднялся ли туннель
    await asyncio.sleep(10)
    if is_ssh_running():
        notify("SSH Tunnel", f"Успешно подключено к {SSH_HOST}:{SSH_PORT}")
    else:
        notify("SSH Tunnel", f"Подключение не удалось")

# Запуск iTerm2 скрипта
iterm2.run_until_complete(main)
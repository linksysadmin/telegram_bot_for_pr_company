#bin/bash

if ! command -v python3 &> /dev/null
then
    echo "Python не установлен. Установите Python и запустите скрипт снова."
    exit 1
fi

if [ -d ".venv" ]
then
    echo ""

else
    echo "Установка виртуального окружения"
    python3 -m venv .venv
    source .venv/bin/activate
    pip install -r requirements.txt
    deactivate

    echo "Создание и импорт базы данных"
    echo "Введите пароль от mysql root пользователя: "
    mysql -u root -p -e "CREATE DATABASE mr_h_db"
    echo "Введите пароль от mysql root пользователя: "
    mysql -u root -p mr_h_db < create_db.sql
    echo "Импорт базы данных завершен"
fi

echo "Запуск QR Bot"
python3 main.py
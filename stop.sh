#!/bin/bash
pids=$(pgrep -f "python -u calendar-bot.py")
if [ -z "$pids" ]; then
    echo "Нет запущенных calendar-bot"
else
    kill "$pids"
    echo "Готово"
fi
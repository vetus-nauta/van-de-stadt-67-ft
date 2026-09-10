# FreeCAD: установка и проверка, 2026-09-10

Установлен официальный стабильный FreeCAD 1.1.3 для Linux x86_64, Python 3.11, AppImage. Проверен настоящий GUI на DISPLAY=:0; системные пакеты, sudo, ассоциации по умолчанию и исходные чертежи не изменялись.

## Источник и целостность

- Release: https://github.com/FreeCAD/FreeCAD/releases/tag/1.1.3
- API latest на момент проверки: tag_name=1.1.3, prerelease=false.
- AppImage: https://github.com/FreeCAD/FreeCAD/releases/download/1.1.3/FreeCAD_1.1.3-Linux-x86_64-py311.AppImage
- Контрольная сумма: https://github.com/FreeCAD/FreeCAD/releases/download/1.1.3/FreeCAD_1.1.3-Linux-x86_64-py311.AppImage-SHA256.txt
- Размер: 820795896 байт.
- SHA256: `3a853eb69ee595f779f2255dbf80a765926981d8ff68903cefee4dfb03a8f5ef`. Фактически рассчитан по загрузке; совпал с опубликованным SHA256.txt и digest GitHub API.

## Установка и запуск

- Программа: `/home/alexey/Applications/FreeCAD/FreeCAD_1.1.3-Linux-x86_64-py311.AppImage`.
- Команда: `/home/alexey/.local/bin/freecad`.
- Меню Linux: **FreeCAD**, launcher `/home/alexey/.local/share/applications/org.freecad.FreeCAD.desktop`.
- Иконка скопирована из самого проверенного AppImage в каталог установки.
- desktop-file-validate завершился 0; update-desktop-database завершился 0. Defaults не назначались.
- Версия внутри приложения: `1.1.3R20260725 (Git shallow)`, commit `145529fe741292ff0b3977a01195bf0247425794`.
- Бинарь и скачанные пакеты находятся вне Git; сохраняются описание и результаты проверки.

## Выполненная проверка

Запущен GUI через `freecad /home/alexey/Groot/van-de-stadt-67-ft/.local/tooling/freecad-smoke.FCMacro`.

Макрос создал твердотельную деталь 100×60×10 мм со сквозным отверстием Ø8 мм, выполнил булево вычитание, сохранил FCStd и STEP, закрыл документ и повторно прочитал каждый формат. Оба результата имеют valid shape, ровно одно solid, объём 59497.34517542564 мм³. Аналитический ожидаемый объём 59497.34517542563 мм³, допуск теста 1e-6 мм³. Результат PASS. GUI сохранил PNG, визуально проверено наличие детали и отверстия. Эти проверки подтверждают работоспособность установки и базового геометрического ядра, сохранения/чтения FCStd и STEP; они не подтверждают точный импорт Rhino `.3dm` или проектирование корпуса.

Подробности: `result.json`, `freecad-smoke.FCMacro`, `freecad-smoke.log`, `test-bracket.png`. Рабочие FCStd/STEP теста: `.local/tooling/freecad-smoke/`.

## Применение в проекте

FreeCAD пригоден как визуальный параметрический CAD для создаваемых деталей, компоновочных объёмов, сечений и обмена STEP. Исходный Rhino `.3dm` следует сохранять как эталон; точный переход его NURBS/BRep в рабочую модель требует отдельной проверки. Установка приложения сама по себе не решает этот переход.

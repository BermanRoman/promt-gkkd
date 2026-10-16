# Установка ГККД — инструкция для Claude Code

Этот файл читает Claude Code (вкладка Code в приложении Claude или терминал), а не человек. Человек вставил в чат одну строку из README и ждёт, что ты всё сделаешь сам. Говори с ним простыми словами, на «ты», без технических подробностей, если он не спросил. Одно сообщение — одно действие с его стороны.

## Что должно получиться

Рабочая папка, в которой запущен Claude Code (дальше — «рабочая папка»):

    рабочая папка/
    ├── CLAUDE.md        ← памятка для следующих сессий (шаг 4)
    ├── promt-gkkd/      ← система: агенты, методички, библиотека
    ├── repos/           ← методички Романа Бермана, их читают агенты
    └── projects/        ← проекты экспертов, создаёт Фиксик

## Шаг 0. Проверь рабочую папку

- Посмотри, где запущен Claude Code.
- Если это домашняя папка пользователя, рабочий стол или папка с чужими файлами — не ставь туда. Скажи человеку: «Давай поставим систему в отдельную папку. Создай пустую папку, например „ГККД“ в „Документах“, начни новую сессию во вкладке Code, нажми Select folder, выбери эту папку и снова отправь ту же строку». Дальше не продолжай.
- Если в рабочей папке уже есть `promt-gkkd/` — система стоит. Переходи к шагу 5 «Обновление», если человек просил обновить, иначе сразу к шагу 6.

## Шаг 1. Git

- Проверь `git --version`.
- Нет git:
  - macOS — запусти `xcode-select --install` и скажи человеку: «Появится окно установки инструментов разработчика — нажми „Установить“ и напиши мне, когда закончится».
  - Windows — `winget install --id Git.Git -e`; после установки попроси человека полностью закрыть и снова открыть приложение Claude, начать сессию во вкладке Code в той же папке и снова отправить строку.
  - Linux — `sudo apt install git` или пакетный менеджер дистрибутива; пароль вводит человек.

## Шаг 2. Скачай систему и методички

Если `promt-gkkd/` ещё нет:

    git clone https://github.com/BermanRoman/promt-gkkd.git

Методички — в папку `repos/` рядом:

    mkdir repos
    git clone https://github.com/BermanRoman/prompt-audience-research.git repos/prompt-audience-research
    git clone https://github.com/BermanRoman/prompt-spin-questions.git repos/prompt-spin-questions
    git clone https://github.com/BermanRoman/promt-source-life.git repos/promt-source-life
    git clone https://github.com/BermanRoman/promt-hvco.git repos/promt-hvco
    git clone https://github.com/BermanRoman/prompt-clip-landing.git repos/prompt-clip-landing
    git clone https://github.com/BermanRoman/promt-copywriting.git repos/promt-copywriting

Уже скачанное не качай заново. Ошибка сети — повтори один раз, потом скажи человеку, что GitHub недоступен, и предложи проверить интернет или VPN.

## Шаг 3. Проверь, что всё на месте

Агенты читают эти файлы. Каждый должен существовать:

- `repos/prompt-audience-research/audience-research.md`
- `repos/prompt-spin-questions/spin-questions.md`
- `repos/promt-source-life/spin-core.md`
- `repos/promt-source-life/behavior-methodology.md`
- `repos/promt-hvco/hvco.md`
- `repos/prompt-clip-landing/clip-landing.md`
- `repos/promt-copywriting/prompt-copywriter.md`
- `repos/promt-copywriting/methodology-copywriting.md`
- `repos/promt-copywriting/methodology-listening.md`
- `promt-gkkd/agents/00-fiksik.md`

Чего-то нет — назови файл человеку и не запускай Фиксика.

## Шаг 4. Памятка для следующих сессий

Создай в рабочей папке `CLAUDE.md` (если его нет) с таким текстом:

    # Система ГККД

    В этой папке установлена система агентов «Горячие клиенты каждый день» (ГККД) Романа Евгеньевича Бермана.

    - Корень системы — `promt-gkkd/`. Все пути вида `agents/…`, `knowledge/…`, `library/…`, `core/…` в файлах системы — от этой папки.
    - Методички Романа — `repos/` (в файлах системы — `<корень>/../repos/`).
    - Проекты экспертов — `projects/` в этой папке.
    - Человек пишет «начинаем», «продолжаем» или что-то про воронку, продукт, бота — работай по `promt-gkkd/agents/00-fiksik.md`: найди проект в `projects/` и продолжи с места остановки.
    - «Обнови систему» — выполни раздел «Обновление» из `promt-gkkd/INSTALL.md`.

## Шаг 5. Обновление (по просьбе человека)

    git -C promt-gkkd pull
    git -C repos/prompt-audience-research pull
    git -C repos/prompt-spin-questions pull
    git -C repos/promt-source-life pull
    git -C repos/promt-hvco pull
    git -C repos/prompt-clip-landing pull
    git -C repos/promt-copywriting pull

Проекты в `projects/` не трогай. Скажи человеку одной строкой, обновилось что-то или нет.

## Шаг 6. Wordstat — по желанию

Спроси один раз: «Хочешь, чтобы я сам смотрел спрос в Яндекс Wordstat? Нужен аккаунт Яндекса, банковская карта для Яндекс Облака и около часа. Можно и без этого — тогда попрошу скриншоты». 

- «Да» — веди человека по `promt-gkkd/knowledge/wordstat-setup.md`, вариант «Если работаешь в Claude Code» (он подходит и для вкладки Code в приложении). Команды выполняй сам; шаги в браузере Яндекса делает человек, ты подсказываешь по одному. Секреты (токен, ключ) человек в чат не присылает — следуй разделу о секретах в инструкции.
- «Нет» или «потом» — идём дальше.

## Шаг 7. Запуск

1. Скажи человеку коротко: система стоит, где лежит, что дальше начнёт Фиксик. Подскажи один раз: «Если я спрашиваю разрешение на каждый файл — выбери режим Accept edits рядом с кнопкой отправки (в терминале — Shift+Tab)».
2. Прочитай `promt-gkkd/agents/00-fiksik.md` и работай по нему. Полный путь к папке методичек для заданий агентам — абсолютный путь к `repos/` в рабочей папке.

## Чего не делать

- Не меняй файлы в `promt-gkkd/` и `repos/` — это система; правки пропадут при обновлении.
- Не ставь ничего глобально, кроме git и того, что требует инструкция Wordstat.
- Не проси человека открывать файлы и копировать пути — всё делаешь сам.

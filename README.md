# Горячие клиенты каждый день

Мастер-промт превращает Claude в команду из десяти агентов, которая собирает воронку продаж для эксперта, который ничего не понимает в маркетинге.

На входе эксперт рассказывает, чем занимается и как сейчас продаёт.

На выходе он получает папку с готовыми материалами: пересобранный продукт, тексты всех этапов, ТЗ страниц и витрины, бот-продавец и схема его сборки в любом сервисе, шаблоны юридических документов.

Агенты работают по методологии «Горячие клиенты каждый день» _(ГККД)_ Романа Евгеньевича Бермана.

## Для кого создан этот мастер-промт?

Для экспертов, предпринимателей, фрилансеров и прочих бедолаг, которые продают свои знания и работу и хотят воронку под себя, а не модную схему, в которой они сломаются.

## Как пользоваться?

Система работает в Claude Code — это Claude в терминале, который сам читает и создаёт файлы в папке на твоём компьютере.

Нужна платная подписка Claude: Pro, Max или выше.

В бесплатный тариф Claude Code не входит.

### 1. Установи Claude Code

Открой терминал: на Mac — программа «Терминал», на Windows — PowerShell.

Вставь команду для своей системы и нажми Enter.

Mac и Linux:

    curl -fsSL https://claude.ai/install.sh | bash

Windows (PowerShell):

    irm https://claude.ai/install.ps1 | iex

На Windows ещё поставь **[Git для Windows](https://git-scm.com/downloads/win)**: без него не скачаются репозитории.

Когда установка закончится, открой новое окно терминала и проверь:

    claude --version

Терминал показал номер версии — всё стоит.

Если пишет, что команда не найдена, — смотри **[официальную инструкцию по установке](https://code.claude.com/docs/en/setup)**.

### 2. Скачай систему и методички

Система ищет методички в папке **repos** рядом с собой, поэтому структура такая:

    gkkd/
    ├── promt-gkkd/   ← эта система
    └── repos/        ← методички

Вставь команды в терминал по очереди.

Они одинаково работают на Mac и в PowerShell на Windows:

    mkdir ~/gkkd
    cd ~/gkkd
    git clone https://github.com/BermanRoman/promt-gkkd.git
    mkdir repos
    cd repos
    git clone https://github.com/BermanRoman/prompt-audience-research.git
    git clone https://github.com/BermanRoman/prompt-spin-questions.git
    git clone https://github.com/BermanRoman/promt-source-life.git
    git clone https://github.com/BermanRoman/promt-hvco.git
    git clone https://github.com/BermanRoman/prompt-clip-landing.git
    git clone https://github.com/BermanRoman/promt-copywriting.git

На Mac при первой команде `git` система может предложить поставить инструменты разработчика — соглашайся и потом повтори команду.

Что скачалось в **repos**:

* **[prompt-audience-research](https://github.com/BermanRoman/prompt-audience-research)** — исследование аудитории и клиента мечты, работает Исследователь ЦА;
* **[prompt-spin-questions](https://github.com/BermanRoman/prompt-spin-questions)** — СПИН-вопросы и отработка возражений для бота-продавца;
* **[promt-source-life](https://github.com/BermanRoman/promt-source-life)** — ядро СПИН для диагностики эксперта и продающего диалога;
* **[promt-hvco](https://github.com/BermanRoman/promt-hvco)** — история-магнит, которая цепляет и отдаёт реальный результат;
* **[prompt-clip-landing](https://github.com/BermanRoman/prompt-clip-landing)** — клип-лендинг для посадочной страницы;
* **[promt-copywriting](https://github.com/BermanRoman/promt-copywriting)** — правила текста для всех материалов.

### 3. Дай Claude доступ к папкам и запусти

Claude Code видит только ту папку, в которой его запустили.

Поэтому запускаешь его в папке системы, а папку с методичками добавляешь через `--add-dir`:

    cd ~/gkkd/promt-gkkd
    claude --add-dir ../repos

При первом запуске:

1. Claude откроет браузер — войди в свой аккаунт Claude.
2. Claude спросит, доверяешь ли ты файлам в этой папке. Отвечай «да»: это папка системы, которую ты только что скачал.
3. Во время работы Claude будет спрашивать разрешение создать или изменить файл. Разрешай. Чтобы не подтверждать каждый файл, нажми Shift+Tab — включится режим, в котором правки файлов принимаются сами.

Свои материалы эксперта — ролики, расшифровки, скриншоты — фиксик попросит положить в папку проекта.

Он сам скажет куда.

### 4. Подключи Wordstat, если нужно

Если хочешь, чтобы Разведчик сам смотрел спрос, подключи Wordstat по инструкции **[knowledge/wordstat-setup.md](knowledge/wordstat-setup.md)**.

Без него Разведчик тоже работает, только цифры спроса пришлёшь ты.

### 5. Начни работу

Напиши в Claude Code:

_«Начинаем работу по фиксику, согласно agents/00-fiksik.md»_

Прерываться можно. Чтобы продолжить с того же места, запусти Claude так:

    cd ~/gkkd/promt-gkkd
    claude --add-dir ../repos --continue

### 6. Собери воронку

Когда Фиксик отдаст папку проекта, собирай по её README.md: витрина, бот, страницы в любом сервисе, который умеет то, что написано в схеме бота.

### Обновить систему и методички

    cd ~/gkkd/promt-gkkd
    git pull
    git -C ../repos/prompt-audience-research pull
    git -C ../repos/prompt-spin-questions pull
    git -C ../repos/promt-source-life pull
    git -C ../repos/promt-hvco pull
    git -C ../repos/prompt-clip-landing pull
    git -C ../repos/promt-copywriting pull
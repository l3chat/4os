# Литературные конкурсы · Literary competitions

Создание, хранение, публикация и обновление списков литературных конкурсов на разных языках.

Этот проект находится в папке `literary-competitions/` общего репозитория [l3chat/4os](https://github.com/l3chat/4os). Другие задачи размещаются в отдельных папках; см. [корневой README](../README.md). Исходные списки хранятся в Markdown; сайт собирается Jekyll и публикуется через GitHub Pages.

## Состояние проекта

Подготовлена инфраструктура. Списки пока не заполнены. Конкурсы из прежних документов будут перенесены отдельно после проверки источников.

Предполагаемый адрес после включения Pages: **https://l3chat.github.io/4os/**. Фактический адрес показывает Settings → Pages; наличие этой ссылки в README не означает, что сайт уже опубликован.

## Разделы

| Язык произведений | Исходная страница |
| --- | --- |
| Русский | [Русскоязычные конкурсы](docs/contests/ru/index.md) |
| English | [English-language competitions](docs/contests/en/index.md) |
| Deutsch | [Deutschsprachige Wettbewerbe](docs/contests/de/index.md) |
| Français | [Concours francophones](docs/contests/fr/index.md) |
| Українська | [Українськомовні конкурси](docs/contests/uk/index.md) |

Язык раздела обозначает язык принимаемых произведений, а не страну организатора. Текст страницы по возможности пишется на языке раздела. Переводы одного списка могут добавляться отдельно; язык произведений и язык описания нельзя смешивать.

## Структура

| Путь | Назначение |
| --- | --- |
| `docs/index.md` | Главная страница сайта |
| `docs/contests/<язык>/index.md` | Указатель списков на соответствующем языке |
| `docs/contests/<язык>/<год>.md` | Годовой список, создаётся при добавлении конкурсов |
| `docs/_config.yml` | Настройки Jekyll, адрес и базовый путь сайта |
| `docs/_layouts/`, `docs/assets/` | Общий шаблон страниц и оформление |
| `templates/contest-list.md` | Шаблон годового списка и карточки конкурса |
| [`../.github/workflows/literary-competitions-pages.yml`](../.github/workflows/literary-competitions-pages.yml) | Сборка, проверка ссылок и публикация; исполняемый workflow хранится в корне репозитория |
| `scripts/check_links.py` | Проверка внутренних ссылок собранного сайта |
| `CONTRIBUTING.md` | Правила добавления и обновления |
| `AGENTS.md` | Инструкции для ИИ-агентов |

## Первое включение GitHub Pages

1. Открыть [Settings → Pages](https://github.com/l3chat/4os/settings/pages).
2. В **Build and deployment → Source** выбрать **GitHub Actions**.
3. Открыть [Actions](https://github.com/l3chat/4os/actions), выбрать **Literary competitions — build and publish Pages** и нажать **Run workflow** для ветки `main`.
4. Проверить успешное завершение `build` и `deploy`. Адрес сайта появится в результате `deploy` и в Settings → Pages.

После настройки каждый push в `main` запускает сборку и публикацию. Для pull request выполняется только сборка и проверка; сайт обновляется после слияния в `main`.

**Приватный репозиторий.** По документации GitHub, Pages для приватных репозиториев требует подходящего платного плана, например GitHub Pro. Если Pages недоступен, сначала нужно выбрать подходящий план или отдельно принять решение о смене видимости. Инфраструктура не меняет видимость репозитория. Опубликованные страницы Pages обычно общедоступны даже при приватном исходном репозитории.

Документация GitHub: [публикация сайта](https://docs.github.com/en/pages/getting-started-with-github-pages/configuring-a-publishing-source-for-your-github-pages-site), [собственный workflow](https://docs.github.com/en/pages/getting-started-with-github-pages/using-custom-workflows-with-github-pages).

Все пути ниже, кроме пути к workflow, указаны относительно папки `literary-competitions/`. Сайт публикуется с прежним базовым путём `/4os`; расположение исходников в репозитории не добавляет к адресу сайта сегмент `literary-competitions`.

## Как добавить список

1. Скопировать [шаблон](templates/contest-list.md), например в `docs/contests/en/2026.md`.
2. Заполнить заголовок, язык, год и карточки. Удалить подсказки и незаполненные примеры.
3. Добавить ссылку на годовой список в `docs/contests/en/index.md`, используя `relative_url`, как описано в CONTRIBUTING.
4. Зафиксировать изменения в GitHub. Проверить результат workflow в Actions.

Для дополнительного языка создать каталог с кодом BCP 47, страницу `index.md`, добавить её в `languages` файла `docs/_config.yml` и в таблицу README.

## Проверка

GitHub Actions собирает настоящий сайт Jekyll, затем проверяет локальные ссылки, изображения и якоря в итоговом HTML. При ошибке публикация не выполняется. Внешние ссылки автоматически не проверяются: доступность страницы не подтверждает актуальность условий конкурса.

Если сайт уже собран локально в `literary-competitions/_site`, ту же проверку можно запустить с Python 3 из папки проекта:

```bash
cd literary-competitions
python3 scripts/check_links.py _site --base-path /4os
```

Для нового домена или переименования репозитория изменить `url` и `baseurl` в `docs/_config.yml`, а также `--base-path` в workflow. Секреты и дополнительные токены для обычной публикации не нужны: workflow использует штатный `GITHUB_TOKEN`.

## Редакционные правила

Сроки, взносы, ограничения, языки произведений и правила применения ИИ проверяются по официальным источникам. Дата проверки записывается в карточке. Неизвестные сведения отмечаются явно. Рекомендации по выбору темы отделяются от требований организатора. Подробности — в [CONTRIBUTING.md](CONTRIBUTING.md).

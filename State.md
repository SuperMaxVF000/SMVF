# SMVF State

## v1.0beta — init

### Архитектура
- Telethon (не hikka-tl-new) — чистая установка
- Три типа модулей: HikkaCompat / MCUBCompat / SMVFNative
- Inline-бот: автосоздание через BotFather, fallback — ручной токен
- Лог-группа: создаётся автоматически, все логи туда + терминал
- Конфиг: интерактивный ввод в терминале → сохраняется в config.json локально
- Язык: ru/en, выбор при первом запуске

### Структура
```
smvf/
  smvf/
    __init__.py         — точка входа, run()
    __main__.py         — python -m smvf
    version.py          — VERSION, BUILD
    core/
      loader.py         — загрузчик 3 типов модулей
      dispatcher.py     — диспетчер команд
      keepalive.py      — никогда не засыпает
      database.py       — config.json + runtime DB
    inline/
      manager.py        — создание бота, inline query handler
      botfather.py      — автосоздание через BotFather
    modules/            — встроенные модули
      info.py
      ping.py
      loader_cmd.py     — .lm .dlm .im .um
      help.py
      logs.py           — .logstxt
    utils/
      logger.py         — логгер: терминал + группа + файл
      platform.py       — определение платформы (RPi/Termux/Ubuntu/UserLand)
      colors.py         — ANSI цвета терминала
      i18n.py           — ru/en строки
      helpers.py        — утилиты
    compat/
      hikka.py          — совместимость с Hikka-модулями
      mcub.py           — совместимость с MCUB-модулями
  assets/
    banner.txt
    smvf_pfp.png        — заглушка (пользователь заменяет)
  docs/
    MODULES.md          — документация SMVF-модулей
    HIKKA_COMPAT.md     — гайд переписки Hikka→SMVF
    MCUB_COMPAT.md      — гайд MCUB→SMVF
    AI_PROMPT.md        — промпт для ИИ конвертации модулей
  scripts/
    install.sh          — установщик Ubuntu/UserLand
    termux.sh           — установщик Termux
    rpi.sh              — установщик RPi
  config.example.json
  requirements.txt
  README.md
  .gitignore
```

### Статус файлов
- [x] version.py
- [x] smvf/__init__.py
- [x] smvf/__main__.py
- [x] smvf/core/database.py
- [x] smvf/core/loader.py
- [x] smvf/core/dispatcher.py
- [x] smvf/core/keepalive.py
- [x] smvf/utils/logger.py
- [x] smvf/utils/platform.py
- [x] smvf/utils/colors.py
- [x] smvf/utils/i18n.py
- [x] smvf/utils/helpers.py
- [x] smvf/compat/hikka.py
- [x] smvf/compat/mcub.py
- [x] smvf/inline/botfather.py
- [x] smvf/inline/manager.py
- [x] smvf/modules/ping.py
- [x] smvf/modules/info.py
- [x] smvf/modules/help.py
- [x] smvf/modules/loader_cmd.py
- [x] smvf/modules/logs.py
- [x] assets/banner.txt
- [x] requirements.txt
- [x] config.example.json
- [x] .gitignore
- [x] docs/MODULES.md
- [x] docs/HIKKA_COMPAT.md
- [x] docs/MCUB_COMPAT.md
- [x] docs/AI_PROMPT.md
- [x] scripts/install.sh
- [x] scripts/termux.sh
- [x] scripts/rpi.sh
- [x] README.md

### Заметки
- Inline username: smvfinline + 4 рандомных цифры
- Log group: создаётся с userbot + inline bot
- Premium emoji: проверка me.premium перед использованием
- keepalive: asyncio loop никогда не прерывается, reconnect с backoff

## Завершено
Все 39 файлов созданы. Синтаксис всех .py — OK. Zip: SMVF-1.0beta.zip
## Fix 1 — Termux pip / UserLand systemd
- termux.sh: убран pip upgrade (запрещён в Termux)
- install.sh: systemd-блок обёрнут в проверку is-system-running (UserLand не имеет systemd)
- install.sh: pip upgrade теперь игнорирует ошибку через 2>/dev/null
## Fix 2 — авторизация и скрипты
- termux.sh: убран set -e, [[ ]] → [ ], pip upgrade убран
- install.sh: systemd проверяется перед предложением
- __init__.py: client.start() → явный _authorize() с input() для кода и 2FA

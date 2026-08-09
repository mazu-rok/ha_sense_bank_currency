# Sense Bank Currency для Home Assistant

Кастомна інтеграція для [Home Assistant](https://www.home-assistant.io/), яка відстежує **курс купівлі USD/UAH**, опублікований [Сенс Банком](https://sensebank.ua) (Sense Bank, Україна).

Створює два сенсори: поточний курс купівлі та простий індикатор тренду, що показує, чи курс зростає, чи знижується.

[![Open your Home Assistant instance and open a repository inside the Home Assistant Community Store.](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=mazu-rok&repository=ha_sense_bank_currency&category=integration)

## Можливості

- Опитує публічне API курсів валют Сенс Банку із заданим інтервалом
- `sensor` з поточним курсом купівлі USD/UAH (в UAH)
- `sensor` з трендом курсу (`going_high` / `going_low`), який зберігається після перезавантаження Home Assistant
- Налаштовується повністю через інтерфейс (config flow) — YAML не потрібен
- Інтервал опитування можна змінити пізніше в **Опціях** інтеграції

## Встановлення

### HACS (рекомендовано)

Натисніть на бейдж вище, щоб одразу додати цей репозиторій у HACS, або зробіть це вручну:

1. Відкрийте **HACS** у вашому Home Assistant.
2. Перейдіть у **Integrations** → меню з трьома крапками → **Custom repositories**.
3. Додайте `https://github.com/mazu-rok/ha_sense_bank_currency` з категорією **Integration**.
4. Знайдіть **Sense Bank Currency** у списку та натисніть **Download**.
5. Перезавантажте Home Assistant.

### Вручну

1. Завантажте або клонуйте цей репозиторій.
2. Скопіюйте папку `custom_components/sensebank_currency` у директорію `config/custom_components/` вашого Home Assistant.
3. Перезавантажте Home Assistant.

## Налаштування

Інтеграція налаштовується повністю через інтерфейс Home Assistant:

1. Перейдіть у **Settings → Devices & Services**.
2. Натисніть **Add Integration** і знайдіть **Sense Bank Currency**.
3. За бажанням задайте **інтервал опитування** (у хвилинах, 1–1440). За замовчуванням — **15 хвилин**.
4. Підтвердіть — буде створено запис інтеграції "Sense Bank USD/UAH".

Щоб змінити інтервал опитування пізніше, відкрийте запис інтеграції та натисніть **Configure** (options flow).

## Сенсори

| Сутність | Опис | Примітки |
|---|---|---|
| `sensor.usd_uah_buy_rate` | Поточний курс купівлі USD/UAH | Device class `monetary`, одиниця виміру `UAH`. Атрибут `last_updated` (ISO-мітка часу останнього успішного оновлення). |
| `sensor.usd_uah_trend` | Тренд курсу | Стан `going_high` або `going_low` залежно від порівняння з попереднім значенням. Атрибут `previous_rate`. Відновлюється після перезавантаження. |

*(Точні entity ID залежать від налаштувань іменування у вашому Home Assistant; обидва сенсори експортуються з `has_entity_name = True` під записом пристрою "Sense Bank USD/UAH".)*

## Як це працює

- Дані отримуються з `https://sensebank.ua/api/pages/currency-exchange`.
- Інтеграція шукає блок `ExchangeRateTabs` у відповіді та витягує значення `buy` для запису `USD/UAH`.
- `DataUpdateCoordinator` керує опитуванням із заданим інтервалом (`iot_class: cloud_polling`).
- Якщо очікуваний блок/валюта/значення не знайдені у відповіді API, оновлення завершується помилкою — координатор логує/піднімає `UpdateFailed`.

## Обмеження

- Відстежується лише **USD/UAH**, і лише курс **купівлі** — інші валюти чи курс продажу наразі не доступні.
- Залежить від стабільності структури публічного API/сторінки Сенс Банку; якщо банк змінить формат, інтеграцію може знадобитися оновити.

## Застереження

Це неофіційна інтеграція, що підтримується спільнотою, і не пов'язана з Сенс Банком та не схвалена ним.

## Внесок

Issues та pull requests вітаються.

## Ліцензія

<!-- Додайте ліцензію (наприклад, MIT), якщо вона застосовується до цього репозиторію. -->

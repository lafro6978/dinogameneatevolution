# Dino Game: NEAT Evolution

🇷🇺 Интеллектуальная игра-раннер (аналог Chrome Dino) с автопилотом на базе генетического алгоритма **NEAT**. Проект разработан студентом **ВКИ НГУ** в рамках профессионального модуля **ПМ.04 «Сопровождение и обслуживание программного обеспечения компьютерных систем»**.

🇬🇧 An AI-powered runner game (Chrome Dino clone) featuring the **NEAT** genetic algorithm. Developed by a student of the **VKI NSU** as part of the **PM.04 "Support and Maintenance of Computer Systems Software"** course.

---

## 🌟 Ключевые особенности / Key Features

* **🧠 Искусственный интеллект / AI (NEAT):** Самообучающаяся нейросеть, улучшающая свои результаты с каждым новым поколением. / Self-learning neural network improving over generations.
* **☄️ Кастомное препятствие / Custom Obstacle:** Падающий камень с уникальной механикой рывка (переката). / Falling rock featuring a roll/dash mechanic.
* **⚡ Продвинутая физика / Advanced Physics:** Движение отвязано от кадров за счет **Delta Time (`dt_scale`)**. / Frame-rate independent physics using Delta Time.
* **💻 Оптимизация / Optimization:** Кэшированные пиксельные маски коллизий (Pixel-perfect) для разгрузки процессора. / Cached pixel-perfect collision masks.
* **🚀 Turbo-режим / Turbo Mode:** Ускоренное обучение популяции ИИ без отрисовки графики. / Fast AI training without rendering graphics.

---

## 🚀 Установка и запуск / Quick Start

### Вариант 1: Для игроков / For Players
🇷🇺 Скачайте готовый `DinoGame.exe` в разделе **[Releases](https://github.com/lafro6978/dinogameneatevolution/releases)** и запускайте игру в один клик.  
🇬🇧 Download the ready-to-use `DinoGame.exe` from the **[Releases](https://github.com/lafro6978/dinogameneatevolution/releases)** page and play instantly.

### Вариант 2: Для разработчиков / For Developers
🇷🇺 Клонируйте репозиторий и запустите проект из исходного кода:  
🇬🇧 Clone the repository and run the project from source:
```bash
git clone [https://github.com/lafro6978/dinogameneatevolution.git](https://github.com/lafro6978/dinogameneatevolution.git)
cd dinogameneatevolution
pip install -r requirements.txt
python src/main.py
```

## 🎮 Управление / Controls

### 🕹️ Ручной режим / Manual Mode
* **`W` / `UP` / `SPACE`** — Прыжок / Jump
* **`S` / `DOWN`** — Приседание / Duck
* **`D` / `RIGHT`** — Рывок / Перекат (от камня) / Roll / Dash
* **`ESC`** — Пауза и настройки / Pause & Settings

### 🤖 Автопилот и ИИ / AI Assistant
* **`A`** — Включить / Выключить автопилот NEAT / Toggle AI Autopilot
* **`T`** — Включить Turbo-режим (ускоренное обучение) / Toggle Turbo Mode
* **`V`** — Показать телеметрию (зрение ИИ) / Show AI Telemetry

---

## 📁 Структура проекта / Project Structure

* **`src/main.py`** — Главный контроллер и машина состояний (State Machine).
* **`src/ai_env.py`** — Модель игрового окружения, физика и сенсоры ИИ.
* **`src/sprites.py`** — Логика сущностей (динозавр, препятствия, частицы).
* **`src/renderer.py`** — Отрисовка графики (паттерн MVC View).
* **`src/config.py`** — Глобальные константы и `AssetManager` для кэширования.
* **`config-feedforward.txt`** — Конфигурация гиперпараметров NEAT.

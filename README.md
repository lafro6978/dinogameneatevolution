<div align="center">

# 🦖 Dino Game: NEAT Evolution
### Интеллектуальный ИИ-раннер на базе нейроэволюционного алгоритма NEAT / AI-Powered Runner Utilizing NeuroEvolution of Augmenting Topologies

![Python 3.8+](https://img.shields.io/badge/Python-3.8%2B-3776AB?style=for-the-badge&logo=python&logoColor=white)
![NEAT Algorithm](https://img.shields.io/badge/AI-NEAT_NeuroEvolution-FF6F00?style=for-the-badge&logo=tensorflow&logoColor=white)
![Pygame Engine](https://img.shields.io/badge/Engine-Pygame_%2B_MVC-239120?style=for-the-badge&logo=python&logoColor=white)
![Architecture](https://img.shields.io/badge/Pattern-FSM_%26_MVC-512BD4?style=for-the-badge)
![Release](https://img.shields.io/badge/Release-v1.0.0_(exe)-0078D4?style=for-the-badge&logo=windows&logoColor=white)

<br>

![DEMO](https://i.imgur.com/AS46zCi.gif)

</div>

---

## 📌 Overview / Обзор проекта

- **🇷🇺 RU:** Учебный и исследовательский проект интеллектуального раннера на базе нейроэволюционного алгоритма **NEAT (NeuroEvolution of Augmenting Topologies)**, разработанный студентом **ВКИ НГУ** в рамках профессионального модуля ПМ.04 *«Сопровождение и обслуживание программного обеспечения компьютерных систем»*. Система моделирует эволюционное обучение популяции ИИ-агентов в динамической среде с кастомной физикой, телеметрией сенсоров и оптимизацией вычислений.
- **🇬🇧 EN:** Academic and engineering project implementing an AI-powered runner game utilizing the **NEAT (NeuroEvolution of Augmenting Topologies)** algorithm. Developed for the PM.04 *"Support and Maintenance of Computer Systems Software"* module at **VKI NSU** (Higher College of Informatics of Novosibirsk State University).

---

## 🧠 Core Features & Engineering / Ключевые особенности и архитектура

| Feature / Компонент | Technical Implementation (EN) | Техническая реализация (RU) |
| :--- | :--- | :--- |
| **🧬 NEAT Neural Network** | Automated agent training via neuroevolution of augmenting topologies with custom fitness evaluation and generation telemetry. | Автоматизированное обучение популяции ИИ-агентов методами нейроэволюции с расчётом фитнес-функции и сбором статистики по поколениям. |
| **🪨 Custom Mechanics** | Falling rock obstacle requiring a dedicated roll/dash evasion maneuver (`D` / `RIGHT`). | Реализация кастомного динамического препятствия (падающий камень) с новой механикой уклонения через рывок/перекат. |
| **⏱️ Frame-Independent Physics** | Delta Time scaling (`dt_scale`) implementation for deterministic physics execution across varying hardware frame rates. | Масштабирование игровой физики на основе `Delta Time` (`dt_scale`) для обеспечения полной аппаратной независимости от FPS. |
| **⚡ Performance Optimization** | Cached pixel-perfect collision masks to eliminate redundant runtime calculations and reduce CPU overhead. | Предварительное кэширование пиксельных масок коллизий для исключения повторных вычислений в реальном времени и снижения нагрузки на CPU. |
| **🚀 Headless Turbo Mode** | High-speed background training execution without graphical rendering for rapid population evolution. | Турбо-режим ускоренного обучения ИИ без отрисовки графики для быстрой эволюции поколений. |
| **🏗️ MVC & FSM Architecture** | Strict separation between the Finite State Machine controller (`main.py`), environment physics (`ai_env.py`), and rendering layer (`renderer.py`). | Строгое разделение логики по паттерну **MVC** и управление состояниями игры через отказоустойчивый **конечный автомат (FSM)**. |

---

## 🚀 Installation and Execution / Установка и запуск

### 📦 Option 1: Release Binary (For End Users) / Готовый `.exe` файл
- **🇷🇺 RU:** Загрузите готовый скомпилированный файл **`DinoGame.exe`** (не требует установки Python) из официального раздела [**Releases**](https://github.com/lafro6978/dinogameneatevolution/releases).
- **🇬🇧 EN:** Download the standalone compiled executable (**`DinoGame.exe`**) directly from the [**Releases**](https://github.com/lafro6978/dinogameneatevolution/releases) section.

### 💻 Option 2: Source Code (For Developers) / Запуск из исходного кода
**Requirements / Требования:** `Python 3.8+`

1. Clone the repository / Склонируйте репозиторий:
   `git clone https://github.com/lafro6978/dinogameneatevolution.git`
2. Navigate to the project folder / Перейдите в директорию проекта:
   `cd dinogameneatevolution`
3. Install dependencies / Установите зависимости:
   `pip install -r requirements.txt`
4. Run the application / Запустите проект:
   `python src/main.py`

---

## 🎮 Controls / Управление

### 🕹️ Manual Operation / Ручной режим
| Клавиша / Key | Action (EN) | Действие (RU) |
| :--- | :--- | :--- |
| **`W`** / **`UP`** / **`SPACE`** | Jump | Прыжок |
| **`S`** / **`DOWN`** | Duck | Приседание |
| **`D`** / **`RIGHT`** | Roll / Dash (Falling rock evasion) | Рывок / Перекат (уклонение от падающего камня) |
| **`ESC`** | Pause and Settings Menu | Пауза и меню настроек |

### 🤖 AI Operation / Автопилот и телеметрия ИИ
| Клавиша / Key | Action (EN) | Действие (RU) |
| :--- | :--- | :--- |
| **`A`** | Toggle NEAT Autopilot | Включение / выключение нейросетевого автопилота NEAT |
| **`T`** | Toggle Turbo Mode (Fast Training) | Включение / выключение турбо-режима ускоренного обучения |
| **`V`** | Toggle Telemetry (Neural Sensors) | Отображение телеметрии, векторов расстояний и сенсоров ИИ |

---

## 📂 Project Structure / Структура проекта

- **`src/main.py`** — Core controller and finite state machine (FSM) implementation. / Главный контроллер приложения и реализация конечного автомата состояний.
- **`src/ai_env.py`** — Environment model, `dt_scale` physics calculations, and neural sensor data collection. / Модель игровой среды, расчёт физики и сбор векторов сенсоров для входа нейросети.
- **`src/sprites.py`** — Entity logic (player, custom obstacles, cached collision masks, particles). / Объектно-ориентированная логика игровых сущностей и кэширование масок коллизий.
- **`src/renderer.py`** — Graphical rendering and UI telemetry layer adhering to the MVC pattern. / Модуль графической отрисовки и визуализации телеметрии (Представление по шаблону MVC).
- **`src/config.py`** — Global constants, physics parameters, and asset management utilities. / Глобальные константы конфигурации и менеджер ресурсов.
- **`config-feedforward.txt`** — NEAT hyperparameter configuration file (topology mutations, population size, activation functions). / Конфигурационный файл гиперпараметров нейроэволюции NEAT.

# Dino Game: NEAT Evolution

## Overview / Обзор проекта

* **EN:** Academic project implementing an AI-powered runner game utilizing the NEAT (NeuroEvolution of Augmenting Topologies) algorithm. Developed for the PM.04 "Support and Maintenance of Computer Systems Software" by student of the VKI NSU.
* **RU:** Учебный проект интеллектуального раннера на базе алгоритма NEAT (NeuroEvolution of Augmenting Topologies), разработанный студентом ВКИ НГУ в рамках профессионального модуля ПМ.04 «Сопровождение и обслуживание программного обеспечения компьютерных систем».

---

## Core Features / Ключевые особенности

* **NEAT Neural Network:** Automated agent training via neuroevolution of augmenting topologies. / Автоматизированное обучение агентов методами нейроэволюции.
* **Custom Mechanics:** Falling rock obstacle requiring a dedicated roll/dash maneuver. / Реализация кастомного препятствия (падающий камень) с механизмом рывка.
* **Frame-Independent Physics:** Delta Time scaling (`dt_scale`) implementation for consistent execution across varying hardware. / Масштабирование физики на основе Delta Time для обеспечения аппаратной независимости.
* **Performance Optimization:** Cached pixel-perfect collision masks to reduce CPU overhead. / Кэширование пиксельных масок коллизий для снижения нагрузки на центральный процессор.
* **Turbo Mode:** Headless training execution without graphical rendering for rapid population generation. / Режим ускоренного обучения без отрисовки графики.

---

## Installation and Execution / Установка и запуск

### Release Binary (For End Users) / Исполняемый файл

* **EN:** Download the compiled executable (`DinoGame.exe`) from the [Releases](https://github.com/lafro6978/dinogameneatevolution/releases) section.
* **RU:** Загрузите готовый исполняемый файл (`DinoGame.exe`) из официального раздела [Releases](https://github.com/lafro6978/dinogameneatevolution/releases).

### Source Code (For Developers) / Исходный код

Requirements: Python 3.8 or higher.

```bash
git clone https://github.com/lafro6978/dinogameneatevolution.git
cd dinogameneatevolution
pip install -r requirements.txt
python src/main.py

```

---

## Controls / Управление

### Manual Operation / Ручной режим

* **`W` / `UP` / `SPACE`**: Jump / Прыжок
* **`S` / `DOWN`**: Duck / Приседание
* **`D` / `RIGHT`**: Roll / Dash (Obstacle evasion) / Рывок (перекат)
* **`ESC`**: Pause and Settings Menu / Пауза и меню настроек

### AI Operation / Автопилот и ИИ

* **`A`**: Toggle NEAT Autopilot / Включение/выключение автопилота
* **`T`**: Toggle Turbo Mode / Включение турбо-режима
* **`V`**: Toggle Telemetry (Neural sensors) / Отображение телеметрии ИИ

---

## Project Structure / Структура проекта

* **`src/main.py`**: Core controller and finite state machine implementation. / Главный контроллер и конечный автомат.
* **`src/ai_env.py`**: Environment model, physics calculations, and sensor data collection. / Модель игровой среды, физика и сенсоры ИИ.
* **`src/sprites.py`**: Entity logic (player, obstacles, particles). / Логика игровых сущностей.
* **`src/renderer.py`**: Graphical rendering layer adhering to the MVC pattern. / Модуль визуализации (представление MVC).
* **`src/config.py`**: Global constants and asset management utilities. / Константы конфигурации и менеджер ресурсов.
* **`config-feedforward.txt`**: NEAT hyperparameter configuration file. / Файл конфигурации гиперпараметров NEAT.

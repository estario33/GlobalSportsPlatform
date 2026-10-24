# Сквозная трассировка требований

[← К оглавлению](../README.md)

| Требование | Цели | ФТ (группы) | Сервисы | ADR | UC | Фаза |
|---|---|---|---|---|---|---|
| R1 Группы | BG-1 | FR-SC | Social, Notifications | 001, 007, 008 | 04, 13 | 1–2 |
| R2 Аналитика | BG-3 | FR-AN | Activity, Analytics | 004, 008 | 02, 03 | 1–3 |
| R3 Поиск людей | BG-1, BG-4 | FR-DS | Discovery, Identity | 007, 008 | 06 | 2–3 |
| R4 Инвентарь | BG-2 | FR-GR | Gear & Plans | 011 | 07 | 1 |
| R5 Планы | BG-3 | FR-PL | Gear & Plans | — | 08 | 2+ |
| R6 Уведомления друзьям | BG-1 | FR-NT, FR-SC-05 | Notifications | 001 | 05 | 1 |
| R7 Геймификация | BG-3, BG-1 | FR-GM, FR-CP | Gamification, Competitions | 006 | 05, 09 | 1–3 |
| R8 Промо и новости | BG-2 | FR-PM | Promo & Content | 011 | 10 | 2–3 |
| R9 Устройства | BG-3 | FR-DV, FR-AR-03 | Device Integration, клиент | 005, 009 | 02, 11 | 1–3 |
| R10 Интеграция | BG-2 | FR-CM | Commerce Connector | 010 | 10 | 1–2 |
| R11 Региональные промо | BG-2 | FR-PM-02, FR-AD-01 | Promo & Content | 011 | 14 | 2 |
| O1 Мир | BG-4 | — | Ячейки, Directory | 002, 003, 007 | 01, 02, 06 | 0–2 |
| O2 Соревнования | BG-1 | FR-CP | Competitions, Ingestion | 006, 009 | 09, 13 | 3 |
| O3 Продвинутые устройства | BG-3 | FR-DV-02, FR-DV-03, NFR-MOD-01 | Device Integration, Ingestion | 001, 009, 013 | 11, 02 | 2–3 |
| O4 Фитнес телефона | BG-3 | FR-AR-03 | Клиент | 005 | 02 | 1 |
| O5 Охрана данных | BG-4 | FR-PR, NFR-SEC | Identity и все | 008, 012 | 01, 12 | 0 |
| O6 Не все требования равнозначны | все | [MoSCoW-приоритизация](02-functional-requirements.md) | — | — | — | [фазы](06-roadmap.md) |

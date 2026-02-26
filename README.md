# Eyes Fullstack v2 (адаптировано под таблицы из скриншота)

## Запуск
```bash
docker compose up --build
```

- Frontend: http://localhost:3000
- Backend (Swagger): http://localhost:8000/docs
- Postgres: localhost:5432 (eyes/eyes)

## Демо-аккаунты
- admin@example.com / admin123
- doctor@example.com / doctor123
- surgeon@example.com / surgeon123
- patient@example.com / patient123

## Таблицы (создаются автоматически на старте)
appointments, checklist_item_templates, checklist_templates, comments, file_assets,
operation_log, organizations, patient_checklist_items, patient_checklists, patients,
reviews, telegram_identities, users

## Что реализовано по user-flow
- Логин + /auth/me
- Дашборд summary
- Пациенты (список/карточка)
- Кейсы (= patient_checklists) список/карточка
- Замеры (MEASUREMENT item) + смена статуса NEED_DATA / IN_CALC_QUEUE
- Очередь на расчёт + расчёт (MVP формула) => CALCULATED
- История действий (operation_log)

> Дальше легко нарастить: загрузку файлов (file_assets), полноценный чеклист UI, уведомления, маршрутный лист и т.д.

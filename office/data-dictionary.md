# Реестры и связи

Активные реестры: `data/office/`. Шаблоны: `templates/registers/`. Формат новых CSV: UTF-8, разделитель `;`, первая строка — заголовок; числовые значения для инструментов с точкой, без разделителей тысяч. Исходная `data/spec-matrix.csv` сохраняет свой прежний формат с запятыми. Пустые поля не становятся нулём. Списки ID разделяются `|`.

Ключи не перенумеровывать при сортировке. SPEC — факт/требование спецификации, WBS — пакет работ, quantity — измеренное/вычисленное количество, quote — предложение, line — строка стоимости, change — изменение. Связь может быть многие-ко-многим; один факт геометрии не равен одной закупке. Новому источнику присваивать SRC-ID, сохранять ревизию, locator и SHA-256.

Начальная WBS имеет статус PROPOSED; привязка SPEC к ней — организационная, не утверждение технической границы. Справочные параметры и неопределённые записи остаются в покрытии, но не включаются в денежный итог автоматически.

| Реестр | Назначение |
|---|---|
| spec-crosswalk | 73 исходные записи, устойчивые ID и исходные статусы без повышения достоверности |
| wbs | Предварительные пакеты, границы и ответственные роли |
| roles / tasks | Назначения и ограниченные задания, зависимости, критерии приёма |
| questions / decisions | Пробелы, варианты, влияние и фактические решения |
| source-register | Происхождение, доступность, ревизии и хеши |
| quantities | Количество и единица с формулой, листом/строкой и основанием |
| quotes | Исполнение, единица цены, комплект, коммерческие условия и выбор |
| estimate | Строки стоимости с SPEC/WBS и источником |
| cost-control | База, обязательства, факт, платежи и прогноз без пересечения |
| changes / risks / interfaces | Изменения, неопределённость и ответственность на стыках |
| deliverables | Выдаваемая версия, проверка, решение, основной файл и сопровождение |

## Денежный CSV для инструментов

`estimate.csv`: quantity и unit_price обязательны; unit явно задаёт одну и ту же единицу количества и цены. Перед запуском уже должно быть выполнено обоснованное приведение. currency — согласованная валюта; price_basis — NET или GROSS. status — CONFIRMED либо APPROVED_ASSUMPTION с непустым assumption_id. source_id ссылается на документ/расчёт-основание в source-register; если цена из КП, в notes также хранится quote_id. Инструмент проверяет наличие ссылки, но не подлинность и смысл её документа.

В cost_type использовать понятную категорию: MATERIAL, EQUIPMENT, LABOUR, SUBCONTRACT, DESIGN, SURVEY, LOGISTICS, TESTING, OTHER. Предмет цены и включённость расходов важнее названия категории. Отрицательные строки для изменения анализируются через сравнение версий; в базовой смете инструмент принимает неотрицательные количества и цены. Скидку/кредит, если нужен отдельный отрицательный расчёт, подготовить вне этого ограниченного инструмента с проверкой и основанием.

Суммирование разных валют/налоговых основ запрещено без предварительного документированного приведения. Поля налога и курса не угадываются скриптом. Выход инструмента CALCULATION_ONLY_NOT_APPROVAL не является решением начальника.

## Колонки шаблонов

- `spec-crosswalk.csv`: `spec_id`, `source_row`, `system`, `item`, `source_value`, `source_confidence`, `source_commit`, `wbs_id`, `operational_status`, `next_action`.
- `wbs.csv`: `wbs_id`, `parent_id`, `name`, `scope`, `status`, `owner_role`, `source_ref`.
- `roles.csv`: `role_id`, `role_name`, `assignee`, `appointment_status`, `scope`, `reviewer`.
- `tasks.csv`: `task_id`, `title`, `owner_role`, `assignee`, `status`, `depends_on`, `input_refs`, `deliverable`, `acceptance`, `due_date`.
- `questions.csv`: `question_id`, `topic`, `spec_ids`, `missing_or_conflict`, `options_and_source`, `impact`, `owner_role`, `status`, `decision_id`.
- `decisions.csv`: `decision_id`, `date`, `authority`, `instruction_or_decision`, `scope`, `status`, `evidence`.
- `source-register.csv`: `source_id`, `path_or_url`, `revision`, `source_type`, `evidence_status`, `locator`, `sha256`, `access_scope`, `issuer`, `source_date`, `received_date`, `document_number`, `scale`.
- `quantities.csv`: `quantity_id`, `spec_ids`, `wbs_id`, `description`, `quantity`, `unit`, `formula`, `source_id`, `source_locator`, `revision`, `status`, `assumption_id`.
- `quotes.csv`: `quote_id`, `supplier`, `document_number`, `price_date`, `valid_until`, `spec_ids`, `wbs_id`, `description`, `quantity_basis`, `price_unit`, `package_content`, `unit_price`, `currency`, `tax_basis`, `tax_rate`, `included_scope`, `excluded_scope`, `delivery_place`, `delivery_terms`, `lead_time`, `payment_terms`, `source_id`, `locator`, `technical_status`, `selection_reason`.
- `estimate.csv`: `line_id`, `wbs_id`, `spec_ids`, `description`, `cost_type`, `quantity`, `unit`, `unit_price`, `currency`, `price_basis`, `source_id`, `status`, `assumption_id`, `notes`.
- `cost-control.csv`: `period`, `wbs_id`, `baseline_version`, `currency`, `price_basis`, `baseline_amount`, `committed_total`, `actual_cost`, `payments`, `remaining_commitments`, `uncommitted_remaining`, `approved_unallocated_reserve`, `forecast_final`, `source_id`, `status`.
- `changes.csv`: `change_id`, `date`, `initiator`, `reason`, `old_revision`, `new_revision`, `spec_ids`, `wbs_ids`, `estimate_line_ids`, `scope_effect`, `quantity_effect`, `price_effect`, `schedule_effect`, `interface_effect`, `decision_id`, `status`.
- `risks.csv`: `risk_id`, `description`, `spec_ids`, `wbs_ids`, `evidence`, `cost_effect`, `schedule_effect`, `technical_effect`, `mitigation`, `owner_role`, `status`, `decision_id`.
- `interfaces.csv`: `interface_id`, `from_system`, `to_system`, `spec_ids`, `requirement`, `source_id`, `responsible_from`, `responsible_to`, `cost_boundary`, `status`, `decision_id`.
- `deliverables.csv`: `deliverable_id`, `task_id`, `version`, `kind`, `main_file`, `support_folder`, `review_ref`, `decision_id`, `status`, `manifest_path`.

У source-register дата документа (`source_date`) и дата получения (`received_date`) различаются. Издатель/автор (`issuer`), номер документа и масштаб заполняются при наличии; пустой масштаб неприменимого файла не является ошибкой. Для исходной импортированной базы дата получения 10.09.2026 не подменяет отсутствующую дату первичного документа.

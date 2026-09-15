# M09 — независимая сверка источников auxiliary / hydraulic

15.09.2026. Результат: **PASS_WITH_OPEN_INPUTS**, только как реестр ценовых аналогов. Полная комплектность, достаточность оборудования и закупочная готовность не подтверждаются. Проверены все 23 строки двух JSON на валюту, арифметику, границы поставки и дубли; повторно открыта выборка существенных цен. Исходники не редактировались.

Прямая сверка:

- [Vetus HT1010 и аксессуары](https://www.vetus-shop.com/aluminium-hydraulic-tank-70-incl-ht1013-p-2024.html): все шесть цен страницы совпадают с реестром; ex VAT явно. Один HT1013 уже в баке. Дополнительные клапаны и масло не имеют назначенного количества; канистра20л не литр. Бак отсутствует, аксессуары под заказ.
- [HT1016SD2](https://www.vetus-shop.com/variably-adjustable-piston-pump-45cc-left-handed-saeb-flang-p-2033.html): 2716.67GBP ex VAT; насос отсутствует. LH, SAE-B13 и PRM раскрыты, применимость к Yanmar/PTO не утверждена.
- [ECB](https://www.ecb.europa.eu/stats/policy_and_exchange_rates/euro_reference_exchange_rates/html/eurofxref-graph-gbp.en.html): 14.09.2026 — 0.85598GBP за EUR. Все семь делений и округлений до0.01EUR совпали. Это стоимость товара NET, без международной доставки/таможни/импортного НДС.
- [Webasto ImpEK](https://standheizung-ersatzteile.com/thermo-pro-90-24v-marine-std): SKU9029941C, 2405.71EUR с НДС. [FAQ](https://standheizung-ersatzteile.com/shop/en/faq) указывает19%; 2021.61NET арифметически верно. [SVB](https://www.svb24.com/en/webasto-thermo-pro-90-marine-diesel-water-heater-24-v-9-1-kw.html) —2260.46NET. Это альтернативные продавцы одного отопителя; собственное отопление остаётся опцией. Налог Польши не назначается ставкой магазина.
- [Таблица Fireboy](https://www.nauticabasile.it/eng/osculati/fixed-fireboy-fire-extinguishers-with-clean-agent-and-manualautomatic-activation-46870/):31.610.31=4251.10EUR,26.8кг,31.1м³;31.620.55=2332.10EUR,13.4кг,15.6м³. [ESC](https://www.nauticabasile.it/eng/osculati/fireboy-esc-series-automatic-engine-shutdown-systems-46872/?listRef=related):31.650.03=586.40EUR,8цепей. [Условия L.8](https://www.nauticabasile.it/eng/pages/sales-conditions/) подтверждают VAT включён, без ставки: NETnull корректно. Индивидуальный URL большого баллона при повторном открытии дал ошибку; цена и исполнение независимо подтверждены доступной таблицей семейства. Ни один баллон не принят по защищаемому объёму.
- [Marco UP3](https://www.svb24.com/en/marco-up3-electric-oil-change-pump.html) и [BilgeAlert](https://www.svb24.com/en/johnson-pump-bilge-alert-high-water-alarm-with-ultima-switch.html):24V варианты168.03 и97.44NET соответственно; дешёвые12V варианты не подставлены.

Другие строки сверены по содержимому JSON, не каждая повторно открывалась. Независимые расчёты Decimal не обнаружили ошибок NET: прямые exVAT цены сохранены, ImpEK деление на1.19, GBP деление накурс. Неизвестные количества не заменены единицей/нулём. Предлагаемые насос/бак/регулятор/охладитель по1 — именно рабочая гипотеза, не утверждённое требование. Шланги, PTO, силовые узлы, исполнительные устройства, монтаж и испытания исключены; «всё гидравлическое оборудование яхты» этим набором не закрыто.

Риски сведения: ME-29 в hydraulic и ME20… в auxiliary нужно сопоставить каноническим ID. Числа hydraulic сохранены строками, auxiliary — числами; импорт обязан преобразовать типы, а не конкатенировать. Клапан HT1013 уже в HT1010; альтернативы ручных помп, macerator, вентилятора, баллона и отопителя не суммировать автоматически. Общая заметка о насосе/24V повторяется в hydraulic даже у масла/охладителя: это контекст всей системы, не электрическое свойство этих деталей. Эти замечания не меняют цен и не требуют редактирования исходников для чтения человеком.

SHA256 проверенных файлов:

- `deliverables/M09/v001/01_support/auxiliary/offers.json`: `a7e2267066ecdf68b2b0e228c7cacff1fc568e1e77746c558e72a012dc734d1a`
- `deliverables/M09/v001/01_support/hydraulic/offers.json`: `eba8dd6869d16cfc9a56c144c6eb4356a4a48d093d50a934c05f874c3bacddf3`

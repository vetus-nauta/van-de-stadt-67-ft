# M09 — вспомогательные системы, исследование 15.09.2026

Статус: открытые розничные предложения на компоненты. Не персональные КП, не выбранное оборудование и не полная стоимость работоспособных систем. Все цены проверены открытием карточек; дата просмотра не является датой выпуска прайса. Доставка, монтаж, расходные материалы, наладка и налоговый режим покупателя не включены автоматически.

Сопоставление идёт по полезному результату, а не по одинаковому названию или номиналу. Расходы и напоры помп, баланс вентиляции, защищаемый объём, число танков и тепловая нагрузка остаются открытыми. Все provisional_qty = null: M01 не фиксирует физические количества этих вспомогательных компонентов. Исследовательское количество при сведении должно быть явно отделено от требований владельца. Основные количества двигателя, генераторов и аккумуляторов не менялись.

| ID | ME | Компонент / источник | Цена источника, EUR | Налог | NET единицы, EUR |
|---|---|---|---:|---|---:|
| AX01 | ME20 | [Rule 2000 / 24 V](https://www.svb24.com/en/rule-heavy-duty-bilge-pump-2000-24v.html) | 153.36 | excl; ставка не установлена | 153.36 |
| AX02 | ME20 | [Whale Gusher Urchin BP9005](https://www.svb24.com/en/whale-gusher-urchin-manual-bilge-pump-type-bp-9005.html) | 89.87 | excl; ставка не установлена | 89.87 |
| AX03 | ME20 | [Whale Gusher 30 / surface mounting](https://www.svb24.com/en/whale-gusher-30-manual-bilge-pump-surface-mounting.html) | 783.15 | excl; ставка не установлена | 783.15 |
| AX04 | ME22 | [Ocean Technologies blower / 24 V / 1000 m³/h](https://www.svb24.com/en/ocean-technologies-engine-compartment-blower-24-v-1000-m3-hour-150-mm-flex-mount.html) | 189.87 | excl; ставка не установлена | 189.87 |
| AX05 | ME23 | [Marco UP3 Oil Change Pump / 24 V](https://www.svb24.com/en/marco-up3-electric-oil-change-pump.html) | 168.03 | excl; ставка не установлена | 168.03 |
| AX06 | ME25 | [Jabsco Type 12GPM waste water pump / 24 V](https://www.svb24.com/en/jabsco-type-12gpm-waste-water-pump-24v.html) | 210.04 | excl; ставка не установлена | 210.04 |
| AX07 | ME20 | [Rule-A-Matic Plus float switch](https://www.svb24.com/en/rule-rule-a-matic-plus-automatic-float-switch.html) | 54.58 | excl; ставка не установлена | 54.58 |
| AX08 | ME20 | [Johnson Bilge Alert / 24 V](https://www.svb24.com/en/johnson-pump-bilge-alert-high-water-alarm-with-ultima-switch.html) | 97.44 | excl; ставка не установлена | 97.44 |
| AX09 | ME24 | [KUS Water/Fuel Sensor / 150 mm](https://www.svb24.com/en/kus-water-fuel-sensor.html) | 25.17 | excl; ставка не установлена | 25.17 |
| AX10 | ME21 | [Fireboy MA / 13.4 kg / 15.6 m³](https://www.nauticabasile.it/eng/osculati/fixed-fireboy-fire-extinguishers-with-clean-agent-and-manualautomatic-activation-46870/31.620.55/) | 2332.10 | incl; ставка не установлена | — |
| AX11 | ME21 | [Fireboy ESC shutdown / 8 circuits](https://www.nauticabasile.it/eng/osculati/fireboy-esc-series-automatic-engine-shutdown-systems-46872/?listRef=related) | 586.40 | incl; ставка не установлена | — |
| AX12 | ME26 | [Webasto Thermo Pro 90 Marine / 24 V](https://www.svb24.com/en/webasto-thermo-pro-90-marine-diesel-water-heater-24-v-9-1-kw.html) | 2260.46 | excl; ставка не установлена | 2260.46 |
| AX13 | ME26 | [Webasto Thermo Pro 90 Marine Std / 24 V](https://standheizung-ersatzteile.com/thermo-pro-90-24v-marine-std) | 2405.71 | incl; 19 | 2021.61 |
| AX14 | ME21 | [Fireboy MA / 26.8 kg / 31.1 m³](https://www.nauticabasile.it/eng/osculati/fixed-fireboy-fire-extinguishers-with-clean-agent-and-manualautomatic-activation-46870/31.610.31/) | 4251.10 | incl; ставка не установлена | — |
| AX15 | ME22 | [Ocean Technologies blower / 24 V / 550 m³/h](https://www.svb24.com/en/ocean-technologies-engine-compartment-blower-24-v-550-m3-hour-100-mm-hose-connection.html) | 129.37 | excl; ставка не установлена | 129.37 |
| AX16 | ME25 | [Johnson TA3P10-19 Macerator / 24 V](https://www.svb24.com/en/johnson-pump-ta3p10-19-macerator-pump-24v.html) | 193.24 | excl; ставка не установлена | 193.24 |

NET SVB опубликован прямо: source_tax_basis=excl, ставка null. Это не нулевая ставка поставки. Для ImpEK опубликована цена с налогом; 19% подтверждены [FAQ продавца](https://standheizung-ersatzteile.com/shop/en/faq), расчёт 2405.71 / 1.19 с округлением до цента. Для Nautica Basile [условия L.8](https://www.nauticabasile.it/eng/pages/sales-conditions/) говорят о включении VAT, но не называют ставку: NET не восстановлен догадкой по стране. Налог доставки в Польшу отдельно согласуется.

Границы и антидубли:

- ME20: AX01 — электрическая помпа; AX02 и AX03 — альтернативы ручной функции, не две обязательные установки. AX07 — включение по уровню; AX08 — отдельный высокий уровень/сигнализация. Эти позиции не заменяют многозонный щит, независимое питание, трубопроводы и приёмку. BP9005 не назначен главным аварийным средством яхты.
- ME21: AX10 сохраняет ценовой ориентир прежнего SKU M07. Его 15.6 м³ недостаточно просто объявить всей МО; 51 м³ на сайте относится к серии. AX14 на 31.1 м³ — другой типоразмер для исследования, без утверждения достаточности для G03. Баллон нельзя выбрать только сравнением приблизительного объёма 14.08 × 2.1 ≈ 29.6 м³. AX11 добавляет отдельную функцию аварийного останова; трос, исполнительные клапаны и противопожарное перекрытие вентиляции остаются вне цены. 24 V конкретного shutdown SKU нужно подтвердить.
- ME22: AX04 и AX15 — альтернативные типоразмеры, не готовая вентиляционная установка. Суммарные воздух/тепло от трёх дизелей, сопротивление трасс, шум и пожарная блокировка ещё не рассчитаны.
- ME23: AX05 включает короткие трубки, но не стационарную маслосменную сеть трёх дизелей/редуктора. Не дублировать агрегатные насосы, если они войдут в поставку производителя.
- ME24: AX09 — один пассивный резистивный датчик, а не вся автоматика танков. Длина 150 мм — только точный ценовой вариант, не проектная глубина танка. Нужны индикатор/вход, схема питания и калибровка каждого танка.
- ME25: AX06 и AX16 альтернативны. Проверить, не входит ли перекачивающий насос в пакет санитарной системы; цену не прибавлять дважды.
- ME26: AX12 и AX13 — один Webasto SKU у двух продавцов. Это опция, не второй обязательный источник отопления и не второй бойлер. Состав Marine packing list сравнить; распределение тепла и монтаж остаются открытыми.

Поиск и отсеянные варианты: SVB Rule 2000 24V / Whale Gusher / Bilge Alert; Fireboy MA EU и карточки Nautica Basile; SVB Ocean blower; Marco UP3 oil; KUS/SENSORA/Simarine; Jabsco/Johnson macerator; Webasto Thermo Pro 90 Marine у SVB, ImpEK и других EU продавцов. Для пожаротушения SVB переносной/малый автоматический огнетушитель не принят вместо объёмной защиты МО. Simarine STR1 найден за 67.18 NET, но карточка указывает 12 V — исключён из offers, поскольку бортовая сеть только 24 V. [Карточка STR1](https://www.svb24.com/en/p/simarine-radar-tank-sensor-0-190-ohm-240-33-ohm-0-5-v-output-bluetooth.html). Marco UP3-R не принят как маслосменный: продавец исключает масло. Старые снятые с продажи macerator и ультразвуковые комплекты не перенесены.

Контроль точных вариантов: UP3 24 V = 168.03, не базовые 166.34 для 12 V; Bilge Alert 24 V = 97.44, не 92.40 для 12 V. У ImpEK открытая цена 2405.71 отличается от поисковых 2349.30: использована открытая. Наличие в SVB меняется между просмотрами, старые ожидаемые даты не трактуются как гарантия наличия.

Полные сторонние страницы в публичный выпуск не копировались. Реестр хранит фактические данные и прямые ссылки. Поставщикам сообщения не отправлялись.

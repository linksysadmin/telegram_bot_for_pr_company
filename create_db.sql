
CREATE TABLE partners (
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    id BIGINT PRIMARY KEY,
    name VARCHAR(255),
    tg_username VARCHAR(255),
    phone VARCHAR(50),
    company TEXT,
    website TEXT,
    documents BOOLEAN DEFAULT FALSE,
    status VARCHAR(255) DEFAULT 'registered'
);

CREATE TABLE employees (
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    id BIGINT PRIMARY KEY,
    name VARCHAR(255),
    operator BOOLEAN,
    manager BOOLEAN
);

CREATE TABLE clients (
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    id BIGINT PRIMARY KEY,
    name VARCHAR(255),
    tg_username VARCHAR(255),
    phone VARCHAR(50),
    company TEXT,
    website TEXT,
    documents BOOLEAN DEFAULT FALSE,
    status VARCHAR(255) DEFAULT 'registered'
);


CREATE TABLE questions (
    id INT AUTO_INCREMENT PRIMARY KEY NOT NULL,
    direction VARCHAR(255),
    sub_direction VARCHAR(255) DEFAULT NULL,
    section_name VARCHAR(50),
    question_number INT,
    question_text TEXT,
    informal_question TEXT,
    answer TEXT DEFAULT NULL,
    UNIQUE KEY idx_question (direction, sub_direction, section_name, question_number)
);


CREATE TABLE clients_briefings (
    id INT AUTO_INCREMENT PRIMARY KEY,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    user_id BIGINT NOT NULL,
    question_id INT NOT NULL,
    user_response TEXT,
    UNIQUE KEY idx_client_question (user_id, question_id),
    FOREIGN KEY(question_id) REFERENCES questions(id)
);



CREATE INDEX clients_briefings_index ON clients_briefings(user_id);


INSERT INTO questions (direction, sub_direction, section_name, question_number, question_text, informal_question, answer)
VALUES
    ('Маркетинг', NULL, 'Стратегия', 1, 'Цель вашего проекта', 'Цель', 'Увеличить продажи| Снизить затраты| Улучшить сервис'),
    ('Маркетинг', NULL, 'Стратегия', 2, 'Ключевые задачи', 'Ключевые задачи', 'Разработать новые продукты| Увеличить узнаваемость| Расширить каналы распространения'),
    ('Маркетинг', NULL, 'Стратегия', 3, 'Срок реализации проекта', 'Срок реализации', '6 месяцев| 12 месяцев| 18 месяцев'),
    ('Маркетинг', NULL, 'Стратегия', 4, 'Бюджет', 'Бюджет', '500 000 руб.| 850 000 руб.| 1 200 000 руб.'),
    ('Маркетинг', NULL, 'Стратегия', 5, 'Какие демографические характеристики у аудитории', 'Демографические данные', 'Пол| Возраст| Доход| Интересы'),
    ('Маркетинг', NULL, 'Стратегия', 6, 'Какие ключевые факторы влияют на покупку', 'Факторы, влиюяющие на покупку', 'Цена| Качество| Узнаваемость бренда| Удобство использования'),
    ('Маркетинг', NULL, 'Стратегия', 7, 'Кто главные конкуренты', 'Конкуренты', NULL),
    ('Маркетинг', NULL, 'Стратегия', 8, 'Сильные и слабые стороны конкурентов|Положительные|Отрицательные', 'Сильные и слабые стороны конкурентов', NULL),
    ('Маркетинг', NULL, 'Стратегия', 9, 'Как целевая аудитория воспринимает бренд компании', 'Восприятие бренда у целевой аудитории', 'Положительно| Отрицательно| Нейтрально'),
    ('Маркетинг', NULL, 'Стратегия', 10, 'Какова эффективность текущей маркетинговой стратегии', 'Эффективность текущей маркетинговой стратегии', 'Очень эффективна| Умеренно эффективна| Неэффективна'),
    ('Маркетинг', NULL, 'Стратегия', 11, 'Какие маркетинговые каналы наиболее эффективны сейчас', 'Наиболее эффективные маркетинговые инструменты', NULL),
    ('Маркетинг', NULL, 'Стратегия', 12, 'Какие способы привлечения наиболее эффективны сейчас', 'Эффективные способы привлечения', 'Скидки и специальные предложения| Рекламные кампании на новых рынках| Рекомендации от клиентов'),
    ('Маркетинг', NULL, 'Стратегия', 13, 'Какие основные вызовы стоят перед компанией', 'Основные вызовы', 'Высокая конкуренция| Низкая лояльность клиентов| Большие расходы на маркетинг| Быстро меняющиеся требования рынка'),


    ('Маркетинг', NULL, 'Исследования', 1, 'Цель маркетингового исследования?', 'Цель маркетингового исследования', 'Определить потребности и предпочтения целевой аудитории| Изучить конкурентов и рыночную среду| Оценить эффективность маркетинговых кампаний'),
    ('Маркетинг', NULL, 'Исследования', 2, 'Какие показатели необходимы', 'Необходимые показатели', 'Опросы и анкетирование| Фокус-группы и глубинные интервью| Анализ данных и статистика| Наблюдение и эксперименты'),
    ('Маркетинг', NULL, 'Исследования', 3, 'Какой объем выборки требуется для исследования', 'Объем выборки', 'Маленькая (до 100 человек)| Средняя (100-500 человек)| Большая (более 500 человек)'),
    ('Маркетинг', NULL, 'Исследования', 4, 'Какой географический охват исследования необходим', 'Географический охват', 'Локальный| Региональный| Национальный| Международный'),
    ('Маркетинг', NULL, 'Исследования', 5, 'Какую информацию вы хотели бы получить от исследования', 'Необходимые данные', 'Демографические данные| Поведенческие характеристики| Мнения и отзывы клиентов| Информацию о конкурентах'),
    ('Маркетинг', NULL, 'Исследования', 6, 'Какой бюджет вы готовы выделить', 'Бюджет', '100 000 руб.| 500 000 руб.| 1 500 000 руб.'),
    ('Маркетинг', NULL, 'Исследования', 7, 'Какие сроки выполнения проекта вам необходимы?', 'Сроки исследования', 'Меньше месяца| 1-3 месяца| Более 3 месяцев'),
    ('Маркетинг', NULL, 'Исследования', 8, 'Какие особенности исследования необходимо учесть', 'Особенности', 'Онлайн-исследования| Исследования в офлайн-среде| Учет мобильной аудитории'),
    ('Маркетинг', NULL, 'Исследования', 9, 'Какую форму предпочитаете для представления результатов исследования', 'Форма предоставления результатов', 'Письменный отчет| Презентация с визуализацией данных| Интерактивная дашборд-панель'),
    ('Маркетинг', NULL, 'Исследования', 10, 'Какой будет дальнейший шаг после получения результатов исследования', 'Дальнейший шаг', 'Разработка маркетинговой стратегии| Улучшение продукта/услуги| Анализ конкурентов| Планирование маркетинговых кампаний'),


    ('Маркетинг', NULL, 'Подписка', 1, 'Основная цель вашей стратегии', 'Основная цель стратеги', 'Увеличение узнаваемости бренда и осведомленности о продукте/услуге| Привлечение новых клиентов и расширение клиентской базы| Удержание существующих клиентов и повышение их лояльности| Увеличение объемов продаж и прибыли'),
    ('Маркетинг', NULL, 'Подписка', 2, 'Какие каналы маркетинга вы предпочитаете использовать', 'Используемые каналы маркетинга', 'Реклама (телевидение,радио,печатные издания)| Цифровой маркетинг(социальные сети,поисковая оптимизация,контент-маркетинг)| Событийный маркетинг (мероприятия,ярмарки,конференции)| Прямой маркетинг (личные встречи, телефонные звонки, электронная почта)'),
    ('Маркетинг', NULL, 'Подписка', 3, 'Какую аудиторию вы хотите охватить своим проектом', 'Аудитория', 'Молодежь (18-34 лет)| Взрослые (35-54 лет)| Пожилые люди (55+ лет)| Бизнес-сектор'),
    ('Маркетинг', NULL, 'Подписка', 4, 'Какой бюджет вы готовы выделить на комплексный маркетинг', 'Бюджет', '400 000 руб.| 1 000 000 руб.| 2 000 000 руб.| 5 000 000 руб.'),
    ('Маркетинг', NULL, 'Подписка', 5, 'Какие ключевые показатели успеха вы хотели бы отслеживать', 'KPI', 'Увеличение трафика на веб-сайте| Повышение конверсии и продаж| Рост уровня узнаваемости бренда| Улучшение показателей лояльности клиентов'),
    ('Маркетинг', NULL, 'Подписка', 6, 'Какой географический охват вашего проекта', 'География проекта', 'Локальный (небольшая территория)| Региональный (несколько городов/регионов)| Национальный| Международный'),
    ('Маркетинг', NULL, 'Подписка', 7, 'Какой временной горизонт вы намечаете для реализации проекта комплексного маркетинга', 'Сроки реализации проекта', 'Краткосрочный (до 3 месяцев)| Среднесрочный (3-6 месяцев)| Долгосрочный (более 6 месяцев)'),
    ('Маркетинг', NULL, 'Подписка', 8, 'Какие инструменты и методы вы планируете использовать для измерения эффективности проекта', 'Инструменты оценки KPI', 'Аналитика веб-сайта и отслеживание конверсий| Опросы и исследования мнений клиентов| Анализ социальных медиа и метрик вовлеченности| Сравнение показателей до и после внедрения проекта'),
    ('Маркетинг', NULL, 'Подписка', 9, 'Какие особенности вашей отрасли или рынка необходимо учесть при разработке проекта', 'Особенности', 'Сезонность и цикличность спроса| Особенности поведения и предпочтений целевой аудитории| Конкурентная среда и уровень конкуренции| Технические или регуляторные ограничения'),


    ('Креатив', NULL, 'Концепция', 1, 'Какой тип проекта требует креативной концепции', 'Тип проекта', 'Рекламная кампания| Брендинг или ребрендинг| Промо-акция или специальное мероприятие| Веб-дизайн или разработка приложения'),
    ('Креатив', NULL, 'Концепция', 2, 'Цель проекта', 'Цель проекта', 'Привлечение новых клиентов или аудитории| Улучшение узнаваемости бренда| Повышение продаж или конверсии| Создание уникального пользовательского опыта'),
    ('Креатив', NULL, 'Концепция', 3, 'Какая целевая аудитория должна быть заинтересована в продукте', 'Целевая аудитория', 'Молодежь и миллениалы| Профессионалы и бизнес-сектор| Семейная аудитория| Технически подкованные пользователи'),
    ('Креатив', NULL, 'Концепция', 4, 'Основное сообщение или идея, которую вы хотите передать через креатив', 'Основное сообщение', 'Инновация и современность| Качество и надежность| Креативность и уникальность| Удобство и функциональность'),
    ('Креатив', NULL, 'Концепция', 5, 'Какой стиль или настроение вы предпочитаете', 'Стиль и настроение', 'Стильный и минималистичный| Яркий и энергичный| Элегантный и роскошный| Природный и экологичный'),
    ('Креатив', NULL, 'Концепция', 6, 'Какими цветами или цветовыми схемами вы хотели бы работать', 'Цветовая схема', 'Яркие и насыщенные цвета| Пастельные и нежные оттенки| Контрастные и играющие на противопоставлении| Естественные и природные тона'),
    ('Креатив', NULL, 'Концепция', 7, 'Какие визуальные элементы или идеи вы хотели бы использовать в проекте', 'Визуальные элементы', 'Геометрические фигуры и линии| Фотографии или изображения| Текстуры и паттерны| Иллюстрации или арт-элементы'),
    ('Креатив', NULL, 'Концепция', 8, 'Какие слова или фразы наилучшим образом описывают вашу желаемую концепцию', 'Ключевые фразы', 'Инновационный, смелый, экспериментальный| Игривый, нестандартный, удивительный| Элегантный, стильный, роскошный| Простой, понятный, функциональный'),
    ('Креатив', NULL, 'Концепция', 9, 'Какой будет дальнейший шаг после завершения проекта', 'Дальнейший шаг', 'Оценка результатов и обратная связь| Проведение анализа эффективности проекта| Реализация и запуск проекта| Дальнейшее развитие и модификация концепции'),
    ('Креатив', NULL, 'Концепция', 10, 'Какой бюджет вы выделяете на создание креативной концепции', 'Бюджет', 'Минимальный| Средний| Высокий| Не знаю/не уверен'),


    ('Креатив', NULL, 'Контент', 1, 'Какой тип контента вы планируете создать', 'Тип контента', 'Статьи или блоги| Видео| Изображения или графика| Социальные медиа посты| Аудио или подкасты'),
    ('Креатив', NULL, 'Контент', 2, 'Какая целевая аудитория должна быть заинтересована в контенте', 'Целевая аудитория', 'Молодежь и миллениалы| Профессионалы и бизнес-сектор| Семейная аудитория| Технически подкованные пользователи'),
    ('Креатив', NULL, 'Контент', 3, 'Какую информацию или сообщение вы хотите передать через контент', 'Сообщение целевой аудитории', 'Образовательная информация или экспертное мнение| Вдохновение и мотивация, Развлечение и юмор| Продвижение продукта или услуги'),
    ('Креатив', NULL, 'Контент', 4, 'Основной формат контента', 'Формат', 'Текстовый контент| Визуальный контент(изображения,графика)| Аудио-контент (подкасты,аудиозаписи)| Видео-контент'),
    ('Креатив', NULL, 'Контент', 5, 'Какой стиль или настроение контента вы хотите создать', 'Стиль', 'Серьезный и профессиональный| Позитивный и веселый| Эмоциональный и вдохновляющий| Минималистичный и современный'),
    ('Креатив', NULL, 'Контент', 6, 'Какими цветами или цветовыми схемами вы хотели бы использовать', 'Цветовая схема', 'Яркие и насыщенные цвета| Пастельные и нежные оттенки| Контрастные и играющие на противопоставлении| Естественные и природные тона'),
    ('Креатив', NULL, 'Контент', 7, 'Какие визуальные элементы или стили использовать в контенте', 'Визуальные элементы', 'Геометрические фигуры и линии| Фотографии или изображения| Иллюстрации или арт-элементы| Текстуры и паттерны'),
    ('Креатив', NULL, 'Контент', 8, 'Какие ключевые сообщения или фразы вы хотели бы включить в контент', 'Ключевые фразы', 'Цитаты и мотивирующие высказывания| Уникальные продажные предложения (USP)| Описания продукта или услуги| Позывные к действию (Call-to-action)'),
    ('Креатив', NULL, 'Контент', 9, 'Какая платформа или канал распространения контента планируется', 'Платформа для  публикации', 'Сайт или блог| Социальные сети| YouTube или видеохостинги| Подкастинговые платформы, Email-рассылки'),
    ('Креатив', NULL, 'Контент', 10, 'Каким будет дальнейший шаг после создания контента', 'Дальнейший шаг', 'Распространение и продвижение контента| Оценка результатов и анализ эффективности| Модификация или обновление контента| Планирование и создание следующего контент-проекта'),


    ('Креатив', NULL, 'Фирменный стиль', 1, 'Какая отрасль вашего бизнеса', 'Отрасль бизнеса', 'Розничная торговля| Финансовые услуги| Технологии и информационные технологии| Здравоохранение и медицина| Пищевая промышленность'),
    ('Креатив', NULL, 'Фирменный стиль', 2, 'Цель создания фирменного стиля', 'Цель создания фирменного стиля', 'Улучшение узнаваемости бренда| Создание профессионального образа компании| Повышение доверия и авторитетности| Привлечение новых клиентов или аудитории'),
    ('Креатив', NULL, 'Фирменный стиль', 3, 'Целевая аудитория которая должна быть заинтересована в вашем бренде', 'Целевая аудитория', 'Молодежь и миллениалы| Профессионалы и бизнес-сектор| Семейная аудитория| Технически подкованные пользователи'),
    ('Креатив', NULL, 'Фирменный стиль', 4, 'Какие слова или фразы наилучшим образом описывают ваш бренд', 'Слова и фразы, опмсывающие бренд', 'Инновационный, современный, передовой| Элегантный, стильный, роскошный| Природный, экологически чистый, органический| Профессиональный, надежный, качественный'),
    ('Креатив', NULL, 'Фирменный стиль', 5, 'Какими цветами или цветовыми схемы вы хотели бы отразить в фирменном стиле', 'Цветовая схема', 'Яркие и насыщенные цвета| Пастельные и нежные оттенки| Классические и элегантные комбинации| Естественные и природные тона'),
    ('Креатив', NULL, 'Фирменный стиль', 6, 'Какие визуальные элементы или символы вы хотели бы включить в фирменный стиль', 'Визуальные элементы', 'Логотип и фирменное слово| Иконки и графические элементы| Шрифты и типографика| Текстуры и паттерны'),
    ('Креатив', NULL, 'Фирменный стиль', 7, 'Каким будет стиль общения и тональность вашего бренда', 'Стиль', 'Формальный и профессиональный| Дружелюбный и неформальный| Информативный и экспертный| Игривый и креативный'),
    ('Креатив', NULL, 'Фирменный стиль', 8, 'Какие ключевые сообщения или ценности вашего бренда вы хотели бы выразить через фирменный стиль', 'Ключевые сообщения', 'Инновация и передовые технологии| Качество и надежность| Удобство и функциональность| Экологическая ответственность'),
    ('Креатив', NULL, 'Фирменный стиль', 9, 'Где будет использование фирменного стиля', 'Использование фирменного стиля', 'Веб-сайт и онлайн-присутствие| Принтовые материалы и упаковка| Социальные медиа и реклама| Фирменная атрибутика и выставочные стенды'),
    ('Креатив', NULL, 'Фирменный стиль', 10, 'Какой бюджет, который вы выделяете на создание фирменного стиля', 'Бюджет', '100 000 руб.| 400 000 руб.| 1 000 000 руб.'),


    ('Креатив', NULL, 'Медиапланирование', 1, 'Какая цель вашей рекламной кампании', 'Цель рекламной кампании', 'Увеличение узнаваемости бренда| Привлечение новых клиентов| Увеличение продаж и конверсии| Повышение осведомленности о продукте или услуге'),
    ('Креатив', NULL, 'Медиапланирование', 2, 'Какая целевая аудитория должна быть заинтересована в вашей рекламе', 'Целевая аудитория', 'Молодежь и миллениалы| Профессионалы и бизнес-сектор| Семейная аудитория| Технически подкованные пользователи'),
    ('Креатив', NULL, 'Медиапланирование', 3, 'Какие каналы или платформы вы планируете использовать для размещения рекламы', 'Каналы распространения', 'Телевидение| Радио| Пресса и журналы| Интернет (веб-сайты, социальные сети, поисковая реклама)| Открытые рекламные пространства (билборды, автобусы и т.д.)'),
    ('Креатив', NULL, 'Медиапланирование', 4, 'Какой географический охват должна иметь ваша рекламная кампания', 'Географический охват', 'Локальный (один город или регион)| Национальный| Международный'),
    ('Креатив', NULL, 'Медиапланирование', 5, 'Какие временные рамки у вас для рекламной кампании', 'Объем', 'Краткосрочная (несколько недель или месяцев)| Долгосрочная (несколько месяцев или годы)| Постоянная реклама'),
    ('Креатив', NULL, 'Медиапланирование', 6, 'Какой бюджет вы выделяете на рекламную кампанию', 'Бюджет', 'Минимальный| Средний| Высокий'),
    ('Креатив', NULL, 'Медиапланирование', 7, 'Какой формат рекламы вы планируете использовать', 'Формат рекламы', 'Текстовые объявления| Видеореклама| Графические объявления| Реклама с использованием баннеров'),
    ('Креатив', NULL, 'Медиапланирование', 8, 'Какой будет ключевое сообщение или продающее предложение вашей рекламы', 'Ключевое сообщение', NULL),
    ('Креатив', NULL, 'Медиапланирование', 9, 'Какую метрику или ключевой показатель производительности (KPI) вы хотите использовать для измерения успеха рекламной кампании', 'KPI', 'Количество просмотров или прослушиваний| Количество кликов или переходов| Конверсионная воронка (покупки,регистрации и т.д.)| Уровень осведомленности о бренде'),
    ('Креатив', NULL, 'Медиапланирование', 10, 'Какой у вас есть срок для запуска рекламной кампании', 'Сроки реализации', NULL),
    ('Креатив', NULL, 'Медиапланирование', 11, 'Какие конкуренты у вас есть в данной нише и какие медиаканалы они используют', 'Конкуренты', NULL),
    ('Креатив', NULL, 'Медиапланирование', 12, 'Какие ограничения или требования вам необходимо учесть при размещении рекламы', 'Ограничения и требования', NULL),


    ('Студия', 'ВЕБ', 'Сайты', 1, 'Тип сайта', 'Тип сайта', 'Интернет-магазин (продажа товаров и/или услуги с заказом и оплатой товаров)| Сайт-портфолио| Лендинг (одностраничный сайт)| Сайт-визитка (общая информация о компании и ее координаты)| Корпоративный сайт (подробная информация о компании. Каталог товаров и/или услуг, без возможности оформления заказов на сайте)|  С каталогом| Без каталога'),
    ('Студия', 'ВЕБ', 'Сайты', 2, 'Цели и задачи сайта', 'Цели и задачи', 'Привлечение клиентов| Привлечение читателей (для сайта СМИ)| Повышение узнаваемости компании, улучшение имиджа| Увеличение объема продаж| Информирование о проведении акций| Информирование о товарах и услугах| Информирование о компании| Размещение новостей компании'),
    ('Студия', 'ВЕБ', 'Сайты', 3, 'Структура сайта. Укажите основные разделы сайта. Пример: «О компании», «Каталог», «Новости» и т.д.', 'Структура', ' Разделы сайта, меню (меню, подменю и т.д.)| Блоки и элементы, присутствующие на главной странице'),
    ('Студия', 'ВЕБ', 'Сайты', 4, 'Модули сайта', 'Модули сайта', 'Поиск по сайту| Информационные блоки| Веб-формы| Форумы| Блоги| Фотогалерея/портфолио| Защита форм картинкой(captcha)| Реклама (управление баннерами)'),
    ('Студия', 'ВЕБ', 'Сайты', 5, 'Сервисы для связи с посетителями сайта', 'Сервисы для связи с посетителями', 'Форма обратной связи| Форма обратного звонка| Вопрос-ответ| Голосования(опросы)| Отзывы| Комментарии| Техподдержка(онлайн-консультации)| Системы онлайн-бронирования| Формы подписки и email-рассылки| Регистрация пользователей| Личный кабинет| Оповещения по SMS'),
    ('Студия', 'ВЕБ', 'Сайты', 6, 'Сервисы по продаже через интернет', 'Сервисы по продаже услуг через Интернет', 'Рубрикатор товаров/услуг| Поиск по каталогу| Поиск по каталогу товаров и услуг с заданием параметров(расширенный поиск/фильтрация товаров)| Расширенное описание категорий или товаров| Добавление товаров в избранное| Запрос цены по отдельным позициям| Сравнение товаров| Корзина| Расчет скидок| Расчет стоимости доставки| История заказов пользователя| Уведомление клиентов о статусе заказов| Оплата онлайн| Автоматическое формирование счета для оплаты'),
    ('Студия', 'ВЕБ', 'Сайты', 7, 'Языковые версии сайта', 'Языковые версии', 'Русский| Английский| Поддержка многоязычности'),
    ('Студия', 'ВЕБ', 'Сайты', 8, 'Технические требования к сайту: Ориентирование на размер экрана (Смартфоны)', 'Ориентирование на размер экрана (Смартфоны)', '14”| 15”| 17”| 19”| 21”| Больше 21”| Не важно/неизвестно'),
    ('Студия', 'ВЕБ', 'Сайты', 9, 'Технические требования к сайту: Разрешение экрана', 'Разрешение экрана', '320px| 480px| 768px| 1000px| 1280px| Не важно/неизвестно'),
    ('Студия', 'ВЕБ', 'Сайты', 10, 'Технические требования к сайту: Технические параметры хостинга', 'Технические параметры хостинга', NULL),
    ('Студия', 'ВЕБ', 'Сайты', 11, 'Технические требования к сайту: Система управления сайтом', 'Система управления сайтом', 'Bitrix24| Wordpress| OpenCart| Tilda'),
    ('Студия', 'ВЕБ', 'Сайты', 12, 'Технические требования к сайту: Интеграции со сторонними сервисами и программами', 'Интеграции со сторонними сервисами и программами', 'Импорт прайса из Excel| Интеграция с 1С| Интеграция с корпоративной базой данных| Яндекс.Маркет| Фарпост'),
    ('Студия', 'ВЕБ', 'Сайты', 13, 'Технические требования к сайту: Нужна ли мобильная версия сайта или адаптивный дизайн', 'Нужна ли мобильная версия сайта или адаптивный дизайн', 'Нет| Нужна мобильная версия сайта| Адаптивный дизайн'),


    ('Студия', 'Звук', 'Рекламные ролики', 1, 'Какой у вас проект в студии звукозаписи', 'Проект', 'Запись и продакшн музыкальных треков| Запись и сведение аудиокниг или подкастов| Создание звуковых эффектов для фильмов или игр| Разработка рекламных аудиоматериалов'),
    ('Студия', 'Звук', 'Рекламные ролики', 2, 'Какие услуги в студии звукозаписи вам необходимы', 'Необходимые услуги', 'Запись вокала и инструментов| Сведение и мастеринг аудиоматериалов| Создание музыкальных аранжировок и композиций| Работа со звуковыми эффектами и сэмплами'),
    ('Студия', 'Звук', 'Рекламные ролики', 3, 'Какой жанр музыки или аудиоматериала вы планируете записывать', 'Жанр', 'Поп-музыка| Рок и альтернатива| Электронная музыка| Джаз и блюз| Классическая музыка'),
    ('Студия', 'Звук', 'Рекламные ролики', 4, 'Каков размер вашего проекта в студии звукозаписи', 'Объем', 'Одиночный трек или проект небольшого объема| EP или мини-альбом (3-6 треков)| Полноформатный альбом (более 10 треков)'),
    ('Студия', 'Звук', 'Рекламные ролики', 5, 'Какие дополнительные услуги или возможности  вам важны', 'Дополнительные услуги', 'Аренда инструментов и оборудования| Написание текстов и аранжировка композиций| Использование вокального буфера или бэк-вокала| Аудиореставрация и улучшение качества звука'),
    ('Студия', 'Звук', 'Рекламные ролики', 6, 'Какую атмосферу или звуковую концепцию вы хотели бы создать в вашем проекте студии звукозаписи', 'Концепция', 'Мощный и энергичный звук| Интимный и эмоциональный звук| Пространственный и погружающий звук| Классический и органичный звук'),
    ('Студия', 'Звук', 'Рекламные ролики', 7, 'Какой бюджет вы планируете выделить на проект', 'Бюджет', 'Минимальный бюджет| Средний бюджет| Высокий бюджет| Не знаю/не уверен'),
    ('Студия', 'Звук', 'Рекламные ролики', 8, 'Какой временной горизонт вы намечаете для реализации', 'Сроки реализации', 'Краткосрочный(до 2-x недель)| Среднесрочный(1-3 месяца)| Долгосрочный(более 3 месяцев)'),
    ('Студия', 'Звук', 'Рекламные ролики', 9, 'Какие форматы и доставки аудиофайлов вам необходимы для вашего проекта в студии звукозаписи', 'Формат', 'WAV или AIFF (без сжатия)| MP3 или AAC (сжатие с потерями)| FLAC или ALAC (сжатие без потерь)'),
    ('Студия', 'Звук', 'Рекламные ролики', 10, 'Каким будет дальнейший шаг после завершения проекта в студии звукозаписи', 'Дальнейший шаг', 'Релиз и распространение аудиоматериала| Продвижение и маркетинг вашей музыки или аудиоматериала| Проведение живых выступлений или концертов| Работа над следующим проектом в студии звукозаписи'),


    ('Студия', 'Видео', 'Видеоролик', 1, 'Цель вашего проекта', 'Основная цель', 'Создание корпоративных видео для бизнеса| Производство музыкальных видеоклипов| Съемка и монтаж рекламных видеороликов| Производство видеоконтента для социальных медиа'),
    ('Студия', 'Видео', 'Видеоролик', 2, 'Какие услуги вам необходимы', 'Услуги', 'Сценарий и концепция видео| Съемка и освещение| Звуковое оформление и монтаж| Визуальные эффекты и анимация'),
    ('Студия', 'Видео', 'Видеоролик', 3, 'Какой формат видео вы планируете создавать', 'Формат', 'Короткометражные фильмы| Рекламные ролики| Информационные видео| Анимационные видео'),
    ('Студия', 'Видео', 'Видеоролик', 4, 'Какую аудиторию вы хотите охватить вашим видео контентом', 'Аудитория', 'Потребители (конечные пользователи)| Бизнес-клиенты и предприятия| Образовательные учреждения и студенты| Организации и некоммерческие организации'),
    ('Студия', 'Видео', 'Видеоролик', 5, 'Какой стиль и эстетика видео вы предпочитаете', 'Стиль', 'Классический и профессиональный| Креативный и нестандартный| Минималистический и современный| Ретро и винтажный'),
    ('Студия', 'Видео', 'Видеоролик', 6, 'Какую продолжительность видео вы планируете создавать', 'Продолжительность', 'Короткие видео (до 1 минуты)| Средняя продолжительность (1-5 минут)| Длинные видео (более 5 минут)| Варьируется в зависимости от проекта'),
    ('Студия', 'Видео', 'Видеоролик', 7, 'Каким будет дальнейший шаг после завершения проекта видео студии?', 'Дальнейший шаг', 'Публикация и распространение видео контента| Продвижение видео через социальные медиа и маркетинг| Использование видео на веб-сайте или платформе| Создание следующего видео проекта'),


    ('Студия', 'Дизайн', 'Проект дизайна', 1, 'Какая цель вашего проекта дизайна', 'Цель дизайн проекта', 'Создание логотипа и брендинга| Разработка веб-дизайна и пользовательского интерфейса| Дизайн упаковки и продуктового дизайна| Графический дизайн для печатных материалов (брошюры, флаера и т.д.)'),
    ('Студия', 'Дизайн', 'Проект дизайна', 2, 'Какой тип продукта или услуги требует дизайна', 'Тип продукта', 'Розничные товары| Промышленные товары| Услуги и консалтинг| Веб-приложения и онлайн-платформы'),
    ('Студия', 'Дизайн', 'Проект дизайна', 3, 'Какова целевая аудитория вашего продукта или услуги', 'Целевая аудитория', 'Дети и подростки| Взрослые (18-35 лет)| Взрослые (35+ лет)| Бизнес-сектор и профессионалы'),
    ('Студия', 'Дизайн', 'Проект дизайна', 4, 'Какой стиль дизайна вы предпочитаете', 'Стиль', 'Минимализм и современный стиль| Классический и элегантный стиль| Игривый и креативный стиль| Природный и экологичный стиль'),
    ('Студия', 'Дизайн', 'Проект дизайна', 5, 'Какой цветовой палитрой вы предпочитаете работать', 'Цвет', 'Яркие и насыщенные цвета| Пастельные и нежные цвета| Монохромная и черно-белая палитра| Естественные и землистые тона'),
    ('Студия', 'Дизайн', 'Проект дизайна', 6, 'Какая информация или элементы должны быть включены в дизайне', 'Информация и элементы', 'Логотип и название компании| Текстовые данные и описания| Изображения и фотографии| Графики и диаграммы'),


    ('Студия', 'Мероприятие', 'Проект', 1, 'Какой тип мероприятия вы планируете организовать', 'Тип мероприятия', 'Конференция| Корпоративное мероприятие| Выставка или ярмарка| Культурное или развлекательное событие| Спортивное мероприятие'),
    ('Студия', 'Мероприятие', 'Проект', 2, 'Какова цель вашего мероприятия', 'Цель мероприятия', 'Образовательная или информационная| Продвижение продукта или услуги| Развлечение и развлекательная программа| Нет определенной цели'),
    ('Студия', 'Мероприятие', 'Проект', 3, 'Какой масштаб мероприятия вы планируете', 'Масштаб', 'Маленький (до 50 участников)| Средний (50-200 участников)| Большой (более 200 участников)| Не знаю/не уверен'),
    ('Студия', 'Мероприятие', 'Проект', 4, 'Какой формат мероприятия вы предпочитаете', 'Формат', 'Офлайн (лицом к лицу)| Онлайн (виртуальное)| Гибридный (сочетание офлайн и онлайн)| Не знаю/не уверен'),
    ('Студия', 'Мероприятие', 'Проект', 5, 'Продолжительность мероприятия', 'Продолжительность', 'Однодневное, Многодневное| Вечеринка или специальное мероприятие (несколько часов)| Не знаю/не уверен'),
    ('Студия', 'Мероприятие', 'Проект', 6, 'Какую локацию вы предпочитаете для проведения мероприятия', 'Локация', 'Внутреннее помещение (зал, конференц-зал)| Открытое пространство (парк, пляж)| Особая площадка или специальное место| Виртуальная платформа'),
    ('Студия', 'Мероприятие', 'Проект', 7, 'Какой бюджет вы выделяете на организацию мероприятия', 'Бюджет', NULL),
    ('Студия', 'Мероприятие', 'Проект', 8, 'Кто целевая аудитория вашего мероприятия', 'Целевая аудитория ', 'Бизнес-сектор и профессионалы| Общественность и широкая аудитория| Студенты и академическая сфера| Дети и семейная аудитория'),
    ('Студия', 'Мероприятие', 'Проект', 9, 'Какие дополнительные услуги или элементы вы хотели бы включить в мероприятие', 'Дополнительные услуги', 'Кейтеринг и обслуживание питания| Звуковое и световое оборудование| Декорации и оформление| Рекламные материалы и сувениры| Развлекательная программа или выступления'),


    ('Пиар', NULL, 'Социальные медиа', 1, 'Какая цель вашего проекта в социальных медиа', 'Цель проекта', 'Увеличение узнаваемости бренда| Привлечение новых клиентов| Увеличение продаж и конверсии| Улучшение взаимодействия с существующими клиентами'),
    ('Пиар', NULL, 'Социальные медиа', 2, 'Кто ваша целевая аудитория в социальных медиа', 'Целевая аудитория', 'Молодежь и миллениалы| Профессионалы и бизнес-сектор| Семейная аудитория| Технически подкованные пользователи'),
    ('Пиар', NULL, 'Социальные медиа', 3, 'Какие социальные медиа-платформы вы хотели бы использовать', 'Социальные сети', 'Vk.com| Instagram| Twitter| LinkedIn| YouTube| TikTok'),
    ('Пиар', NULL, 'Социальные медиа', 4, 'Какой тип контента вы планируете создавать и публиковать в социальных медиа', 'Тип контента', 'Текстовые посты| Изображения и фотографии| Видео контент| Инфографика и иллюстрации| Аудио контент'),
    ('Пиар', NULL, 'Социальные медиа', 5, 'Какую частоту публикации вы планируете для контента в социальных медиа', 'Частота публикаций', 'Ежедневно| Несколько раз в неделю| Раз в неделю| Раз в месяц'),
    ('Пиар', NULL, 'Социальные медиа', 6, 'Какие метрики или ключевые показатели производительности (KPI) вы хотели бы использовать для измерения успеха проекта в социальных медиа', 'Метрики и KPI', 'Количество подписчиков и лайков| Количество комментариев и разделений контента| Уровень вовлеченности аудитории (энгейджмент)| Конверсия и покупки'),
    ('Пиар', NULL, 'Социальные медиа', 7, 'Какой бюджет вы выделяете на проект в социальных медиа', 'Бюджет', 'Минимальный| Средний| Высокий| Не знаю/не уверен'),
    ('Пиар', NULL, 'Социальные медиа', 8, 'Какие ограничения или требования необходимо учесть при разработке контента и стратегии в социальных медиа', 'Ограничения и требования', NULL),
    ('Пиар', NULL, 'Социальные медиа', 9, 'Какое сообщение или тематику вы хотели бы передать через социальные медиа', 'Сообщение аудитории', NULL),


    ('Пиар', NULL, 'Репутация', 1, 'Какую цель вы хотели бы достичь в рамках проекта управления репутацией в интернете', 'Цель', 'Улучшение общей репутации компании/бренда| Решение конкретных проблем или негативных отзывов| Увеличение положительных отзывов и рейтинга| Создание и поддержка положительного образа'),
    ('Пиар', NULL, 'Репутация', 2, 'Какие целевые аудитории вы хотели бы охватить в рамках управления репутацией', 'Целевые аудитоии', 'Потребители и клиенты| Партнеры и поставщики| Работники и сотрудники| Инвесторы и финансовые сообщества'),
    ('Пиар', NULL, 'Репутация', 3, 'Какие платформы и онлайн-каналы вы хотели бы использовать для управления репутацией', 'Платформы и онлайн каналы ', 'Социальные сети| Онлайн-форумы и сообщества| Рейтинговые и отзывные сайты| Блоги и веб-сайты'),
    ('Пиар', NULL, 'Репутация', 4, 'Какие инструменты и подходы к управлению репутацией в интернете вы рассматриваете', 'Инструменты', 'Мониторинг и анализ отзывов и упоминаний| Оптимизация контента и поисковая оптимизация (SEO)| Активное участие в социальных сетях и форумах| Разработка и размещение положительного контента'),
    ('Пиар', NULL, 'Репутация', 5, 'Какие ключевые показатели производительности (KPI) вы хотели бы использовать для измерения успеха проекта управления репутацией', 'Ключевые показатели и KPI', 'Количество положительных отзывов и рейтингов| Увеличение трафика на веб-сайт| Снижение негативных отзывов и рейтингов| Уровень удовлетворенности клиентов'),
    ('Пиар', NULL, 'Репутация', 6, 'Как конкуренты или негативные факторы влияют на вашу репутацию в интернете', 'Конкуренты и негативные факторы', NULL),
    ('Пиар', NULL, 'Репутация', 7, 'Какие требования или ограничения необходимо учесть при проведении проекта', 'Ограничения и особенности', NULL),
    ('Пиар', NULL, 'Репутация', 8, 'Дополнительные данные и важная информация для оценки проекта управления репутацией в интернете', 'Дополнительные данные', NULL),


    ('Пиар', NULL, 'Промоакция', 1, 'Какая цель у вашей промоакции', 'Цель промоакции', 'Увеличение продаж конкретного продукта или услуги| Привлечение новых клиентов| Укрепление связи с существующими клиентами| Увеличение узнаваемости бренда'),
    ('Пиар', NULL, 'Промоакция', 2, 'Какая целевая аудитория должна быть заинтересована в следствии промоакции', 'Целевая аудитория', 'Молодежь и миллениалы| Профессионалы и бизнес-сектор| Семейная аудитория| Технически подкованные пользователи'),
    ('Пиар', NULL, 'Промоакция', 3, 'Какие продукты или услуги будут участвовать в промоакции', 'Продукты и услуги', 'Один конкретный продукт или услуга| Группа продуктов или услуг| Все продукты или услуги вашей компании'),
    ('Пиар', NULL, 'Промоакция', 4, 'Какой будет длительность промоакции', 'Длительность', 'Однодневная| Несколько дней| Недельная| Месячная'),
    ('Пиар', NULL, 'Промоакция', 5, 'Какие каналы или платформы вы планируете использовать для промоакции', 'Задействуемые каналы', 'Социальные медиа| Электронная почта| Сайт компании| Рекламные баннеры на веб-сайтах| Традиционные СМИ (телевидение, радио, пресса)'),
    ('Пиар', NULL, 'Промоакция', 6, 'Какие метрики или ключевые показатели производительности (KPI) вы хотели бы использовать для измерения успеха промоакции', 'Метрики для измерения', 'Количество продаж| Количество участников/регистраций| Количество просмотров/кликов| Конверсионная воронка'),
    ('Пиар', NULL, 'Промоакция', 7, 'Какой бюджет вы выделяете на промоакцию', 'Бюджет', '200 000 руб.| 500 000 руб.| 1 000 000 руб.'),
    ('Пиар', NULL, 'Промоакция', 8, 'Какое сообщение или предложение будет использоваться в промоакции', 'Сообщения для аудитории', NULL),
    ('Пиар', NULL, 'Промоакция', 9, 'Каким будет формат промоакции', 'Формат', 'Скидки или акционные предложения| Бесплатные подарки или образцы| Конкурсы или розыгрыши| Информационные вебинары или мастер-классы'),
    ('Пиар', NULL, 'Промоакция', 10, 'Каков срок запуска промоакции и ее продолжительность', 'Срок реализации', NULL),
    ('Пиар', NULL, 'Промоакция', 11, 'Какие ограничения или требования вам необходимо учесть при организации промоакции', 'Ограничения и особенности', NULL),


    ('Пиар', NULL, 'Стратегия', 1, 'Какая цель у пиар-стратегии', 'Цель проекта', 'Увеличение видимости и осведомленности о бренде/компании| Улучшение имиджа и репутации| Привлечение новых клиентов или инвесторов| Кризисное управление и решение проблем'),
    ('Пиар', NULL, 'Стратегия', 2, 'Какая целевая аудитория для которой строится пиар-стратегии', 'Целевая аудитория', 'Потребители и клиенты| Бизнес-сектор и партнеры| Медиа и журналисты| Инвесторы и финансовые сообщества'),
    ('Пиар', NULL, 'Стратегия', 3, 'Какие каналы и инструменты вы хотели бы использовать в пиар-стратегии', 'Каналы и инструменты', 'Пресс-релизы и связи с СМИ| Онлайн-публикации и блоги| Социальные медиа и инфлюенсеры| Мероприятия и конференции'),
    ('Пиар', NULL, 'Стратегия', 4, 'Какие сообщения и ключевые идеи вы хотели бы передать через пиар', 'Сообщение и ключевая идея', 'Уникальные особенности продукта/услуги| Инновационные и технологические достижения| Корпоративная ответственность и устойчивость| Экспертность и авторитет в отрасли'),
    ('Пиар', NULL, 'Стратегия', 5, 'Какие метрики или ключевые показатели производительности (KPI) вы хотели бы использовать для измерения успеха пиар-стратегии', 'Метрики и KPI', 'Количество публикаций и упоминаний в СМИ| Количество положительных отзывов и комментариев|  Уровень осведомленности целевой аудитории| Увеличение трафика на веб-сайт или социальные медиа'),
    ('Пиар', NULL, 'Стратегия', 6, 'Какой бюджет вы выделяете на проект пиар-стратегии', 'Бюджет', 'Минимальный| Средний| Высокий'),
    ('Пиар', NULL, 'Стратегия', 7, 'Какие ограничения или требования необходимо учесть при разработке пиар-стратегии', 'Ограничения и требования', NULL),
    ('Пиар', NULL, 'Стратегия', 8, 'Какие конкуренты или негативные факторы влияют на вашу репутацию или образ в отрасли', 'Конкуренты и негативные факторы', NULL),
    ('Пиар', NULL, 'Стратегия', 9, 'Какие дополнительные данные или информацию вы считаете важными для оценки проекта пиар-стратегии', 'Дополнительные данные', NULL),
    ('Пиар', NULL, 'Стратегия', 10, 'Какая ваша предполагаемая длительность проекта пиар-стратегии', 'Длительность проекта', NULL);

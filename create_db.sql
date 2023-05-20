
CREATE TABLE partners (
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    id BIGINT PRIMARY KEY,
    name VARCHAR(255)
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
    phone VARCHAR(50),
    company TEXT
);

CREATE TABLE questions (
    id INT AUTO_INCREMENT PRIMARY KEY NOT NULL,
    direction VARCHAR(255),
    sub_direction VARCHAR(255),
    section_name VARCHAR(50),
    question_number INT,
    question_text TEXT,
    answer TEXT DEFAULT NULL
);


--CREATE TABLE clients_briefings (
--    id BIGINT AUTO_INCREMENT PRIMARY KEY NOT NULL,
--    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
--    client_id BIGINT,
--    question_id INT,
--    user_response TEXT,
--    FOREIGN KEY(client_id) REFERENCES clients(id),
--    FOREIGN KEY(question_id) REFERENCES questions(id)
--);

CREATE TABLE clients_briefings (
    id INT AUTO_INCREMENT PRIMARY KEY,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    client_id BIGINT NOT NULL,
    question_id INT NOT NULL,
    user_response TEXT,
    UNIQUE KEY idx_client_question (client_id, question_id),
    FOREIGN KEY(client_id) REFERENCES clients(id),
    FOREIGN KEY(question_id) REFERENCES questions(id)
);

INSERT INTO questions (direction, sub_direction, section_name, question_number, question_text, answer)
VALUES
    ('Маркетинг', NULL, 'Стратегия', 1, 'Цель вашего проекта', 'Увеличить продажи, Снизить затраты, Улучшить сервис'),
    ('Маркетинг', NULL, 'Стратегия', 2, 'Ключевые задачи', 'Разработать новые продукты, Увеличить узнаваемость, Расширить каналы распространения'),
    ('Маркетинг', NULL, 'Стратегия', 3, 'Срок реализации проекта', '6 месяцев, 12 месяцев, 18 месяцев'),
    ('Маркетинг', NULL, 'Стратегия', 4, 'Бюджет', '500 000 руб., 850 000 руб., 1 200 000 руб.'),
    ('Маркетинг', NULL, 'Стратегия', 5, 'Какие демографические характеристики у аудитории', 'Пол, Возраст, Доход, Интересы'),
    ('Маркетинг', NULL, 'Стратегия', 6, 'Какие ключевые факторы влияют на покупку', 'Цена, Качество, Узнаваемость бренда, Удобство использования'),
    ('Маркетинг', NULL, 'Стратегия', 7, 'Кто главные конкуренты', NULL),
    ('Маркетинг', NULL, 'Стратегия', 8, 'Сильные и слабые стороны конкурентов|Положительные|Отрицательные', NULL),
    ('Маркетинг', NULL, 'Стратегия', 9, 'Как целевая аудитория воспринимает бренд компании', 'Положительно, Отрицательно, Нейтрально'),
    ('Маркетинг', NULL, 'Стратегия', 10, 'Какова эффективность текущей маркетинговой стратегии', 'Очень эффективна, Умеренно эффективна, Неэффективна'),
    ('Маркетинг', NULL, 'Стратегия', 11, 'Какие маркетинговые каналы наиболее эффективны сейчас', NULL),
    ('Маркетинг', NULL, 'Стратегия', 12, 'Какие способы привлечения наиболее эффективны сейчас', 'Скидки и специальные предложения, Рекламные кампании на новых рынках, Рекомендации от клиентов'),
    ('Маркетинг', NULL, 'Стратегия', 13, 'Какие основные вызовы стоят перед компанией', 'Высокая конкуренция, Низкая лояльность клиентов, Большие расходы на маркетинг, Быстро меняющиеся требования рынка'),
    ('Маркетинг', NULL, 'Исследования', 1, 'Вопрос исследований', 'Ответ1, Ответ2, Ответ3'),
    ('Маркетинг', NULL, 'Подписка', 1, 'Вопрос подписки', 'Ответ1, Ответ2, Ответ3'),
    ('Студия', 'ВЕБ', 'Сайты', 1, 'Вопрос сайтов', 'Ответ1, Ответ2, Ответ3'),
    ('Студия', 'Звук', 'Рекламные ролики', 1, 'Вопрос сайтов', 'Ответ1, Ответ2, Ответ3'),
    ('Креатив', NULL, 'Концепция', 1, 'Вопрос Концепция', 'Ответ1, Ответ2, Ответ3'),
    ('Креатив', NULL, 'Концепция', 2, 'Вопрос Концепция', 'Ответ1, Ответ2, Ответ3');

INSERT INTO clients (id) VALUES (123);

INSERT INTO clients_briefings (client_id, question_id, user_response) VALUES (123, 2, 'Ответ пользователя');

--SELECT cb.client_id, cb.response, q.text FROM clients_briefings cb INNER JOIN questions q ON cb.question_id=q.id WHERE cb.client_id = 456;



SELECT questions.id, questions.question_text, COALESCE(clients_briefings.user_response, 'Ответа нет') AS answer_text
FROM questions
LEFT JOIN clients_briefings ON questions.id = clients_briefings.question_id AND clients_briefings.client_id = 123
WHERE questions.id = 2;




# API-for-the-library
RESTful API для базового управления библиотечным каталогом.

## Техническое исполнение.

Приложение реализовано, функционально, запускается в контейнере.
    
    Управление зависимостями с Poetry.

    Парадинма: Асинхронное программирование.

    Язык программирования: Python 3.12.3.

    Сервер: Uvicorn на 8000 порту. 
    
    Фреймворк: FastAPI.

    База данных: PostgreSQL.

    ORM: SQLAlchemy 
   
    Аутентификация (Новое): JWT с использованием python-jose для токенов и passlib[bcrypt] для хеширования паролей.

    Логирование: Loguru - выводится в stdout, но можно настроить запись в Loki или в файл через docker-compose.yaml.
 
    Валидация данных: Pydantic.


## Подготовка к запуску.

### После клонирования проекта можно установить зависимости из pyproject.toml. Вот некоторые команды **bash**:
    
    curl -sSL https://install.python-poetry.org | python3 - свежая версия poetry если необходимо.

    export PATH="$HOME/.local/bin:$PATH" - задать путь для доступности.

    poetry install  - установить зависимости из pyproject.toml.

### Переменные окружения. Создать в корне проекта .env и заполнить по шаблону файла .env.template:

    POSTGRES_USER=ваш логин
    
    POSTGRES_PASSWORD=ваш пароль
    
    DB_PORT=порт базы данных
    
    POSTGRES_DB=название базы данных
    
    SECRET_KEY=секретная строка (ключ), которая используется для подписывания и проверки JWT-токенов.
    
    ALGORITHM= алгоритм хеширования (шифрования) для создания подписи JWT. Чаще всего применяется "HS256".
    
    ACCESS_TOKEN_EXPIRE_MINUTES=время жизни (в минутах) JWT-токена доступа.
    
    LOGLEVEL=Уровень логирования.


## Запуск и работа приложения

### Для запуска приложения, просмотра логов необходимо выполнить команды bash:

    docker compose up --build -d - первая сборка и запуск.

    docker compose logs app - логи приложения (-f app - в фоновом режиме).

    docker compose logs db - логи базы данных (-f db - в фоновом режиме).

    docker compose logs db_test - логи тестовой базы данных (-f db_test - в фоновом режиме).

### Аутентификация. Включает регистрацию и получение токена для управления базой библиотеки.
Эта разработка вызвала у меня большую трудность, так как я совешенно не изучал данный вопрос ранее.

#### Краткое описание реализации аутентификации:

В проекте для аутентификации используется JWT (JSON Web Token), который генерируется и проверяется с помощью библиотеки python-jose. 
Пароли пользователей хранятся в виде хэшей, созданных с помощью passlib[bcrypt] - это обеспечивает безопасное хранение и проверку паролей.
Генерация токена: при успешной аутентификации создаётся JWT-токен с полезной нагрузкой - email пользователя - и временем жизни, заданным в настройках (ACCESS_TOKEN_EXPIRE_MINUTES). Токен подписывается секретным ключом (SECRET_KEY) с использованием алгоритма (ALGORITHM), что гарантирует его целостность и подлинность.
Проверка токена: при обращении к защищённым эндпоинтам сервер проверяет подпись и срок действия токена, чтобы удостовериться в правомерности доступа.
Защищённые эндпоинты: доступны только аутентифицированным пользователям -библиотекарям, для чего используется зависимость Depends(get_current_librarian),
которая извлекает и проверяет токен из запроса.

Используемые библиотеки:

    python-jose[cryptography] - для создания и верификации JWT-токенов, выбран за надёжность и поддержку стандартов.

    passlib[bcrypt] - для безопасного хеширования паролей с использованием алгоритма bcrypt, который устойчив к атакам перебора.

**ВАЖНО:** Auth2PasswordRequestForm из fastapi.security ждёт от нас **не json**, **а форму** и она не ждёт никаких других полей, кроме обязательных **username** и **password**(поле **email** не ждёт). С помощью passlib.context.CryptContext создается форма для заполнения данных.

При регистрации главное ввести уникальный email (и email) - на примере оставил уже зарегистрированный чей-то.
![image](https://github.com/user-attachments/assets/3efbdaec-fb7f-401d-bfd8-37d7797b8650)
![image](https://github.com/user-attachments/assets/61a9432d-f59f-4dcb-93e4-65ff996117fa)

Поправил.
![image](https://github.com/user-attachments/assets/ca8a7504-3b00-4f2d-8978-8875d9323a47)

Для получения права **Depends(get_current_librarian)**, нужно клинуть кнопку с **замочком**, пост запрос ниже вернёт токен но права не даст.
![image](https://github.com/user-attachments/assets/59bd9809-fe2e-4cdd-a4a1-c55c80fe2953)

Заполнить **username**/**password**
![image](https://github.com/user-attachments/assets/dcab0aa4-6347-4c2e-9273-aad1b2f290e2)
![image](https://github.com/user-attachments/assets/152f110b-2979-431a-ad4b-1436d0b3d48c)


### Краткое описание структуры проекта.

#### Swagger и Onen Api.

Для каждого эндпоинта существуют модели сериализации c Pydantic, в том числе обработчики ошибок сериализуются в стандартные json ответы.
всё задокументировано и создает возможность для подключения фронтенда.

#### Модели таблиц.

    class Base(DeclarativeBase): 
    - базовый декларатиный из ОРМ SQLAlchemy

    class BaseModel(Base):
    - абстрктная родительская модель. Пока содержит общий для наследников ID, но может расширяться, например, created_at.

    class Librarian(BaseModel):
    - модель не имеет связей, имеет три поля: name - бесполезное (что б было); email - уникальное, так как попадает в токен для идентификации; password - не уникальный, так как все равно хэшируется.

    class Book(BaseModel):
        - имеет связь многие-ко-многим с class Reader(BaseModel) через class ReaderBook(BaseModel);
        - поля: title - обязательная строка; author - обязательная строка; publication_year - необязательное int; isbn - уникальная, 
              но необязательная строка; copies_count - обязательная int - копий не меньше 0.
        - реализован полный CRUD.
![image](https://github.com/user-attachments/assets/499e78c9-aa39-4811-b60c-3f17167a5097)
        - Уникальность isbn проверяется. Если оставить случайно предыдущий, произойдет ошибка.
![image](https://github.com/user-attachments/assets/fdb26f7d-8125-4fee-9f79-ef10974f1794)
        - Если разлогиниться, то не сможешь ничего, кроме просмотра книг.
![image](https://github.com/user-attachments/assets/c6fcac98-f839-46d1-9289-c7def672f68b)
        - Просмотр книг оставил без Depends(get_current_librarian), что бы читатели получали информацию о книгах.
![image](https://github.com/user-attachments/assets/dbd6e4ab-8ef5-457f-bb58-fd852d037540)
        - Тут пагинация страниц с fastapi_pagination.Page/Params, fastapi_pagination.ext.sqlalchemy.paginate.
              Предусмотрена сортировка по LIFO, что бы новинки были сразу видны.
![image](https://github.com/user-attachments/assets/f6f0d963-6c9b-4246-b7fa-bc83a47485a0)
              
        - Если, например, обновить без авторизации,
![image](https://github.com/user-attachments/assets/05758655-8548-4eea-a903-69c1133711de)
            то получим сереиализованную ошибку.
![image](https://github.com/user-attachments/assets/a2f3ca3e-6f74-42a1-8ad3-d054094892ca)
        - Если авторизоваться - обновится.
![image](https://github.com/user-attachments/assets/3bd65b6a-2bbd-4a02-b671-1a6650bbcef2)
        - Во всех эндпоинтах, где вводиться id, предусмотрена проверка. Например, введем ложный id.
![image](https://github.com/user-attachments/assets/7cc5d452-66fe-46ed-85db-00a91668887f)
              Если правильно:
![image](https://github.com/user-attachments/assets/1a895157-e3c7-4b28-a2d7-c4b388733069)
        - Удаление книги реализовано через связь с промежуточной таблицей cascade="all, delete-orphan", то есть при удалении книги
              удалиться и запись в таблице, именно поэтому предусмотрено, что книгу с активными - выданными экземплярами - не удалить.
              пример приведу ниже.

        class Reader(BaseModel):
            - имеет такую же связь многие-ко-многим к class Book(BaseModel), через class ReaderBook(BaseModel);
            - поля: name - обязательная строка, email - обязательная уникальная строка, note - необязательная строка до 500 символов.
            - CRUD такой же как и в Book(BaseModel).
![image](https://github.com/user-attachments/assets/ffa78bff-1070-432a-81d7-42efdee4dc33)
            - Проверяется уникальность email. Если ошибка, то выведет.
![image](https://github.com/user-attachments/assets/135cb701-5319-42e2-ad2d-9806dfdb6726)
            - А не ошибиться, то:
![image](https://github.com/user-attachments/assets/e80e8426-2270-4d0e-a1fc-d5cabd840a0d)
             - Просмотр всех пользователей с такой же пагинацией, что и у Book(BaseModel), но
                 предусмотрена сортировка по алфавиту.
![image](https://github.com/user-attachments/assets/cb44267a-c109-4239-a629-21314bfb84d0)
             - Вопросы обновления, получения по id и удаления решены по тому же принципу, что в Book(BaseModel).

             class ReaderBook(BaseModel)
             - промежуточная таблица для регистрации выдачи и возврата книг;
![image](https://github.com/user-attachments/assets/a835f16a-0229-409b-8582-acf55ead71f8)
             
             -поля: reader_id - id читателя ForeignKey с ondelete="CASCADE"; book_id - то же для книг, 
                 borrow_date - дата выдачи проставляется автоматом с erver_default=func.now();
                 return_date - дата возврата, None до момента возврата.

             - выдача книг: Проверяет, и вычитает копии книг, проверяет читателей на условие <= 3 книги.
                  Так у книги 3 - 1 копия.
 ![image](https://github.com/user-attachments/assets/84d212ec-413e-4428-9d14-06b8a2eb65b0)
                  Получили экземпляр.
 ![image](https://github.com/user-attachments/assets/9285f7ee-922f-4076-83c5-b6f4b3921bd9)
                  Остался 0.
 ![image](https://github.com/user-attachments/assets/a76efc64-377f-4266-8f15-ed1c69f58654)
                  Пробуем взять.
![image](https://github.com/user-attachments/assets/b7fce5de-e42c-40c4-af4a-4b1ae96feb0e)
                  Сейчас возму еще 2 книги читателю 2. И  4-ю книгу ему не дали.
![image](https://github.com/user-attachments/assets/64fdabfb-f50f-4ae5-8d29-ee7c4cb96dcb)

            - релизован просмотр книг, которые выданы читателю.
![image](https://github.com/user-attachments/assets/ec1e3533-6d81-42c6-ab41-78bb71dd57d7)
                   Тут в от ответы номера id выводятся, но возможно фронтенд это устроит, если нет - можно выводить и названия с именами.

             - Вернемся к удалению. Библиотекарь не сможет удалить Книгу с ID 3 , так как она активна. Идет проверка наличия ее ID в 
                   class ReaderBook(BaseModel) и одновременно проверка наличия даты в поле return_date.
![image](https://github.com/user-attachments/assets/49acea0c-604f-4a86-b96c-e0c072e3a97c)
                   по этому же принципу не удалим читателя 1.
![image](https://github.com/user-attachments/assets/86d2a42a-dd86-40a7-a4b7-a1bed1bda074)

              - Реализован эндпоинт возврата книг. 
![image](https://github.com/user-attachments/assets/27f0d4f7-2ade-4d8c-aa09-a440971e836a)
              проставляется дата возврата книги.
![image](https://github.com/user-attachments/assets/d59ed4e7-aebb-4bd0-a42a-acd72e1e5625)
              И, поскольку 3 книга перестала иметь активную связь, ее можно удалить.
![image](https://github.com/user-attachments/assets/648109d4-8229-4b26-9903-46423e889c84)


### Реализация миграций с Alembic.

Данный вопрос пока не решен. Предварительно сделан alembic init alembic и внесены данные в env.py


### Реализация тестирования с Pytest.

Тесты пока не написаны, но: 
    - запускается тестовая база данных с пробросом 5433:5433;
    - создан файл config.py с фикстурами и переопределением сессии на тестовую с dependency_overrides.


### Запись логов.

В docker-compose.yaml предусмотрено (закоментировано) создание сервиса grafana/loki для записи. 

При желании можно настроить Sentry (при наличии VPN).

### Дополнительные усовершенствования:

Верификация email библтотекаря. После того, как читатель ввёл пароль и email, пароль временно сохраним в Redis.
Используем функцию асинхронной отправки письма через FastAPI-Mail  с помощью background_tasks.add_task().
Библиотекарь получает письмо со ссылкой на токен подтверждения, кликает на нее, его браузер делает Get запрос
на этот URL. На сервере эндпоинт принимает запрос, сервер дешифрует, проверит токен, пометит email как верифицированный и прдолжит 
афутентификацию, выдаст JWT.
 


              
                     

                   
                   
                   
            
            
                  

                 
                 
                 
                  

            

            
              
        
        
        

            

        
        

    






    
    

    
    

    

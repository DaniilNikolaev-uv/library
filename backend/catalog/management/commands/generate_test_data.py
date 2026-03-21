import random
from datetime import date, timedelta
from decimal import Decimal

from django.core.management.base import BaseCommand
from django.utils import timezone
from django.db import transaction

from accounts.models import Reader, Staff, User, Role
from catalog.models import Author, Book, Category, Publisher
from circulation.models import Loan
from fines.models import FinePolicy, Fine
from inventory.models import Location, BookCopy
from reservations.models import Reservation


class Command(BaseCommand):
    help = "Генерирует тестовые данные для библиотеки"

    def add_arguments(self, parser):
        parser.add_argument(
            "--books",
            type=int,
            default=100,
            help="Количество книг",
        )
        parser.add_argument(
            "--readers",
            type=int,
            default=50,
            help="Количество читателей",
        )
        parser.add_argument(
            "--loans",
            type=int,
            default=80,
            help="Количество выдач",
        )
        parser.add_argument(
            "--reservations",
            type=int,
            default=20,
            help="Количество бронирований",
        )

    @transaction.atomic
    def handle(self, *args, **options):
        books_count = options["books"]
        readers_count = options["readers"]
        loans_count = options["loans"]
        reservations_count = options["reservations"]

        self.stdout.write("📚 Генерация тестовых данных...\n")

        # Очищаем существующие данные (в обратном порядке зависимостей)
        self.stdout.write("🧹 Очистка существующих данных...")
        Fine.objects.all().delete()
        Reservation.objects.all().delete()
        Loan.objects.all().delete()
        BookCopy.objects.all().delete()
        Reader.objects.all().delete()
        Staff.objects.all().delete()
        User.objects.all().delete()
        Book.objects.all().delete()
        Author.objects.all().delete()
        Category.objects.all().delete()
        Publisher.objects.all().delete()
        Location.objects.all().delete()
        FinePolicy.objects.all().delete()
        self.stdout.write("✅ Данные очищены\n")

        # Создаем издателей
        publishers_data = [
            {"name": "Эксмо", "country": "Россия", "city": "Москва"},
            {"name": "АСТ", "country": "Россия", "city": "Москва"},
            {"name": "Питер", "country": "Россия", "city": "Санкт-Петербург"},
            {"name": "БХВ-Петербург", "country": "Россия", "city": "Санкт-Петербург"},
            {"name": "Манн, Иванов и Фербер", "country": "Россия", "city": "Москва"},
            {"name": "Альпина Паблишер", "country": "Россия", "city": "Москва"},
            {"name": "Олимп", "country": "Россия", "city": "Москва"},
            {"name": "Феникс", "country": "Россия", "city": "Ростов-на-Дону"},
            {"name": "Вильямс", "country": "Россия", "city": "Москва"},
            {"name": "ДМК Пресс", "country": "Россия", "city": "Москва"},
            {"name": "Penguin Books", "country": "UK", "city": "London"},
            {"name": "HarperCollins", "country": "USA", "city": "New York"},
            {"name": "Random House", "country": "USA", "city": "New York"},
            {"name": "Simon & Schuster", "country": "USA", "city": "New York"},
            {"name": "Macmillan", "country": "UK", "city": "London"},
        ]
        publishers = []
        for pub_data in publishers_data:
            pub, _ = Publisher.objects.get_or_create(
                name=pub_data["name"],
                defaults=pub_data,
            )
            publishers.append(pub)

        self.stdout.write(f"✅ Создано {len(publishers)} издателей")

        # Создаем категории
        categories_data = [
            {"name": "Художественная литература"},
            {"name": "Научная фантастика"},
            {"name": "Фэнтези"},
            {"name": "Детектив"},
            {"name": "Роман"},
            {"name": "Классика"},
            {"name": "Научно-популярная"},
            {"name": "Техническая"},
            {"name": "Программирование"},
            {"name": "Бизнес"},
            {"name": "Психология"},
            {"name": "История"},
            {"name": "Биографии"},
            {"name": "Детская"},
            {"name": "Учебная"},
        ]
        categories = {}
        parent_categories = {}

        for cat_data in categories_data:
            cat, _ = Category.objects.get_or_create(name=cat_data["name"])
            categories[cat.name] = cat

        # Добавляем подкатегории
        subcategories = [
            {"name": "Python", "parent": "Программирование"},
            {"name": "JavaScript", "parent": "Программирование"},
            {"name": "Java", "parent": "Программирование"},
            {"name": "Веб-разработка", "parent": "Программирование"},
            {"name": "Машинное обучение", "parent": "Программирование"},
            {"name": "Менеджмент", "parent": "Бизнес"},
            {"name": "Маркетинг", "parent": "Бизнес"},
            {"name": "Финансы", "parent": "Бизнес"},
            {"name": "Космос", "parent": "Научно-популярная"},
            {"name": "Физика", "parent": "Научно-популярная"},
            {"name": "Биология", "parent": "Научно-популярная"},
        ]

        for sub_data in subcategories:
            parent = categories.get(sub_data["parent"])
            if parent:
                cat, _ = Category.objects.get_or_create(
                    name=sub_data["name"],
                    defaults={"parent": parent},
                )
                categories[cat.name] = cat

        self.stdout.write(f"✅ Создано {Category.objects.count()} категорий")

        # Создаем авторов
        authors_data = [
            ("Иван", "Тургенев", "Сергеевич", date(1818, 11, 9), date(1883, 9, 3)),
            ("Фёдор", "Достоевский", "Михайлович", date(1821, 11, 11), date(1881, 2, 9)),
            ("Лев", "Толстой", "Николаевич", date(1828, 9, 9), date(1910, 11, 20)),
            ("Антон", "Чехов", "Павлович", date(1860, 1, 29), date(1904, 7, 15)),
            ("Александр", "Пушкин", "Сергеевич", date(1799, 6, 6), date(1837, 2, 10)),
            ("Николай", "Гоголь", "Васильевич", date(1809, 4, 1), date(1852, 3, 4)),
            ("Михаил", "Булгаков", "Афанасьевич", date(1891, 5, 15), date(1940, 3, 10)),
            ("Владимир", "Набоков", "Владимирович", date(1899, 4, 22), date(1977, 7, 2)),
            ("Исаак", "Азимов", "", date(1920, 1, 2), date(1992, 4, 6)),
            ("Артур", "Кларк", "Чарльз", date(1917, 12, 16), date(2008, 3, 19)),
            ("Рэй", "Брэдбери", "", date(1920, 8, 22), date(2012, 6, 5)),
            ("Фрэнк", "Герберт", "", date(1920, 10, 8), date(1986, 10, 11)),
            ("Айзек", "Азимов", "", date(1920, 1, 2), date(1992, 4, 6)),
            ("Стивен", "Кинг", "Эдвин", date(1947, 9, 21), None),
            ("Джоан", "Роулинг", "", date(1965, 7, 31), None),
            ("Джордж", "Мартин", "Рэймонд", date(1948, 9, 20), None),
            ("Толкин", "Толкин", "Рональд Руэл", date(1892, 1, 3), date(1973, 9, 2)),
            ("Агата", "Кристи", "Мэри Кларисса", date(1890, 9, 15), date(1976, 1, 12)),
            ("Эрнест", "Хемингуэй", "Миллер", date(1899, 7, 21), date(1961, 7, 2)),
            ("Габриэль", "Гарсиа Маркес", "", date(1927, 3, 6), date(2014, 4, 17)),
            ("Харуки", "Мураками", "", date(1949, 1, 12), None),
            ("Умберто", "Эко", "", date(1932, 1, 5), date(2016, 2, 19)),
            ("Дэн", "Браун", "", date(1964, 6, 22), None),
            ("Джон", "Грин", "", date(1977, 8, 24), None),
            ("Чак", "Паланик", "", date(1962, 2, 21), None),
            ("Григорий", "Остер", "Бенционович", date(1943, 11, 27), None),
            ("Алексей", "Толстой", "Николаевич", date(1883, 1, 10), date(1945, 2, 23)),
            ("Сергей", "Лукьяненко", "Васильевич", date(1968, 4, 11), None),
            ("Дмитрий", "Глуховский", "", date(1978, 8, 12), None),
            ("Борис", "Акунин", "", date(1956, 5, 20), None),
            ("Александр", "Маринина", "", date(1957, 6, 16), None),
            ("Дарья", "Донцова", "", date(1953, 6, 7), None),
            ("Юлий", "Семенов", "Семёнович", date(1937, 12, 16), None),
            ("Василий", "Головачев", "", date(1948, 3, 5), date(2022, 5, 24)),
            ("Ник", "Перумов", "", date(1963, 11, 21), None),
            ("Мария", "Семенова", "", date(1958, 8, 1), None),
            ("Андрей", "Белянин", "", date(1961, 1, 15), None),
            ("Роберт", "Хайнлайн", "Энсон", date(1907, 7, 7), date(1988, 5, 8)),
            ("Филип", "Дик", "Киндред", date(1928, 12, 16), date(1982, 3, 2)),
            ("Уильям", "Гибсон", "", date(1948, 3, 17), None),
            ("Невил", "Шют", "", date(1895, 2, 9), date(1960, 8, 10)),
            ("Герберт", "Уэллс", "Джордж", date(1866, 9, 21), date(1946, 8, 13)),
            ("Жюль", "Верн", "", date(1828, 2, 8), date(1905, 3, 24)),
            ("Даниэль", "Дефо", "", date(1660, 1, 1), date(1731, 4, 24)),
            ("Джонатан", "Свифт", "", date(1667, 11, 30), date(1745, 10, 19)),
            ("Марк", "Твен", "", date(1835, 11, 30), date(1910, 4, 21)),
            ("Джек", "Лондон", "", date(1876, 1, 12), date(1916, 11, 22)),
            ("Фрэнсис", "Фицджеральд", "Скотт", date(1896, 9, 24), date(1940, 12, 21)),
            ("Джером", "Сэлинджер", "Дэвид", date(1919, 1, 1), date(2010, 1, 27)),
            ("Олдос", "Хаксли", "Леонард", date(1894, 7, 26), date(1963, 11, 22)),
        ]

        authors = []
        for first, last, middle, dob, dod in authors_data:
            author, _ = Author.objects.get_or_create(
                first_name=first,
                last_name=last,
                defaults={
                    "middle_name": middle,
                    "date_of_birth": dob,
                    "date_of_death": dod,
                },
            )
            authors.append(author)

        self.stdout.write(f"✅ Создано {Author.objects.count()} авторов")

        # Создаем книги
        book_titles = [
            "Война и мир", "Преступление и наказание", "Анна Каренина", "Вишнёвый сад",
            "Евгений Онегин", "Мёртвые души", "Мастер и Маргарита", "Защита Лужина",
            "Я, робот", "2001: Космическая одиссея", "451 градус по Фаренгейту", "Дюна",
            "Основание", "Сияние", "Гарри Поттер и философский камень", "Игра престолов",
            "Властелин колец", "Убийство в Восточном экспрессе", "Старик и море",
            "Сто лет одиночества", "Норвежский лес", "Имя розы", "Код да Винчи",
            "Виноваты звёзды", "Бойцовский клуб", "Вредные советы", "Золотой ключик",
            "Ночной дозор", "Метро 2033", "Азазель", "Тайна пропавшей шапки",
            "Танец смерти", "Семнадцать мгновений весны", "Пустота", "Эльфийский клинок",
            "Волкодав", "Особый отряд", "Звёздный десант",
            "Мечтают ли андроиды об электроовцах", "Нейромант", "На берегу",
            "Война миров", "Двадцать тысяч льё под водой", "Робинзон Крузо",
            "Путешествия Гулливера", "Приключения Гекльберри Финна", "Моби Дик",
            "Великий Гэтсби", "Над пропастью во ржи", "О дивный новый мир",
            "Тихий Дон", "Хождение по мукам", "Доктор Живаго", "Лолита",
            "А зори здесь тихие", "Живой труп", "Воскресение", "Капитанская дочка",
            "Герой нашего времени", "Отцы и дети", "Дворянское гнездо", "Обломов",
            "Горе от ума", "Ревизор", "Шинель", "Мёртвые души",
            "Собачье сердце", "Роковые яйца", "Собор Парижской Богоматери",
            "Три мушкетёра", "Граф Монте-Кристо", "Отверженные", "Собор Парижской Богоматери",
            "Дон Кихот", "Божественная комедия", "Декамерон", "Гаргантюа и Пантагрюэль",
            "Приключения Оливера Твиста", "Большие надежды", "Дэвид Копперфильд",
            "Приключения Шерлока Холмса", "Собака Баскервилей", "Этюд в багровых тонах",
            "Остров сокровищ", "Чёрная стрела", "Властелин колец", "Хоббит",
            "Сильмариллион", "Дети Хурина", "Берен и Лутиэн", "Падение Гондолина",
            "Хроники Нарнии", "Лев, колдунья и платяной шкаф", "Принц Каспиан",
            "Покоритель зари", "Серебряное кресло", "Конь и его мальчик",
            "Последняя битва", "Племянник чародея", "Ключ от всех дверей",
            "Унесённые ветром", "Гордость и предубеждение", "Джейн Эйр",
            "Грозовой перевал", "Тэсс из рода д'Эрбервиллей", "Дэвид Копперфильд",
            "Приключения Тома Сойера", "Принц и нищий", "Янки при дворе короля Артура",
            "Таинственный остров", "Дети капитана Гранта", "Вокруг света за 80 дней",
            "Пять недель на воздушном шаре", "Таинственный остров", "Миканджело",
            "Муза", "Последний университет", "Тёмная башня", "Зелёная миля",
            "Побег из Шоушенка", "11/22/63", "Стрелок", "Извлечение троих",
            "Бесплодные земли", "Колдун и кристалл", "Ветер сквозь замочную скважину",
            "Волк-одиночка", "Тёмная башня", "Каноничка", "Ключ от всех дверей",
        ]

        book_subtitles = [
            "", "Роман", "Повесть", "Рассказы", "Эпопея", "Трилогия",
            "Часть 1", "Часть 2", "Книга 1", "Книга 2",
        ]

        category_groups = [
            [categories["Классика"], categories["Художественная литература"]],
            [categories["Научная фантастика"]],
            [categories["Фэнтези"]],
            [categories["Детектив"]],
            [categories["Роман"]],
            [categories["Классика"]],
            [categories["Научно-популярная"]],
            [categories["Техническая"]],
            [categories["Программирование"]],
            [categories["Бизнес"]],
            [categories["Психология"]],
            [categories["История"]],
            [categories["Биографии"]],
            [categories["Детская"]],
            [categories["Учебная"]],
        ]

        books = []
        for i, title in enumerate(book_titles):
            author = random.choice(authors)
            cats = random.choice(category_groups)
            year = random.randint(1800, 2024)
            subtitle = random.choice(book_subtitles)
            
            book, _ = Book.objects.get_or_create(
                title=title,
                defaults={
                    "subtitle": subtitle if subtitle != "" else None,
                    "year": year,
                    "language": random.choice(["ru", "en", "de", "fr"]),
                    "publisher": random.choice(publishers),
                    "description": f"Описание для книги '{title}'. Это тестовое описание книги.",
                },
            )
            book.authors.add(author)
            for cat in cats:
                book.categories.add(cat)
            books.append(book)

        # Генерируем дополнительные книги если нужно больше
        remaining_books = books_count - len(books)
        if remaining_books > 0:
            additional_titles = [
                f"Книга #{i + len(books) + 1}" for i in range(remaining_books)
            ]
            for title in additional_titles:
                author = random.choice(authors)
                cats = random.choice(category_groups)
                year = random.randint(1900, 2024)
                
                book = Book.objects.create(
                    title=title,
                    year=year,
                    language=random.choice(["ru", "en"]),
                    publisher=random.choice(publishers),
                    description=f"Тестовая книга '{title}'. Описание сгенерировано автоматически.",
                )
                book.authors.add(author)
                for cat in cats:
                    book.categories.add(cat)
                books.append(book)

        self.stdout.write(f"✅ Создано {Book.objects.count()} книг")

        # Создаем локации
        locations_data = [
            {"name": "Главный зал", "code": "MAIN"},
            {"name": "Детский зал", "code": "CHILD"},
            {"name": "Научный зал", "code": "SCI"},
            {"name": "Художественный зал", "code": "ART"},
            {"name": "Периодика", "code": "PER"},
            {"name": "Редкий фонд", "code": "RARE"},
            {"name": "Склад", "code": "STORE"},
            {"name": "Стеллаж A", "code": "A", "parent_name": "Главный зал"},
            {"name": "Стеллаж B", "code": "B", "parent_name": "Главный зал"},
            {"name": "Стеллаж C", "code": "C", "parent_name": "Детский зал"},
            {"name": "Стеллаж D", "code": "D", "parent_name": "Научный зал"},
            {"name": "Стеллаж E", "code": "E", "parent_name": "Художественный зал"},
        ]

        locations = {}
        for loc_data in locations_data:
            parent_name = loc_data.pop("parent_name", None)
            parent = locations.get(parent_name) if parent_name else None
            loc, _ = Location.objects.get_or_create(
                code=loc_data["code"],
                defaults={**loc_data, "parent": parent},
            )
            locations[loc.name] = loc

        self.stdout.write(f"✅ Создано {Location.objects.count()} локаций")

        # Создаем экземпляры книг (по 2-5 на книгу)
        copies = []
        copy_counter = 1
        for book in books:
            num_copies = random.randint(2, 5)
            for j in range(num_copies):
                status_choices = [
                    BookCopy.Status.AVAILABLE,
                    BookCopy.Status.AVAILABLE,
                    BookCopy.Status.AVAILABLE,
                    BookCopy.Status.ON_LOAN,
                    BookCopy.Status.RESERVED,
                ]
                copy = BookCopy.objects.create(
                    book=book,
                    inventory_number=f"INV-{copy_counter:06d}",
                    barcode=f"BC-{copy_counter:08d}",
                    location=random.choice(list(locations.values())),
                    status=random.choice(status_choices),
                    acquired_date=date.today() - timedelta(days=random.randint(1, 1000)),
                )
                copies.append(copy)
                copy_counter += 1

        self.stdout.write(f"✅ Создано {BookCopy.objects.count()} экземпляров")

        # Создаем пользователей и читателей
        first_names = [
            "Александр", "Дмитрий", "Сергей", "Андрей", "Алексей", "Иван", "Михаил",
            "Николай", "Владимир", "Евгений", "Ольга", "Елена", "Наталья", "Ирина",
            "Анна", "Татьяна", "Екатерина", "Мария", "Анастасия", "Светлана",
        ]
        last_names = [
            "Иванов", "Смирнов", "Кузнецов", "Попов", "Васильев", "Петров", "Соколов",
            "Михайлов", "Новиков", "Фёдоров", "Морозов", "Волков", "Алексеев", "Лебедев",
            "Семёнов", "Егоров", "Павлов", "Козлов", "Степанов", "Николаев",
        ]

        users = []
        readers = []
        for i in range(readers_count):
            email = f"reader{i + 1}@example.com"
            user, _ = User.objects.get_or_create(
                email=email,
                defaults={
                    "first_name": random.choice(first_names),
                    "last_name": random.choice(last_names),
                    "role": Role.READER,
                },
            )
            user.set_password("password123")
            user.save()
            users.append(user)

            reader, _ = Reader.objects.get_or_create(
                user=user,
                defaults={
                    "card_number": 10000 + i,
                    "phone_number": f"+7900{1000000 + i:07d}",
                    "email": email,
                    "address": f"ул. Примерная, д. {random.randint(1, 100)}, кв. {random.randint(1, 200)}",
                },
            )
            readers.append(reader)

        self.stdout.write(f"✅ Создано {Reader.objects.count()} читателей")

        # Создаем персонал
        staff_data = [
            ("admin@library.ru", "Админ", "Админов", Role.ADMIN),
            ("librarian1@library.ru", "Библиотекарь", "Библиотекаров", Role.LIBRARIAN),
            ("librarian2@library.ru", "Главный", "Библиотекарев", Role.LIBRARIAN),
        ]
        staff_members = []
        for email, first, last, role in staff_data:
            user, _ = User.objects.get_or_create(
                email=email,
                defaults={
                    "first_name": first,
                    "last_name": last,
                    "role": role,
                    "is_staff": True,
                },
            )
            user.set_password("admin123")
            user.save()
            staff, _ = Staff.objects.get_or_create(user=user, defaults={"role": role})
            staff_members.append(staff)

        self.stdout.write(f"✅ Создано {Staff.objects.count()} сотрудников")

        # Создаем политику штрафов
        fine_policy, _ = FinePolicy.objects.get_or_create(
            daily_rate=Decimal("10.00"),
            defaults={
                "max_fine_per_loan": Decimal("500.00"),
                "grace_period_days": 3,
            },
        )
        self.stdout.write("✅ Создана политика штрафов")

        # Создаем выдачи
        active_copies = [c for c in copies if c.status == BookCopy.Status.AVAILABLE]
        available_readers = readers[:int(len(readers) * 0.8)]

        for i in range(loans_count):
            if not active_copies or not available_readers:
                break

            copy = random.choice(active_copies)
            reader = random.choice(available_readers)
            issuer = random.choice(staff_members)

            issue_date = date.today() - timedelta(days=random.randint(1, 60))
            due_date = issue_date + timedelta(days=14)

            status_choices = [
                Loan.Status.ACTIVE,
                Loan.Status.ACTIVE,
                Loan.Status.ACTIVE,
                Loan.Status.RETURNED,
                Loan.Status.OVERDUE,
            ]
            status = random.choice(status_choices)

            return_date = None
            return_processor = None
            if status == Loan.Status.RETURNED:
                return_date = due_date - timedelta(days=random.randint(0, 5))
                return_processor = random.choice(staff_members)
                copy.status = BookCopy.Status.AVAILABLE
                copy.save()
            elif status == Loan.Status.ACTIVE:
                copy.status = BookCopy.Status.ON_LOAN
                copy.save()
            elif status == Loan.Status.OVERDUE:
                copy.status = BookCopy.Status.ON_LOAN
                copy.save()

            loan = Loan.objects.create(
                copy=copy,
                reader=reader,
                issued_by=issuer,
                issue_date=issue_date,
                due_date=due_date,
                return_date=return_date,
                return_processed_by=return_processor,
                status=status,
                renewals_count=random.randint(0, 2) if status == Loan.Status.ACTIVE else 0,
            )

            # Создаем штрафы для просроченных
            if status == Loan.Status.OVERDUE:
                days_overdue = (date.today() - due_date).days
                fine_amount = min(
                    Decimal(days_overdue) * fine_policy.daily_rate,
                    fine_policy.max_fine_per_loan,
                )
                Fine.objects.create(
                    loan=loan,
                    amount=fine_amount,
                    status=Fine.Status.UNPAID,
                )

        self.stdout.write(f"✅ Создано {Loan.objects.count()} выдач")

        # Создаем бронирования
        reserved_copies = [c for c in copies if c.status == BookCopy.Status.RESERVED]
        for i in range(reservations_count):
            if not reserved_copies or not available_readers:
                break

            copy = random.choice(reserved_copies)
            reader = random.choice(available_readers)

            Reservation.objects.create(
                copy=copy,
                reader=reader,
                expires_at=timezone.now() + timedelta(hours=48),
                status=Reservation.Status.ACTIVE,
            )

        self.stdout.write(f"✅ Создано {Reservation.objects.count()} бронирований")

        self.stdout.write(
            self.style.SUCCESS("\n✅ Тестовые данные успешно созданы!")
        )
        self.stdout.write(f"\n📊 Итого:")
        self.stdout.write(f"   • Книг: {Book.objects.count()}")
        self.stdout.write(f"   • Экземпляров: {BookCopy.objects.count()}")
        self.stdout.write(f"   • Авторов: {Author.objects.count()}")
        self.stdout.write(f"   • Издателей: {Publisher.objects.count()}")
        self.stdout.write(f"   • Категорий: {Category.objects.count()}")
        self.stdout.write(f"   • Читателей: {Reader.objects.count()}")
        self.stdout.write(f"   • Сотрудников: {Staff.objects.count()}")
        self.stdout.write(f"   • Выдач: {Loan.objects.count()}")
        self.stdout.write(f"   • Бронирований: {Reservation.objects.count()}")
        self.stdout.write(f"   • Штрафов: {Fine.objects.count()}")

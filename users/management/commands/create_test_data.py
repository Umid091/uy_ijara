from django.core.management.base import BaseCommand
from django.core.files.base import ContentFile
from users.models import User, Tariff, UserSubscription, Payment
from houses.models import House, HouseImage, Region, District
import urllib.request
import os


class Command(BaseCommand):
    help = 'Test ma\'lumotlar yaratish'

    def download_image(self, url, filename):
        """Internetdan rasm yuklab olish"""
        try:
            headers = {'User-Agent': 'Mozilla/5.0'}
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, timeout=10) as response:
                return ContentFile(response.read(), name=filename)
        except Exception as e:
            self.stdout.write(self.style.WARNING(f'    ⚠ Rasm yuklanmadi: {e}'))
            return None

    def handle(self, *args, **kwargs):

        # ── 1. Tariflar ──
        tariff_3 = Tariff.objects.filter(duration_days=3).first()
        tariff_7 = Tariff.objects.filter(duration_days=7).first()

        if not tariff_3 or not tariff_7:
            self.stdout.write(self.style.ERROR(
                'Avval: python manage.py loaddata users/fixtures/tariffs.json'
            ))
            return

        # ── 2. Regionlar ──
        toshkent  = Region.objects.filter(name='Toshkent shahri').first()
        samarqand = Region.objects.filter(name='Samarqand viloyati').first()

        if not toshkent or not samarqand:
            self.stdout.write(self.style.ERROR(
                'Avval: python manage.py loaddata houses/fixtures/regions.json'
            ))
            return

        # ── 3. Districtlar ──
        yunusobod   = District.objects.filter(name='Yunusobod tumani').first()
        chilonzor   = District.objects.filter(name='Chilonzor tumani').first()
        mirzo       = District.objects.filter(name="Mirzo Ulug'bek tumani").first()
        yakkasaroy  = District.objects.filter(name='Yakkasaroy tumani').first()
        olmazor     = District.objects.filter(name='Olmazor tumani').first()
        samarqand_t = District.objects.filter(name='Samarqand tumani').first()
        urgut       = District.objects.filter(name='Urgut tumani').first()

        # ── 4. Test userlar ──
        users_data = [
            {
                'phone': '+998901111111',
                'first_name': 'Sardor',
                'last_name': 'Karimov',
                'password': 'test1234',
                'balance': 100000,
                'tariff': tariff_7,
                'card_number': '8600111122223333',
                'card_holder': 'SARDOR KARIMOV',
                'card_expiry': '12/2027',
            },
            {
                'phone': '+998902222222',
                'first_name': 'Malika',
                'last_name': 'Yusupova',
                'password': 'test1234',
                'balance': 50000,
                'tariff': tariff_3,
                'card_number': '8600444455556666',
                'card_holder': 'MALIKA YUSUPOVA',
                'card_expiry': '06/2026',
            },
            {
                'phone': '+998903333333',
                'first_name': 'Jasur',
                'last_name': 'Toshmatov',
                'password': 'test1234',
                'balance': 0,
                'tariff': None,
                'card_number': None,
                'card_holder': None,
                'card_expiry': None,
            },
        ]

        created_users = {}
        for data in users_data:
            phone = data['phone']
            user  = User.objects.filter(phone=phone).first()

            if not user:
                user = User.objects.create_user(
                    username    = phone,
                    phone       = phone,
                    first_name  = data['first_name'],
                    last_name   = data['last_name'],
                    password    = data['password'],
                    balance     = data['balance'],
                    card_number = data['card_number'] or '',
                    card_holder = data['card_holder'] or '',
                    card_expiry = data['card_expiry'] or '',
                )
                if data['tariff']:
                    sub = UserSubscription.objects.create(
                        user   = user,
                        tariff = data['tariff'],
                    )
                    Payment.objects.create(
                        user               = user,
                        tariff             = data['tariff'],
                        subscription       = sub,
                        amount             = data['tariff'].price,
                        card_number_masked = '**** **** **** ' + (data['card_number'] or '0000')[-4:],
                        status             = Payment.Status.SUCCESS,
                    )
                self.stdout.write(self.style.SUCCESS(
                    f'  ✓ {user.get_full_name()} yaratildi'
                ))
            else:
                self.stdout.write(f'  → {phone} allaqachon mavjud')

            created_users[phone] = user

        sardor = created_users.get('+998901111111')
        malika = created_users.get('+998902222222')

        # ── 5. Rasmlar URL lari (picsum.photos — bepul placeholder) ──
        # Har bir uy uchun 3 ta rasm
        # seed raqami har safar boshqa rasm beradi
        image_sets = {
            'sardor': [
                # house_1: Yunusobod
                [
                    'https://picsum.photos/seed/house101/800/600',
                    'https://picsum.photos/seed/house102/800/600',
                    'https://picsum.photos/seed/house103/800/600',
                ],
                # house_2: Chilonzor
                [
                    'https://picsum.photos/seed/house201/800/600',
                    'https://picsum.photos/seed/house202/800/600',
                    'https://picsum.photos/seed/house203/800/600',
                ],
                # house_3: Mirzo Ulug'bek
                [
                    'https://picsum.photos/seed/house301/800/600',
                    'https://picsum.photos/seed/house302/800/600',
                    'https://picsum.photos/seed/house303/800/600',
                ],
                # house_4: Yakkasaroy
                [
                    'https://picsum.photos/seed/house401/800/600',
                    'https://picsum.photos/seed/house402/800/600',
                    'https://picsum.photos/seed/house403/800/600',
                ],
                # house_5: Olmazor
                [
                    'https://picsum.photos/seed/house501/800/600',
                    'https://picsum.photos/seed/house502/800/600',
                    'https://picsum.photos/seed/house503/800/600',
                ],
                # house_6: Yunusobod elit
                [
                    'https://picsum.photos/seed/house601/800/600',
                    'https://picsum.photos/seed/house602/800/600',
                    'https://picsum.photos/seed/house603/800/600',
                ],
                # house_7: Chilonzor arzon
                [
                    'https://picsum.photos/seed/house701/800/600',
                    'https://picsum.photos/seed/house702/800/600',
                    'https://picsum.photos/seed/house703/800/600',
                ],
            ],
            'malika': [
                # house_1: Registon
                [
                    'https://picsum.photos/seed/house801/800/600',
                    'https://picsum.photos/seed/house802/800/600',
                    'https://picsum.photos/seed/house803/800/600',
                ],
                # house_2: Universitetlar
                [
                    'https://picsum.photos/seed/house901/800/600',
                    'https://picsum.photos/seed/house902/800/600',
                    'https://picsum.photos/seed/house903/800/600',
                ],
                # house_3: Urgut bog'cha
                [
                    'https://picsum.photos/seed/house1001/800/600',
                    'https://picsum.photos/seed/house1002/800/600',
                    'https://picsum.photos/seed/house1003/800/600',
                ],
                # house_4: Shahriston
                [
                    'https://picsum.photos/seed/house1101/800/600',
                    'https://picsum.photos/seed/house1102/800/600',
                    'https://picsum.photos/seed/house1103/800/600',
                ],
                # house_5: Navruz
                [
                    'https://picsum.photos/seed/house1201/800/600',
                    'https://picsum.photos/seed/house1202/800/600',
                    'https://picsum.photos/seed/house1203/800/600',
                ],
                # house_6: Ipak yo'li
                [
                    'https://picsum.photos/seed/house1301/800/600',
                    'https://picsum.photos/seed/house1302/800/600',
                    'https://picsum.photos/seed/house1303/800/600',
                ],
            ],
        }

        # ── 6. Uylar ──
        sardor_houses = [
            {
                'region': toshkent, 'district': yunusobod,
                'street': "Amir Temur shoh ko'chasi",
                'full_address': "Amir Temur shoh ko'chasi 15-uy, 4-qavat, 12-xona",
                'price_usd': 450,
                'description': "3 xonali zamonaviy kvartira. To'liq jihozlangan. "
                               "Konditsioner, muzlatgich, kir yuvish mashinasi mavjud. "
                               "Metro bekati yaqin. Tinch mahalla.",
                'latitude': 41.2995, 'longitude': 69.2401,
            },
            {
                'region': toshkent, 'district': chilonzor,
                'street': "Bunyodkor ko'chasi",
                'full_address': "Bunyodkor ko'chasi 22-uy, 2-qavat",
                'price_usd': 300,
                'description': "2 xonali kvartira. Yangi ta'mirlangan. "
                               "Barcha kommunal xizmatlar ulangan. "
                               "Avtobus bekatiga 5 daqiqa.",
                'latitude': 41.2850, 'longitude': 69.2200,
            },
            {
                'region': toshkent, 'district': mirzo,
                'street': "Shota Rustaveli ko'chasi",
                'full_address': "Shota Rustaveli ko'chasi 8-uy, 1-qavat",
                'price_usd': 250,
                'description': "1 xonali kvartira. Yolg'iz yashash uchun ideal. "
                               "Xavfsiz qo'riqlanadigan uy. "
                               "Barcha do'konlar yaqin atrofda.",
                'latitude': 41.3100, 'longitude': 69.2600,
            },
            {
                'region': toshkent, 'district': yakkasaroy,
                'street': "Navoi ko'chasi",
                'full_address': "Navoi ko'chasi 45/3-uy, 3-qavat",
                'price_usd': 550,
                'description': "4 xonali keng kvartira. Oila uchun ideal. "
                               "Bolalar bog'chasi va maktab yaqin. "
                               "Uy eski, lekin yaxshi ta'mirlangan.",
                'latitude': 41.2900, 'longitude': 69.2700,
            },
            {
                'region': toshkent, 'district': olmazor,
                'street': "Bog'ishamol ko'chasi",
                'full_address': "Bog'ishamol ko'chasi 7-uy, 5-qavat",
                'price_usd': 350,
                'description': "2 xonali kvartira. Ko'rinish ajoyib. "
                               "Liftli bino. Internet va kabel TV ulangan. "
                               "Yaqin atrofda park bor.",
                'latitude': 41.3200, 'longitude': 69.2100,
            },
            {
                'region': toshkent, 'district': yunusobod,
                'street': "Mustakillik ko'chasi",
                'full_address': "Mustakillik ko'chasi 120-uy, 6-qavat",
                'price_usd': 600,
                'description': "3 xonali elit kvartira. Yangi bino (2022-yil). "
                               "Yerosti avtoturargoh. 24/7 qo'riqlash. "
                               "Zamonaviy mebel va jihozlar bilan.",
                'latitude': 41.3050, 'longitude': 69.2450,
            },
            {
                'region': toshkent, 'district': chilonzor,
                'street': "Qo'yliq ko'chasi",
                'full_address': "Qo'yliq ko'chasi 33-uy, 2-qavat",
                'price_usd': 200,
                'description': "1 xonali arzon kvartira. Talabalar uchun ideal. "
                               "Kommunal xarajatlar arzon. "
                               "Avtobus va metro yaqin.",
                'latitude': 41.2780, 'longitude': 69.2300,
            },
        ]

        malika_houses = [
            {
                'region': samarqand, 'district': samarqand_t,
                'street': "Registon ko'chasi",
                'full_address': "Registon ko'chasi 5-uy, 2-qavat",
                'price_usd': 280,
                'description': "2 xonali kvartira. Samarqand markazida. "
                               "Turistik joylar yaqin. Tinch mahalla. "
                               "Internet va barcha sharoitlar mavjud.",
                'latitude': 39.6542, 'longitude': 66.9597,
            },
            {
                'region': samarqand, 'district': samarqand_t,
                'street': "Universitetlar ko'chasi",
                'full_address': "Universitetlar ko'chasi 18-uy, 3-qavat",
                'price_usd': 180,
                'description': "1 xonali kvartira. SamDU yaqin. "
                               "Talabalar uchun qulay. "
                               "Arzon narx, yaxshi sharoit.",
                'latitude': 39.6600, 'longitude': 66.9650,
            },
            {
                'region': samarqand, 'district': urgut,
                'street': "Bog'cha ko'chasi",
                'full_address': "Bog'cha ko'chasi 3-uy, 1-qavat",
                'price_usd': 150,
                'description': "2 xonali hovlili uy. Katta bog'cha bor. "
                               "Tabiat qo'ynida. Shahardan 20 km. "
                               "Oziq-ovqat arzon.",
                'latitude': 39.4000, 'longitude': 66.8500,
            },
            {
                'region': samarqand, 'district': samarqand_t,
                'street': "Shahriston ko'chasi",
                'full_address': "Shahriston ko'chasi 92-uy, 4-qavat",
                'price_usd': 320,
                'description': "3 xonali kvartira. Yangi ta'mirlangan. "
                               "Zamonaviy mebel. Konditsioner bor. "
                               "Bozor va maktab yaqin.",
                'latitude': 39.6580, 'longitude': 66.9620,
            },
            {
                'region': samarqand, 'district': samarqand_t,
                'street': "Navruz ko'chasi",
                'full_address': "Navruz ko'chasi 11-uy, 2-qavat",
                'price_usd': 400,
                'description': "3 xonali keng kvartira. Oila uchun. "
                               "Bolalar bog'chasi yonida. "
                               "Xavfsiz va tinch mahalla.",
                'latitude': 39.6510, 'longitude': 66.9570,
            },
            {
                'region': samarqand, 'district': urgut,
                'street': "Ipak yo'li ko'chasi",
                'full_address': "Ipak yo'li ko'chasi 67-uy, 1-qavat",
                'price_usd': 220,
                'description': "2 xonali uy. Ipak yo'li yaqinida. "
                               "Katta xovli. Avtoturargoh bor. "
                               "Tinch va ozoda joy.",
                'latitude': 39.4100, 'longitude': 66.8600,
            },
        ]

        # ── 7. Uylarni va rasmlarni yaratish ──
        self.stdout.write('')
        self.stdout.write('Uylar va rasmlar qo\'shilmoqda...')
        self.stdout.write('(Rasmlar internetdan yuklanadi, biroz vaqt ketadi...)')
        self.stdout.write('')

        def create_houses_with_images(user, houses_data, img_sets, label):
            count = 0
            for i, data in enumerate(houses_data):
                if House.objects.filter(
                    owner=user,
                    full_address=data['full_address']
                ).exists():
                    self.stdout.write(f'    → {data["full_address"][:40]}... allaqachon mavjud')
                    continue

                house = House.objects.create(
                    owner        = user,
                    region       = data['region'],
                    district     = data['district'],
                    street       = data['street'],
                    full_address = data['full_address'],
                    price_usd    = data['price_usd'],
                    description  = data['description'],
                    latitude     = data.get('latitude'),
                    longitude    = data.get('longitude'),
                    is_active    = True,
                )

                # Rasmlarni yuklash
                urls = img_sets[i] if i < len(img_sets) else []
                img_count = 0
                for j, url in enumerate(urls):
                    filename = f'house_{house.pk}_img_{j+1}.jpg'
                    img_file = self.download_image(url, filename)
                    if img_file:
                        HouseImage.objects.create(
                            house   = house,
                            image   = img_file,
                            is_main = (j == 0),
                            order   = j,
                        )
                        img_count += 1

                count += 1
                self.stdout.write(self.style.SUCCESS(
                    f'    ✓ [{label}] {house.full_address[:45]}... '
                    f'${house.price_usd} | {img_count} rasm'
                ))
            return count

        sardor_count = create_houses_with_images(
            sardor, sardor_houses, image_sets['sardor'], 'Sardor'
        )
        malika_count = create_houses_with_images(
            malika, malika_houses, image_sets['malika'], 'Malika'
        )

        # ── 8. Natija ──
        self.stdout.write('')
        self.stdout.write(self.style.SUCCESS('═' * 55))
        self.stdout.write(self.style.SUCCESS('✅ Hammasi tayyor!'))
        self.stdout.write('')
        self.stdout.write('  👤 Foydalanuvchilar:')
        self.stdout.write('  📱 +998901111111 | test1234 | 7 kunlik | 7 uy')
        self.stdout.write('  📱 +998902222222 | test1234 | 3 kunlik | 6 uy')
        self.stdout.write('  📱 +998903333333 | test1234 | tarif yo\'q')
        self.stdout.write('')
        self.stdout.write(f'  🏠 Jami yangi uylar: {sardor_count + malika_count} ta')
        self.stdout.write('  🖼  Har bir uyda 3 ta rasm')
        self.stdout.write(self.style.SUCCESS('═' * 55))
"""Populate name_ru and name_en for Region and District."""
from django.core.management.base import BaseCommand

from houses.models import District, Region


REGIONS = {
    'Andijon viloyati'             : ('Андижанская область',         'Andijan Region'),
    'Buxoro viloyati'              : ('Бухарская область',           'Bukhara Region'),
    "Farg'ona viloyati"            : ('Ферганская область',          'Fergana Region'),
    'Jizzax viloyati'              : ('Джизакская область',          'Jizzakh Region'),
    'Namangan viloyati'            : ('Наманганская область',        'Namangan Region'),
    'Navoiy viloyati'              : ('Навоийская область',          'Navoiy Region'),
    'Qashqadaryo viloyati'         : ('Кашкадарьинская область',     'Kashkadarya Region'),
    "Qoraqalpog'iston Respublikasi": ('Республика Каракалпакстан',   'Republic of Karakalpakstan'),
    'Samarqand viloyati'           : ('Самаркандская область',       'Samarkand Region'),
    'Sirdaryo viloyati'            : ('Сырдарьинская область',       'Syrdarya Region'),
    'Surxondaryo viloyati'         : ('Сурхандарьинская область',    'Surkhandarya Region'),
    'Toshkent shahri'              : ('город Ташкент',               'Tashkent City'),
    'Toshkent viloyati'            : ('Ташкентская область',         'Tashkent Region'),
    'Xorazm viloyati'              : ('Хорезмская область',          'Khorezm Region'),
}

DISTRICTS = {
    # Andijon
    'Andijon tumani'        : ('Андижанский район',         'Andijan District'),
    'Asaka tumani'          : ('Асакинский район',          'Asaka District'),
    'Baliqchi tumani'       : ('Балыкчинский район',        'Baliqchi District'),
    "Bo'z tumani"           : ('Бузский район',             'Boz District'),
    'Izboskan tumani'       : ('Избасканский район',        'Izboskan District'),
    'Jalaquduq tumani'      : ('Джалакудукский район',      'Jalaquduq District'),
    'Marhamat tumani'       : ('Мархаматский район',        'Marhamat District'),
    "Oltinko'l tumani"      : ('Алтынкульский район',       'Oltinko\'l District'),
    'Paxtaobod tumani'      : ('Пахтаабадский район',       'Pakhtaobod District'),
    'Shahrixon tumani'      : ('Шахриханский район',        'Shahrikhan District'),
    "Ulug'nor tumani"       : ('Улугнорский район',         'Ulug\'nor District'),
    "Xo'jaobod tumani"      : ('Ходжаабадский район',       'Xo\'jaobod District'),
    # Buxoro
    'Buxoro tumani'         : ('Бухарский район',           'Bukhara District'),
    "G'ijduvon tumani"      : ('Гиждуванский район',        'G\'ijduvon District'),
    'Kogon tumani'          : ('Каганский район',           'Kogon District'),
    'Qorovulbozor tumani'   : ('Караулбазарский район',     'Qorovulbozor District'),
    'Romitan tumani'        : ('Ромитанский район',         'Romitan District'),
    'Shofirkon tumani'      : ('Шофирканский район',        'Shofirkon District'),
    'Vobkent tumani'        : ('Вабкентский район',         'Vobkent District'),
    # Farg'ona
    "Bag'dod tumani"        : ('Багдадский район',          'Bag\'dod District'),
    'Beshariq tumani'       : ('Бешарыкский район',         'Beshariq District'),
    'Buvayda tumani'        : ('Бувайдинский район',        'Buvayda District'),
    "Dang'ara tumani"       : ('Дангаринский район',        'Dang\'ara District'),
    "Farg'ona tumani"       : ('Ферганский район',          'Fergana District'),
    "Marg'ilon tumani"      : ('Маргиланский район',        'Marg\'ilon District'),
    'Oltiariq tumani'       : ('Алтыарыкский район',        'Oltiariq District'),
    "Qo'shtepa tumani"      : ('Кыштепинский район',        'Qo\'shtepa District'),
    'Quva tumani'           : ('Кувинский район',           'Quva District'),
    'Rishton tumani'        : ('Риштанский район',          'Rishton District'),
    "So'x tumani"           : ('Сохский район',             'So\'x District'),
    'Toshloq tumani'        : ('Ташлакский район',          'Toshloq District'),
    "Uchko'prik tumani"     : ('Учкуприкский район',        'Uchko\'prik District'),
    'Yozyovon tumani'       : ('Язъяванский район',         'Yozyovon District'),
    # Jizzax
    'Arnasoy tumani'        : ('Арнасайский район',         'Arnasoy District'),
    "Do'stlik tumani"       : ('Дустликский район',         'Do\'stlik District'),
    'Forish tumani'         : ('Фаришский район',           'Forish District'),
    "G'allaorol tumani"     : ('Галляаральский район',      'G\'allaorol District'),
    'Jizzax tumani'         : ('Джизакский район',          'Jizzakh District'),
    "Mirzacho'l tumani"     : ('Мирзачульский район',       'Mirzacho\'l District'),
    'Sharof Rashidov tumani': ('Шараф-Рашидовский район',   'Sharof Rashidov District'),
    'Yangiobod tumani'      : ('Янгиабадский район',        'Yangiobod District'),
    'Zarbdor tumani'        : ('Зарбдарский район',         'Zarbdor District'),
    'Zomin tumani'          : ('Заминский район',           'Zomin District'),
    # Namangan
    'Chortoq tumani'        : ('Чартакский район',          'Chortoq District'),
    'Chust tumani'          : ('Чустский район',            'Chust District'),
    'Kosonsoy tumani'       : ('Касансайский район',        'Kosonsoy District'),
    'Mingbuloq tumani'      : ('Мингбулакский район',       'Mingbuloq District'),
    'Namangan tumani'       : ('Наманганский район',        'Namangan District'),
    'Norin tumani'          : ('Нарынский район',           'Norin District'),
    'Pop tumani'            : ('Папский район',             'Pop District'),
    "To'raqo'rg'on tumani"  : ('Туракурганский район',      'To\'raqo\'rg\'on District'),
    'Uychi tumani'          : ('Уйчинский район',           'Uychi District'),
    "Yangiqo'rg'on tumani"  : ('Янгикурганский район',      'Yangiqo\'rg\'on District'),
    # Navoiy
    'Karmana tumani'        : ('Карманинский район',        'Karmana District'),
    'Konimex tumani'        : ('Канимехский район',         'Konimex District'),
    'Navbahor tumani'       : ('Навбахорский район',        'Navbahor District'),
    'Navoiy tumani'         : ('Навоийский район',          'Navoiy District'),
    'Nurota tumani'         : ('Нуратинский район',         'Nurota District'),
    'Qiziltepa tumani'      : ('Кызылтепинский район',      'Qiziltepa District'),
    'Tomdi tumani'          : ('Тамдынский район',          'Tomdi District'),
    'Uchquduq tumani'       : ('Учкудукский район',         'Uchquduq District'),
    # Qashqadaryo
    'Chiroqchi tumani'      : ('Чиракчинский район',        'Chiroqchi District'),
    "G'uzor tumani"         : ('Гузарский район',           'G\'uzor District'),
    'Kasbi tumani'          : ('Касбийский район',          'Kasbi District'),
    'Kitob tumani'          : ('Китабский район',           'Kitob District'),
    'Koson tumani'          : ('Касанский район',           'Koson District'),
    'Muborak tumani'        : ('Мубарекский район',         'Muborak District'),
    'Nishon tumani'         : ('Нишанский район',           'Nishon District'),
    'Qamashi tumani'        : ('Камашинский район',         'Qamashi District'),
    'Qarshi tumani'         : ('Каршинский район',          'Qarshi District'),
    'Shahrisabz tumani'     : ('Шахрисабзский район',       'Shahrisabz District'),
    "Yakkabog' tumani"      : ('Яккабагский район',         'Yakkabog\' District'),
    # Qoraqalpog'iston
    'Amudaryo tumani'       : ('Амударьинский район',       'Amudaryo District'),
    'Beruniy tumani'        : ('Берунийский район',         'Beruniy District'),
    'Chimboy tumani'        : ('Чимбайский район',          'Chimboy District'),
    "Ellikqal'a tumani"     : ('Элликкалинский район',      'Ellikqal\'a District'),
    'Kegeyli tumani'        : ('Кегейлийский район',        'Kegeyli District'),
    "Mo'ynoq tumani"        : ('Муйнакский район',          'Mo\'ynoq District'),
    'Nukus tumani'          : ('Нукусский район',           'Nukus District'),
    "Qo'ng'irot tumani"     : ('Кунгирадский район',        'Qo\'ng\'irot District'),
    "Taxtako'pir tumani"    : ('Тахтакупырский район',      'Taxtako\'pir District'),
    "To'rtko'l tumani"      : ('Турткульский район',        'To\'rtko\'l District'),
    "Xo'jayli tumani"       : ('Ходжейлийский район',       'Xo\'jayli District'),
    # Samarqand
    "Bulung'ur tumani"      : ('Булунгурский район',        'Bulung\'ur District'),
    'Ishtixon tumani'       : ('Иштыханский район',         'Ishtixon District'),
    'Jomboy tumani'         : ('Джамбайский район',         'Jomboy District'),
    "Kattaqo'rg'on tumani"  : ('Каттакурганский район',     'Kattaqo\'rg\'on District'),
    'Narpay tumani'         : ('Нарпайский район',          'Narpay District'),
    "Pastdarg'om tumani"    : ('Пастдаргомский район',      'Pastdarg\'om District'),
    'Payariq tumani'        : ('Паярыкский район',          'Payariq District'),
    'Samarqand tumani'      : ('Самаркандский район',       'Samarkand District'),
    'Urgut tumani'          : ('Ургутский район',           'Urgut District'),
    # Sirdaryo
    'Boyovut tumani'        : ('Баяутский район',           'Boyovut District'),
    'Guliston tumani'       : ('Гулистанский район',        'Guliston District'),
    'Mirzaobod tumani'      : ('Мирзаабадский район',       'Mirzaobod District'),
    'Oqoltin tumani'        : ('Акалтынский район',         'Oqoltin District'),
    'Sardoba tumani'        : ('Сардобинский район',        'Sardoba District'),
    'Sayxunobod tumani'     : ('Сайхунабадский район',      'Sayxunobod District'),
    'Shirin tumani'         : ('Ширинский район',           'Shirin District'),
    'Xovos tumani'          : ('Хавастский район',          'Xovos District'),
    'Yangiyer tumani'       : ('Янгиерский район',          'Yangiyer District'),
    # Surxondaryo
    'Angor tumani'          : ('Ангорский район',           'Angor District'),
    'Boysun tumani'         : ('Байсунский район',          'Boysun District'),
    'Denov tumani'          : ('Денауский район',           'Denov District'),
    "Jarqo'rg'on tumani"    : ('Джаркурганский район',      'Jarqo\'rg\'on District'),
    'Muzrabot tumani'       : ('Музрабатский район',        'Muzrabot District'),
    'Qiziriq tumani'        : ('Кизирыкский район',         'Qiziriq District'),
    'Sariosiyo tumani'      : ('Сариасийский район',        'Sariosiyo District'),
    'Sherobod tumani'       : ('Шерабадский район',         'Sherobod District'),
    "Sho'rchi tumani"       : ('Шурчинский район',          'Sho\'rchi District'),
    'Termiz tumani'         : ('Термезский район',          'Termez District'),
    'Uzun tumani'           : ('Узунский район',            'Uzun District'),
    # Toshkent shahri
    'Bektemir tumani'       : ('Бектемирский район',        'Bektemir District'),
    'Chilonzor tumani'      : ('Чиланзарский район',        'Chilonzor District'),
    'Mirobod tumani'        : ('Мирабадский район',         'Mirobod District'),
    "Mirzo Ulug'bek tumani" : ('Мирзо-Улугбекский район',   'Mirzo Ulug\'bek District'),
    'Olmazor tumani'        : ('Алмазарский район',         'Olmazor District'),
    'Sergeli tumani'        : ('Сергелийский район',        'Sergeli District'),
    'Shayxontohur tumani'   : ('Шайхантахурский район',     'Shayxontohur District'),
    'Uchtepa tumani'        : ('Учтепинский район',         'Uchtepa District'),
    'Yakkasaroy tumani'     : ('Яккасарайский район',       'Yakkasaroy District'),
    'Yunusobod tumani'      : ('Юнусабадский район',        'Yunusobod District'),
    # Toshkent viloyati
    'Bekabad tumani'        : ('Бекабадский район',         'Bekabad District'),
    "Bo'ka tumani"          : ('Букинский район',           'Bo\'ka District'),
    'Chinoz tumani'         : ('Чиназский район',           'Chinoz District'),
    "O'rtachirchiq tumani"  : ('Уртачирчикский район',      'O\'rtachirchiq District'),
    'Ohangaron tumani'      : ('Ахангаранский район',       'Ohangaron District'),
    'Parkent tumani'        : ('Паркентский район',         'Parkent District'),
    'Piskent tumani'        : ('Пискентский район',         'Piskent District'),
    'Qibray tumani'         : ('Кибрайский район',          'Qibray District'),
    "Yangiyo'l tumani"      : ('Янгиюльский район',         'Yangiyo\'l District'),
    'Zangiota tumani'       : ('Зангиатинский район',       'Zangiota District'),
    # Xorazm
    "Bog'ot tumani"         : ('Багатский район',           'Bog\'ot District'),
    'Gurlan tumani'         : ('Гурленский район',          'Gurlan District'),
    'Shovot tumani'         : ('Шаватский район',           'Shovot District'),
    'Urganch tumani'        : ('Ургенчский район',          'Urganch District'),
    'Xiva tumani'           : ('Хивинский район',           'Khiva District'),
    'Xonqa tumani'          : ('Ханкинский район',          'Xonqa District'),
    'Yangiariq tumani'      : ('Янгиарыкский район',        'Yangiariq District'),
    'Yangibozor tumani'     : ('Янгибазарский район',       'Yangibozor District'),
}


class Command(BaseCommand):
    help = "Fill name_ru and name_en for regions and districts."

    def handle(self, *args, **opts):
        rcount = 0
        for r in Region.objects.all():
            tr = REGIONS.get(r.name)
            if not tr:
                continue
            r.name_ru, r.name_en = tr
            r.save(update_fields=['name_ru', 'name_en'])
            rcount += 1
        self.stdout.write(self.style.SUCCESS(f"Updated {rcount} regions"))

        dcount = 0
        for d in District.objects.all():
            tr = DISTRICTS.get(d.name)
            if not tr:
                continue
            d.name_ru, d.name_en = tr
            d.save(update_fields=['name_ru', 'name_en'])
            dcount += 1
        self.stdout.write(self.style.SUCCESS(f"Updated {dcount} districts"))

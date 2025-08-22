import random
import json
from typing import Dict, List, Set, Tuple, Optional
from dataclasses import dataclass, field
from enum import Enum


class Habitat(Enum):
    """Среды обитания существ"""
    # Детализация наземной среды
    FOREST_TROPICAL = "Тропический лес"
    GRASSLAND = "Луговое"
    MOUNTAIN = "Горное"
    # Прочие среды
    AQUATIC = "Водное"
    AERIAL = "Воздушное"
    UNDERGROUND = "Подземное"
    AMPHIBIOUS = "Амфибия"
    COSMIC = "Космическое"
    VOLCANIC = "Вулканическое"
    ARCTIC = "Арктическое"
    DESERT = "Пустынное"
    SWAMP = "Болотное"


class CreatureType(Enum):
    """Типы существ"""
    MAMMAL = "Млекопитающее"
    REPTILE = "Рептилия"
    BIRD = "Птица"
    FISH = "Рыба"
    INSECT = "Насекомое"
    AMPHIBIAN = "Амфибия"
    FANTASY = "Фэнтези"
    CRYSTAL = "Кристаллическое"
    MECHANICAL = "Механическое"
    ELEMENTAL = "Элементальное"
    HYBRID = "Гибрид"


class Size(Enum):
    """Размеры существ"""
    MICROSCOPIC = "Микроскопическое"
    TINY = "Крошечное"
    SMALL = "Маленькое"
    MEDIUM = "Среднее"
    LARGE = "Большое"
    HUGE = "Огромное"
    COLOSSAL = "Колоссальное"


@dataclass
class CreatureCharacteristics:
    """Характеристики существа"""
    habitat: Habitat
    creature_type: CreatureType
    size: Size
    surface: str
    form_rules: str
    head_description: str
    body_features: List[str] = field(default_factory=list)
    appendages: List[str] = field(default_factory=list)
    special_abilities: List[str] = field(default_factory=list)
    coloration: List[str] = field(default_factory=list)
    behavior_traits: List[str] = field(default_factory=list)
    environmental_adaptations: List[str] = field(default_factory=list)


class CreatureGenerator:
    """Генератор существ с логическими ограничениями"""
    
    def __init__(self):
        self._initialize_data()
        self._setup_constraints()
        # Подготовка case-insensitive словаря переводов
        self._build_ci_translations()
        # Стадии развития и модификаторы промптов из глобальных настроек
        try:
            from config.settings import CREATURE_LIFE_STAGES, STAGE_PROMPT_MODIFIERS
            self.life_stages = CREATURE_LIFE_STAGES
            self.stage_modifiers = STAGE_PROMPT_MODIFIERS
        except Exception:
            # Фолбэк на случай отсутствия настроек
            self.life_stages = {
                "egg": {"ru": "яйцо", "en": "egg"},
                "baby": {"ru": "детёныш", "en": "hatchling"},
                "adult": {"ru": "взрослая особь", "en": "adult"}
            }
            self.stage_modifiers = {
                "egg": {"ru": "одиночное яйцо", "en": "single egg"},
                "baby": {"ru": "умилительные пропорции", "en": "cute proportions"},
                "adult": {"ru": "полностью сформировавшиеся признаки", "en": "fully developed traits"}
            }
    
    def _initialize_data(self):
        """Инициализация данных о существах"""
        
        # Характеристики по средам обитания
        self.habitat_data = {
            Habitat.FOREST_TROPICAL: {
                "types": [CreatureType.MAMMAL, CreatureType.REPTILE, CreatureType.FANTASY, CreatureType.HYBRID],
                "surfaces": ["Шерсть", "Чешуя", "Кожа", "Перья", "Экзоскелет", "Панцирь"],
                "form_rules": "Любая форма, кроме плавников",
                "forbidden_features": ["Жабры", "Плавники", "Водные мембраны"],
                "preferred_features": ["Конечности", "Хвост", "Уши"]
            },
            Habitat.GRASSLAND: {
                "types": [CreatureType.MAMMAL, CreatureType.REPTILE, CreatureType.FANTASY, CreatureType.HYBRID],
                "surfaces": ["Шерсть", "Чешуя", "Кожа", "Перья", "Экзоскелет", "Панцирь"],
                "form_rules": "Любая форма, кроме плавников",
                "forbidden_features": ["Жабры", "Плавники", "Водные мембраны"],
                "preferred_features": ["Конечности", "Хвост", "Уши"]
            },
            Habitat.MOUNTAIN: {
                "types": [CreatureType.MAMMAL, CreatureType.REPTILE, CreatureType.FANTASY, CreatureType.HYBRID],
                "surfaces": ["Шерсть", "Чешуя", "Кожа", "Перья", "Экзоскелет", "Панцирь"],
                "form_rules": "Любая форма, кроме плавников",
                "forbidden_features": ["Жабры", "Плавники", "Водные мембраны"],
                "preferred_features": ["Конечности", "Хвост", "Уши"]
            },
            Habitat.AQUATIC: {
                "types": [CreatureType.FISH, CreatureType.FANTASY, CreatureType.AMPHIBIAN, CreatureType.HYBRID],
                "surfaces": ["Чешуя", "Гладкая кожа", "Слизь", "Кристаллы", "Биолюминесцентная кожа"],
                "form_rules": "Без крыльев и перьев, с плавательными приспособлениями",
                "forbidden_features": ["Крылья", "Перья", "Сухопутные конечности"],
                "preferred_features": ["Плавники", "Жабры", "Хвостовой плавник", "Боковая линия"]
            },
            Habitat.AERIAL: {
                "types": [CreatureType.BIRD, CreatureType.INSECT, CreatureType.FANTASY, CreatureType.HYBRID],
                "surfaces": ["Перья", "Крылья", "Легкий экзоскелет", "Мембраны"],
                "form_rules": "Обязательны крылья, допустимы перья",
                "forbidden_features": ["Тяжелый панцирь", "Водные приспособления"],
                "preferred_features": ["Крылья", "Перья", "Легкие кости", "Аэродинамическая форма"]
            },
            Habitat.UNDERGROUND: {
                "types": [CreatureType.INSECT, CreatureType.REPTILE, CreatureType.MAMMAL, CreatureType.HYBRID],
                "surfaces": ["Гладкая кожа", "Панцирь", "Шипы", "Твердая чешуя"],
                "form_rules": "Без крыльев, предпочтительно панцирь",
                "forbidden_features": ["Крылья", "Перья", "Светлые цвета"],
                "preferred_features": ["Копательные конечности", "Усики", "Темная окраска"]
            },
            Habitat.AMPHIBIOUS: {
                "types": [CreatureType.AMPHIBIAN, CreatureType.FANTASY, CreatureType.HYBRID],
                "surfaces": ["Слизь", "Кожа", "Легкая чешуя", "Водонепроницаемая кожа"],
                "form_rules": "Без крыльев, с плавательными конечностями",
                "forbidden_features": ["Крылья", "Тяжелый панцирь"],
                "preferred_features": ["Перепонки", "Жабры и легкие", "Влажная кожа"]
            },
            Habitat.COSMIC: {
                "types": [CreatureType.FANTASY, CreatureType.CRYSTAL, CreatureType.ELEMENTAL, CreatureType.HYBRID],
                "surfaces": ["Кристаллы", "Металл", "Энергетическая оболочка", "Космическая материя"],
                "form_rules": "Допустимы любые формы тела",
                "forbidden_features": [],
                "preferred_features": ["Энергетические поля", "Кристаллические структуры", "Необычные формы"]
            },
            Habitat.VOLCANIC: {
                "types": [CreatureType.REPTILE, CreatureType.FANTASY, CreatureType.ELEMENTAL, CreatureType.HYBRID],
                "surfaces": ["Огнеупорная чешуя", "Лавовая кожа", "Теплоизоляционный панцирь"],
                "form_rules": "Устойчивость к высоким температурам",
                "forbidden_features": ["Водные приспособления", "Холодолюбивые черты"],
                "preferred_features": ["Тепловые рецепторы", "Огнестойкие покровы", "Темная окраска"]
            },
            Habitat.ARCTIC: {
                "types": [CreatureType.MAMMAL, CreatureType.BIRD, CreatureType.FANTASY],
                "surfaces": ["Густой мех", "Теплые перья", "Жировая прослойка", "Плотная кожа"],
                "form_rules": "Адаптация к холоду",
                "forbidden_features": ["Тропические черты", "Теплолюбивые адаптации"],
                "preferred_features": ["Густой мех", "Жировая прослойка", "Компактная форма"]
            },
            Habitat.DESERT: {
                "types": [CreatureType.REPTILE, CreatureType.MAMMAL, CreatureType.INSECT],
                "surfaces": ["Сухая чешуя", "Песчаная кожа", "Водоудерживающая кожа"],
                "form_rules": "Адаптация к засухе",
                "forbidden_features": ["Водные приспособления", "Влажные покровы"],
                "preferred_features": ["Водоудерживающие механизмы", "Песочная окраска", "Эффективная терморегуляция"]
            },
            Habitat.SWAMP: {
                "types": [CreatureType.AMPHIBIAN, CreatureType.REPTILE, CreatureType.FANTASY],
                "surfaces": ["Влажная кожа", "Слизь", "Водонепроницаемая чешуя"],
                "form_rules": "Адаптация к влажной среде",
                "forbidden_features": ["Сухие покровы", "Пустынные адаптации"],
                "preferred_features": ["Перепонки", "Влажная кожа", "Болотная окраска"]
            }
        }
        
        # Размеры и их характеристики
        self.size_characteristics = {
            Size.MICROSCOPIC: {"speed": "Очень медленное", "strength": "Минимальная", "visibility": "Почти невидимое"},
            Size.TINY: {"speed": "Быстрое", "strength": "Слабая", "visibility": "Маленькое"},
            Size.SMALL: {"speed": "Очень быстрое", "strength": "Умеренная", "visibility": "Заметное"},
            Size.MEDIUM: {"speed": "Среднее", "strength": "Средняя", "visibility": "Обычное"},
            Size.LARGE: {"speed": "Медленное", "strength": "Сильная", "visibility": "Крупное"},
            Size.HUGE: {"speed": "Очень медленное", "strength": "Очень сильная", "visibility": "Огромное"},
            Size.COLOSSAL: {"speed": "Крайне медленное", "strength": "Колоссальная", "visibility": "Гигантское"}
        }
        
        # Детальные характеристики головы
        self.head_variants = {
            "eyes": [
                "Одна пара круглых глаз",
                "Три глаза треугольником",
                "Множество маленьких глаз",
                "Большие светящиеся глаза",
                "Глаза с вертикальными зрачками",
                "Сложные фасеточные глаза",
                "Глаза с биолюминесценцией",
                "Глаза с тепловым зрением"
            ],
            "mouths": [
                "Клыкастая пасть",
                "Клюв с острыми краями",
                "Мягкие губы",
                "Хоботок для сосания",
                "Челюсти с множественными рядами зубов",
                "Ротовой аппарат с хелицерами",
                "Круглый рот с присосками",
                "Многочисленные щупальца вокруг рта",
                "Грызущие резцы"
            ],
            "appendages": [
                "Длинные усы",
                "Антенны с чувствительными рецепторами",
                "Рога различной формы",
                "Бивни",
                "Грива",
                "Длинные уши",
                "Гребень на голове",
                "Бородавки и наросты",
                "Кристаллические выросты",
                "Энергетические коронки",
                "Биолюминесцентные органы"
            ]
        }
        
        # Характеристики тела
        self.body_features = {
            "limbs": [
                "Четыре конечности с когтями",
                "Четыре конечности с копытами",
                "Четыре конечности с втяжными когтями",
                "Шесть конечностей как у насекомого",
                "Восемь щупалец",
                "Щупальца с присосками",
                "Крылья и две ноги",
                "Передние клешни",
                "Длинные сильные ноги",
                "Плавники и хвост",
                "Множественные придатки",
                "Энергетические конечности",
                "Кристаллические выросты"
            ],
            "torso": [
                "Сегментированное тело",
                "Гибкий позвоночник",
                "Бронированная грудь",
                "Прозрачные участки",
                "Биолюминесцентные полосы",
                "Кристаллические включения",
                "Энергетические узоры",
                "Множественные сердца"
            ],
            "tail": [
                "Длинный хвост с чешуей",
                "Хвост с ядовитым жалом",
                "Пушистый хвост",
                "Хвост-плавник",
                "Хвост с биолюминесценцией",
                "Кристаллический хвост",
                "Энергетический хвост",
                "Хвост с множественными отростками"
            ]
        }
        
        # Специальные способности
        self.special_abilities = {
            "combat": [
                "Ядовитые железы",
                "Электрические разряды",
                "Кислотные выделения",
                "Огненное дыхание",
                "Ледяные кристаллы",
                "Психические атаки",
                "Клонирование",
                "Телепортация",
                "Выброс чернил",
                "Сильный прикус",
                "Удар клешнями"
            ],
            "defense": [
                "Камуфляж",
                "Бронированная кожа",
                "Регенерация",
                "Невидимость",
                "Энергетический щит",
                "Кристаллическая броня",
                "Биолюминесцентное отвлечение",
                "Множественные жизни",
                "Сворачивание в клубок",
                "Флуоресценция в УФ"
            ],
            "movement": [
                "Полет",
                "Плавание",
                "Копание",
                "Телепортация",
                "Планирование",
                "Быстрое бегание",
                "Прыжки",
                "Ползание по стенам",
                "Бесшумный полет",
                "Боковое передвижение"
            ]
        }
        
        # Цветовые схемы
        self.coloration_schemes = {
            "natural": ["Коричневый", "Зеленый", "Серый", "Черный", "Белый", "Рыжий"],
            "bright": ["Красный", "Оранжевый", "Желтый", "Розовый", "Фиолетовый", "Голубой"],
            "metallic": ["Золотой", "Серебряный", "Бронзовый", "Медный", "Платиновый"],
            "crystal": ["Прозрачный", "Радужный", "Кристаллический", "Биолюминесцентный"],
            "dark": ["Черный", "Темно-синий", "Темно-фиолетовый", "Темно-зеленый"],
            "camouflage": ["Песочный", "Лесной", "Снежный", "Болотный", "Скальный"]
        }
        
        # Поведенческие черты
        self.behavior_traits = [
            "Агрессивный охотник",
            "Мирный травоядный",
            "Социальное существо",
            "Одиночка",
            "Ночной образ жизни",
            "Дневной образ жизни",
            "Территориальный",
            "Кочевой",
            "Интеллектуальный",
            "Инстинктивный",
            "Любопытный",
            "Осторожный",
            "Игривый",
            "Серьезный",
            "Хитрый",
            "Скрытный",
            "Засадный хищник",
            "Пугливый",
            "Стадное поведение"
        ]
        
        # Экологические адаптации
        self.environmental_adaptations = {
            Habitat.FOREST_TROPICAL: [
                "Эффективная терморегуляция",
                "Развитые органы чувств",
                "Адаптация к различным ландшафтам",
                "Эффективные конечности для передвижения"
            ],
            Habitat.GRASSLAND: [
                "Эффективная терморегуляция",
                "Развитые органы чувств",
                "Адаптация к различным ландшафтам",
                "Эффективные конечности для передвижения"
            ],
            Habitat.MOUNTAIN: [
                "Эффективная терморегуляция",
                "Развитые органы чувств",
                "Адаптация к различным ландшафтам",
                "Эффективные конечности для передвижения"
            ],
            Habitat.AQUATIC: [
                "Жабры для дыхания",
                "Плавательный пузырь",
                "Боковая линия для ориентации",
                "Гидродинамическая форма тела"
            ],
            Habitat.AERIAL: [
                "Полые кости для легкости",
                "Развитые мышцы крыльев",
                "Острое зрение",
                "Аэродинамическая форма"
            ],
            Habitat.UNDERGROUND: [
                "Копательные конечности",
                "Развитое обоняние",
                "Сниженное зрение",
                "Адаптация к темноте"
            ],
            Habitat.AMPHIBIOUS: [
                "Двойное дыхание",
                "Влажная кожа",
                "Перепонки",
                "Адаптация к двум средам"
            ],
            Habitat.COSMIC: [
                "Независимость от кислорода",
                "Радиационная устойчивость",
                "Энергетическая подпитка",
                "Космическая навигация"
            ]
        }

        # Словари для перевода на английский
        self.english_translations = {
            # Среды обитания
            "Тропический лес": "tropical forest", "Луговое": "grassland", "Горное": "mountain",
            "Водное": "aquatic", "Воздушное": "aerial", 
            "Подземное": "underground", "Амфибия": "amphibious", "Космическое": "cosmic",
            "Вулканическое": "volcanic", "Арктическое": "arctic", "Пустынное": "desert", "Болотное": "swamp",
            
            # Типы существ
            "Млекопитающее": "mammal", "Рептилия": "reptile", "Птица": "bird", "Рыба": "fish",
            "Насекомое": "insect", "Амфибия": "amphibian", "Фэнтези": "fantasy hybrid",
            "Кристаллическое": "crystalline", "Механическое": "mechanical", "Элементальное": "elemental",
            "Гибрид": "hybrid",
            
            # Размеры
            "Микроскопическое": "microscopic", "Крошечное": "tiny", "Маленькое": "small",
            "Среднее": "medium", "Большое": "large", "Огромное": "huge", "Колоссальное": "colossal",
            
            # Покрытия
            "Шерсть": "fur", "Чешуя": "scales", "Кожа": "skin", "Перья": "feathers",
            "Экзоскелет": "exoskeleton", "Панцирь": "shell", "Гладкая кожа": "smooth skin",
            "Слизь": "slime", "Кристаллы": "crystals", "Биолюминесцентная кожа": "bioluminescent skin",
            "Крылья": "wings", "Легкий экзоскелет": "light exoskeleton", "Мембраны": "membranes",
            "Шипы": "spikes", "Твердая чешуя": "hard scales", "Слизь": "mucus",
            "Водонепроницаемая кожа": "waterproof skin", "Кристаллы": "crystal",
            "Металл": "metal", "Энергетическая оболочка": "energy shell", "Космическая материя": "cosmic matter",
            "Огнеупорная чешуя": "fireproof scales", "Лавовая кожа": "lava skin",
            "Теплоизоляционный панцирь": "heat-insulating shell", "Густой мех": "thick fur",
            "Теплые перья": "warm feathers", "Жировая прослойка": "fat layer", "Плотная кожа": "thick skin",
            "Сухая чешуя": "dry scales", "Песочная кожа": "sandy skin", "Водоудерживающая кожа": "water-retaining skin",
            "Влажная кожа": "wet skin", "Водонепроницаемая чешуя": "waterproof scales",
            
            # Глаза
            "Одна пара круглых глаз": "one pair of round eyes", "Три глаза треугольником": "three eyes in triangle",
            "Множество маленьких глаз": "multiple small eyes", "Большие светящиеся глаза": "large glowing eyes",
            "Глаза с вертикальными зрачками": "eyes with vertical pupils", "Сложные фасеточные глаза": "complex compound eyes",
            "Глаза с биолюминесценцией": "bioluminescent eyes", "Глаза с тепловым зрением": "thermal vision eyes",
            
            # Рты
            "Клыкастая пасть": "fanged mouth", "Клюв с острыми краями": "sharp-beaked mouth",
            "Мягкие губы": "soft lips", "Хоботок для сосания": "sucking proboscis",
            "Челюсти с множественными рядами зубов": "jaws with multiple rows of teeth",
            "Ротовой аппарат с хелицерами": "mouth with chelicerae", "Круглый рот с присосками": "round mouth with suckers",
            "Многочисленные щупальца вокруг рта": "numerous tentacles around mouth",
            "Грызущие резцы": "gnawing incisors",
            
            # Придатки
            "Длинные усы": "long whiskers", "Антенны с чувствительными рецепторами": "antennae with sensitive receptors",
            "Рога различной формы": "horns of various shapes", "Бивни": "tusks", "Грива": "mane", "Длинные уши": "long ears", "Гребень на голове": "crest on head",
            "Бородавки и наросты": "warts and growths", "Кристаллические выросты": "crystalline growths",
            "Энергетические коронки": "energy crowns", "Биолюминесцентные органы": "bioluminescent organs",
            
            # Конечности
            "Четыре конечности с когтями": "four limbs with claws", "Четыре конечности с копытами": "four limbs with hooves", "Четыре конечности с втяжными когтями": "four limbs with retractable claws", "Шесть конечностей как у насекомого": "six insect-like limbs",
            "Восемь щупалец": "eight tentacles", "Щупальца с присосками": "tentacles with suckers", "Крылья и две ноги": "wings and two legs",
            "Передние клешни": "front claws", "Длинные сильные ноги": "long powerful legs", "Плавники и хвост": "fins and tail", "Множественные придатки": "multiple appendages",
            "Энергетические конечности": "energy limbs", "Кристаллические выросты": "crystalline appendages",
            
            # Тело
            "Сегментированное тело": "segmented body", "Гибкий позвоночник": "flexible spine",
            "Бронированная грудь": "armored chest", "Прозрачные участки": "transparent areas",
            "Биолюминесцентные полосы": "bioluminescent stripes", "Кристаллические включения": "crystalline inclusions",
            "Энергетические узоры": "energy patterns", "Множественные сердца": "multiple hearts",
            
            # Хвосты
            "Длинный хвост с чешуей": "long scaly tail", "Хвост с ядовитым жалом": "tail with venomous stinger",
            "Пушистый хвост": "fluffy tail", "Хвост-плавник": "fin-like tail",
            "Хвост с биолюминесценцией": "bioluminescent tail", "Кристаллический хвост": "crystalline tail",
            "Энергетический хвост": "energy tail", "Хвост с множественными отростками": "tail with multiple appendages",
            
            # Способности
            "Ядовитые железы": "venom glands", "Электрические разряды": "electric discharges",
            "Кислотные выделения": "acid secretions", "Огненное дыхание": "fire breath",
            "Ледяные кристаллы": "ice crystals", "Психические атаки": "psychic attacks",
            "Клонирование": "cloning", "Телепортация": "teleportation", "Камуфляж": "camouflage",
            "Бронированная кожа": "armored skin", "Регенерация": "regeneration",
            "Невидимость": "invisibility", "Энергетический щит": "energy shield",
            "Кристаллическая броня": "crystalline armor", "Биолюминесцентное отвлечение": "bioluminescent distraction",
            "Множественные жизни": "multiple lives", "Полет": "flight", "Плавание": "swimming",
            "Копание": "digging", "Планирование": "gliding", "Быстрое бегание": "fast running",
            "Прыжки": "jumping", "Ползание по стенам": "wall crawling", "Выброс чернил": "ink jet",
            "Сильный прикус": "powerful bite", "Удар клешнями": "claw strike",
            "Сворачивание в клубок": "curling into a ball", "Флуоресценция в УФ": "UV fluorescence",
            
            # Цвета
            "Коричневый": "brown", "Зеленый": "green", "Серый": "gray", "Черный": "black",
            "Белый": "white", "Рыжий": "reddish", "Красный": "red", "Оранжевый": "orange",
            "Желтый": "yellow", "Розовый": "pink", "Фиолетовый": "purple", "Голубой": "blue",
            "Золотой": "golden", "Серебряный": "silver", "Бронзовый": "bronze", "Медный": "copper",
            "Платиновый": "platinum", "Прозрачный": "transparent", "Радужный": "rainbow",
            "Кристаллический": "crystalline", "Биолюминесцентный": "bioluminescent",
            "Темно-синий": "dark blue", "Темно-фиолетовый": "dark purple", "Темно-зеленый": "dark green",
            "Песочный": "sand", "Лесной": "forest", "Снежный": "snow", "Болотный": "swamp",
            "Скальный": "rock",
            
            # Поведение
            "Агрессивный охотник": "aggressive hunter", "Мирный травоядный": "peaceful herbivore",
            "Социальное существо": "social creature", "Одиночка": "solitary",
            "Ночной образ жизни": "nocturnal", "Дневной образ жизни": "diurnal",
            "Территориальный": "territorial", "Кочевой": "nomadic", "Интеллектуальный": "intelligent",
            "Инстинктивный": "instinctive", "Любопытный": "curious", "Осторожный": "cautious",
            "Игривый": "playful", "Серьезный": "serious", "Хитрый": "cunning", "Скрытный": "stealthy",
            "Засадный хищник": "ambush predator", "Пугливый": "skittish", "Стадное поведение": "herd behavior",

            # Доп. движения
            "Бесшумный полет": "silent flight", "Боковое передвижение": "sideways movement",
            
            # Адаптации
            "Эффективная терморегуляция": "efficient thermoregulation", "Развитые органы чувств": "developed sensory organs",
            "Адаптация к различным ландшафтам": "adaptation to various landscapes",
            "Эффективные конечности для передвижения": "efficient limbs for movement",
            "Жабры для дыхания": "gills for breathing", "Плавательный пузырь": "swim bladder",
            "Боковая линия для ориентации": "lateral line for orientation",
            "Гидродинамическая форма тела": "hydrodynamic body shape", "Полые кости для легкости": "hollow bones for lightness",
            "Развитые мышцы крыльев": "developed wing muscles", "Острое зрение": "sharp vision",
            "Аэродинамическая форма": "aerodynamic shape", "Копательные конечности": "digging limbs",
            "Развитое обоняние": "developed sense of smell", "Сниженное зрение": "reduced vision",
            "Адаптация к темноте": "adaptation to darkness", "Двойное дыхание": "dual breathing",
            "Влажная кожа": "wet skin", "Перепонки": "webbed feet", "Адаптация к двум средам": "adaptation to two environments",
            "Независимость от кислорода": "oxygen independence", "Радиационная устойчивость": "radiation resistance",
            "Энергетическая подпитка": "energy feeding", "Космическая навигация": "cosmic navigation",
            
            # Дополнительные переводы для непереведенных слов
            "ротовой аппарат с хелицерами": "mouth with chelicerae",
            "биолюминесцентные органы": "bioluminescent organs",
            "кристаллические выросты": "crystalline growths",
            "множественные сердца": "multiple hearts",
            "хвост с множественными отростками": "tail with multiple appendages",
            "телепортация": "teleportation",
            "ядовитые железы": "venom glands",
            "камуфляж": "camouflage",
            "лесной": "forest",
            "агрессивный охотник": "aggressive hunter",
            "одиночка": "solitary",
            "инстинктивный": "instinctive",
            "песчаная кожа": "sandy skin",
            "адаптация к засухе": "adaptation to drought",
            "бородавки и наросты": "warts and growths",
            "крылья и две ноги": "wings and two legs",
            "гибкий позвоночник": "flexible spine",
            "клонирование": "cloning",
            "кислотные выделения": "acid secretions",
            "планирование": "gliding",
            "дневной образ жизни": "diurnal",
            "любопытный": "curious",
            "социальное существо": "social creature",
            "кристаллы": "crystals",
            "без крыльев и перьев, с плавательными приспособлениями": "without wings and feathers, with swimming adaptations",
            "энергетические коронки": "energy crowns",
            "восемь щупалец": "eight tentacles",
            "биолюминесцентные полосы": "bioluminescent stripes",
            "хвост с ядовитым жалом": "tail with venomous stinger",
            "жабры для дыхания": "gills for breathing",
            "плавательный пузырь": "swim bladder",
            "энергетический щит": "energy shield",
            "ползание по стенам": "wall crawling",
            "кристаллический": "crystalline",
            "переливающиеся чешуйки": "iridescent scales",
            "клюв с острыми краями": "sharp beak",
            "хвост с биолюминесценцией": "bioluminescent tail",
            "огненное дыхание": "fire breath",
            "копание": "digging",
            "прыжки": "jumping",
            "песочный": "sand",
            "болотный": "swamp",
            "серьезный": "serious",
            "игривый": "playful",
            "копательные конечности": "digging limbs",
            "развитое обоняние": "developed sense of smell",
            "сниженное зрение": "reduced vision",
            "адаптация к темноте": "adaptation to darkness",
            "прозрачные участки": "transparent areas",
            "антенны с чувствительными рецепторами": "antennae with sensitive receptors",
            "множественные жизни": "multiple lives",
            "ледяные кристаллы": "ice crystals",
            "бронзовый": "bronze",
            "серебряный": "silver",
            "мирный травоядный": "peaceful herbivore",
            "ночной образ жизни": "nocturnal",
            "двойное дыхание": "dual breathing",
            "адаптация к двум средам": "adaptation to two environments",
            "четыре конечности с когтями": "four limbs with claws",
            "боковая линия для ориентации": "lateral line for orientation",
            "гидродинамическая форма тела": "hydrodynamic body shape",
            "быстрое бегание": "fast running",
            "металлический блеск": "metallic shine",
            "без крыльев, предпочтительно панцирь": "without wings, preferably with shell",
            "глаза с вертикальными зрачками": "eyes with vertical pupils",
            "круглый рот с присосками": "round mouth with suckers",
            "кристаллическая броня": "crystalline armor",
            "полет": "flight",
            "территориальный": "territorial",
            "осторожный": "cautious",
            "независимость от кислорода": "oxygen independence",
            "радиационная устойчивость": "radiation resistance",
            "энергетическая подпитка": "energy feeding",
            "космическая навигация": "cosmic navigation",
            "допустимы любые формы тела": "any body forms allowed",
            "энергетический хвост": "energy tail",
            "психические атаки": "psychic attacks",
            "зеленый": "green",
            "множество маленьких глаз": "multiple small eyes",
            "длинные усы": "long whiskers",
            "энергетические конечности": "energy limbs",
            "платиновый": "platinum",
            "золотой": "golden",
            "без крыльев, с плавательными конечностями": "without wings, with swimming limbs"
        }
    
    def _setup_constraints(self):
        """Настройка логических ограничений"""
        
        # Несовместимые комбинации (для HYBRID действуют минимальные ограничения: только физически невозможные)
        base_incompatible = {
            "Крылья": ["Плавники", "Жабры", "Водные мембраны"],
            "Плавники": ["Крылья", "Перья", "Сухопутные конечности"],
            "Жабры": ["Крылья", "Перья", "Сухопутные конечности"],
            "Перья": ["Плавники", "Жабры", "Водные мембраны"],
            "Огненное дыхание": ["Водные адаптации", "Ледяные способности"],
            "Ледяные кристаллы": ["Огненные способности", "Вулканические адаптации"],
            "Биолюминесценция": ["Темная окраска", "Камуфляж"],
            "Невидимость": ["Яркая окраска", "Биолюминесценция"]
        }
        # Для простоты: храним базовый набор, а при генерации проверяем тип существа
        self.incompatible_features = base_incompatible
        
        # Обязательные комбинации
        self.required_combinations = {
            Habitat.AERIAL: ["Крылья"],
            Habitat.AQUATIC: ["Плавники"],
            Habitat.UNDERGROUND: ["Копательные конечности"],
            Habitat.AMPHIBIOUS: ["Перепонки"],
            Size.COLOSSAL: ["Множественные сердца"],
            CreatureType.CRYSTAL: ["Кристаллические структуры"]
        }
    
    def _validate_combination(self, features: List[str], creature_type: Optional[CreatureType] = None) -> bool:
        """Проверка совместимости характеристик. Для HYBRID ограничения минимальны."""
        # Гибрид: пропускаем мягкие стилистические ограничения, оставляем только грубо-физические
        if creature_type == CreatureType.HYBRID:
            strict_conflicts = {
                "Крылья": ["Плавники"],
                "Плавники": ["Крылья"],
                "Жабры": ["Сухопутные конечности"],
            }
            for feature in features:
                if feature in strict_conflicts:
                    for incompatible in strict_conflicts[feature]:
                        if incompatible in features:
                            return False
            return True

        # Для остальных типов — полный набор несовместимостей
        for feature in features:
            if feature in self.incompatible_features:
                for incompatible in self.incompatible_features[feature]:
                    if incompatible in features:
                        return False
        return True
    
    def _get_required_features(self, habitat: Habitat, size: Size, creature_type: CreatureType) -> List[str]:
        """Получение обязательных характеристик"""
        required = []
        
        # Обязательные для среды обитания
        if habitat in self.required_combinations:
            required.extend(self.required_combinations[habitat])
        
        # Обязательные для размера
        if size in self.required_combinations:
            required.extend(self.required_combinations[size])
        
        # Обязательные для типа
        if creature_type in self.required_combinations:
            required.extend(self.required_combinations[creature_type])
        
        return required
    
    def _generate_head_description(self) -> str:
        """Генерация описания головы"""
        eyes = random.choice(self.head_variants["eyes"])
        mouth = random.choice(self.head_variants["mouths"])
        appendage = random.choice(self.head_variants["appendages"])
        
        return f"{eyes}, {mouth.lower()}, {appendage.lower()}"
    
    def _generate_body_features(self, habitat: Habitat) -> List[str]:
        """Генерация характеристик тела"""
        features = []
        
        # Основные части тела
        features.append(random.choice(self.body_features["limbs"]))
        features.append(random.choice(self.body_features["torso"]))
        
        # Хвост (не для всех существ)
        if random.random() < 0.7:
            features.append(random.choice(self.body_features["tail"]))
        
        # Адаптации к среде обитания
        if habitat in self.environmental_adaptations:
            features.extend(random.sample(
                self.environmental_adaptations[habitat], 
                min(2, len(self.environmental_adaptations[habitat]))
            ))
        
        return features
    
    def _generate_special_abilities(self, habitat: Habitat, size: Size) -> List[str]:
        """Генерация специальных способностей"""
        abilities = []
        
        # Количество способностей зависит от размера
        ability_count = {
            Size.MICROSCOPIC: 1,
            Size.TINY: 1,
            Size.SMALL: 2,
            Size.MEDIUM: 2,
            Size.LARGE: 3,
            Size.HUGE: 3,
            Size.COLOSSAL: 4
        }
        
        count = ability_count.get(size, 2)
        
        # Выбираем способности из разных категорий
        categories = list(self.special_abilities.keys())
        for _ in range(count):
            category = random.choice(categories)
            ability = random.choice(self.special_abilities[category])
            if ability not in abilities:
                abilities.append(ability)
        
        return abilities
    
    def _generate_coloration(self, habitat: Habitat) -> List[str]:
        """Генерация окраски"""
        colors = []
        
        # Основная окраска зависит от среды обитания
        if habitat in [Habitat.UNDERGROUND, Habitat.DESERT]:
            scheme = "camouflage"
        elif habitat == Habitat.COSMIC:
            scheme = "crystal"
        elif habitat == Habitat.VOLCANIC:
            scheme = "bright"
        else:
            scheme = random.choice(list(self.coloration_schemes.keys()))
        
        base_colors = self.coloration_schemes[scheme]
        colors.append(random.choice(base_colors))
        
        # Дополнительные цвета
        if random.random() < 0.5:
            colors.append(random.choice(base_colors))
        
        # Особые эффекты
        effects = ["Биолюминесцентные пятна", "Металлический блеск", "Переливающиеся чешуйки", "Энергетическое свечение"]
        if random.random() < 0.3:
            colors.append(random.choice(effects))
        
        return colors
    
    def _generate_behavior_traits(self, size: Size) -> List[str]:
        """Генерация поведенческих черт"""
        traits = []
        
        # Количество черт зависит от размера
        trait_count = {
            Size.MICROSCOPIC: 1,
            Size.TINY: 2,
            Size.SMALL: 2,
            Size.MEDIUM: 3,
            Size.LARGE: 3,
            Size.HUGE: 4,
            Size.COLOSSAL: 4
        }
        
        count = trait_count.get(size, 2)
        traits = random.sample(self.behavior_traits, count)
        
        return traits
    
    def _translate_to_english(self, russian_text: str) -> str:
        """Перевод русского текста на английский"""
        if not russian_text:
            return ""
        # Разбиваем текст на части и переводим каждую
        parts = russian_text.split(', ')
        translated_parts = []
        
        for part in parts:
            part = part.strip()
            # Ищем точное совпадение в словаре переводов
            if part in self.english_translations:
                translated_parts.append(self.english_translations[part])
            elif hasattr(self, 'english_translations_ci') and part.lower() in self.english_translations_ci:
                translated_parts.append(self.english_translations_ci[part.lower()])
            else:
                # Если нет точного совпадения, пытаемся перевести по частям
                words = part.split()
                translated_words = []
                for word in words:
                    # Сначала пытаемся по исходному регистру, затем по нижнему
                    if word in self.english_translations:
                        translated_words.append(self.english_translations[word])
                    elif hasattr(self, 'english_translations_ci') and word.lower() in self.english_translations_ci:
                        translated_words.append(self.english_translations_ci[word.lower()])
                    else:
                        # Если слово не найдено, оставляем как есть
                        translated_words.append(word)
                translated_parts.append(' '.join(translated_words))
        
        return ', '.join(translated_parts)

    def _build_ci_translations(self) -> None:
        """Создает нижнерегистровый индекс переводов для устойчивости к регистру"""
        self.english_translations_ci = {k.lower(): v for k, v in getattr(self, 'english_translations', {}).items()}

    def generate_creature(self) -> CreatureCharacteristics:
        """Генерация полного описания существа"""
        
        # Выбор среды: наземная теперь разделена на отдельные подтипы (FOREST_TROPICAL, GRASSLAND, MOUNTAIN)
        # Поэтому просто выбираем из Enum равновероятно
        habitat = random.choice(list(Habitat))
        habitat_info = self.habitat_data[habitat]
        
        creature_type = random.choice(habitat_info["types"])
        surface = random.choice(habitat_info["surfaces"])
        size = random.choice(list(Size))
        
        # Генерация детальных характеристик
        head_description = self._generate_head_description()
        body_features = self._generate_body_features(habitat)
        special_abilities = self._generate_special_abilities(habitat, size)
        coloration = self._generate_coloration(habitat)
        behavior_traits = self._generate_behavior_traits(size)
        environmental_adaptations = self.environmental_adaptations.get(habitat, [])
        
        # Создание объекта характеристик
        creature = CreatureCharacteristics(
            habitat=habitat,
            creature_type=creature_type,
            size=size,
            surface=surface,
            form_rules=habitat_info["form_rules"],
            head_description=head_description,
            body_features=body_features,
            special_abilities=special_abilities,
            coloration=coloration,
            behavior_traits=behavior_traits,
            environmental_adaptations=environmental_adaptations
        )
        
        return creature
    
    def generate_detailed_prompt(self, creature: CreatureCharacteristics) -> str:
        """Генерация детального промпта для изображения"""
        
        size_info = self.size_characteristics[creature.size]
        
        prompt = f"Детальное изображение {creature.creature_type.value.lower()} из среды '{creature.habitat.value}'. "
        prompt += f"Размер: {creature.size.value.lower()} ({size_info['speed']}, {size_info['strength']}). "
        prompt += f"Покрытие: {creature.surface.lower()}. "
        prompt += f"Форма тела: {creature.form_rules.lower()}. "
        prompt += f"Голова: {creature.head_description.lower()}. "
        
        if creature.body_features:
            prompt += f"Тело: {', '.join(creature.body_features).lower()}. "
        
        if creature.special_abilities:
            prompt += f"Способности: {', '.join(creature.special_abilities).lower()}. "
        
        if creature.coloration:
            prompt += f"Окраска: {', '.join(creature.coloration).lower()}. "
        
        if creature.behavior_traits:
            prompt += f"Поведение: {', '.join(creature.behavior_traits).lower()}. "
        
        if creature.environmental_adaptations:
            prompt += f"Адаптации: {', '.join(creature.environmental_adaptations).lower()}. "
        
        return prompt

    def generate_english_prompt(self, creature: CreatureCharacteristics) -> str:
        """Генерация английского промпта для нейросети с прозрачным/нейтральным фоном"""
        # Определяем тип фона в зависимости от среды обитания (RU/EN)
        _, background_type_en = self._determine_background_type(creature.habitat)
        
        # Формируем финальный промпт
        creature_type_eng = self.english_translations.get(creature.creature_type.value, creature.creature_type.value.lower())
        habitat_eng = self.english_translations.get(creature.habitat.value, creature.habitat.value.lower())
        size_eng = self.english_translations.get(creature.size.value, creature.size.value.lower())
        surface_eng = self.english_translations.get(creature.surface, creature.surface.lower())
        
        prompt = f"A detailed {creature_type_eng} from {habitat_eng} environment. "
        prompt += f"Size: {size_eng}. Surface: {surface_eng}. "
        prompt += f"Head: {self._translate_to_english(creature.head_description)}. "
        
        if creature.body_features:
            body_features_eng = [self._translate_to_english(feature) for feature in creature.body_features]
            prompt += f"Body: {', '.join(body_features_eng)}. "
        
        if creature.special_abilities:
            abilities_eng = [self._translate_to_english(ability) for ability in creature.special_abilities]
            prompt += f"Abilities: {', '.join(abilities_eng)}. "
        
        if creature.coloration:
            colors_eng = [self._translate_to_english(color) for color in creature.coloration]
            prompt += f"Coloration: {', '.join(colors_eng)}. "
        
        if creature.behavior_traits:
            traits_eng = [self._translate_to_english(trait) for trait in creature.behavior_traits]
            prompt += f"Behavior: {', '.join(traits_eng)}. "
        
        if creature.environmental_adaptations:
            adaptations_eng = [self._translate_to_english(adaptation) for adaptation in creature.environmental_adaptations]
            prompt += f"Adaptations: {', '.join(adaptations_eng)}. "
        
        # Добавляем требования к фону и качеству
        prompt += f"{background_type_en}, high quality, detailed"
        
        return prompt

    # =============================
    # Стадийные промпты (4 стадии)
    # =============================
    def _extract_head_traits(self, head_description: str) -> Tuple[str, str, str]:
        parts = [p.strip() for p in head_description.split(',')]
        while len(parts) < 3:
            parts.append("")
        return parts[0], parts[1], parts[2]

    def _build_species_motif(self, creature: CreatureCharacteristics) -> Tuple[str, str]:
        # Базовый мотив: покрытие + ключевой цвет + головной придаток
        eyes, mouth, appendage = self._extract_head_traits(creature.head_description)
        key_color_ru = creature.coloration[0] if creature.coloration else ""
        motif_ru_parts = []
        if creature.surface:
            motif_ru_parts.append(f"покровы: {creature.surface.lower()}")
        if key_color_ru:
            motif_ru_parts.append(f"окраска: {key_color_ru.lower()}")
        if appendage:
            motif_ru_parts.append(f"характерный признак головы: {appendage.lower()}")
        motif_ru = ", ".join(motif_ru_parts)

        surface_en = self.english_translations.get(creature.surface, creature.surface.lower())
        key_color_en = self._translate_to_english(key_color_ru) if key_color_ru else ""
        appendage_en = self._translate_to_english(appendage) if appendage else ""
        motif_en_parts = []
        if surface_en:
            motif_en_parts.append(f"surface: {surface_en}")
        if key_color_en:
            motif_en_parts.append(f"coloration: {key_color_en}")
        if appendage_en:
            motif_en_parts.append(f"signature head trait: {appendage_en}")
        motif_en = ", ".join(motif_en_parts)

        return motif_ru, motif_en

    def _stage_ru_prompt(self, creature: CreatureCharacteristics, stage_key: str) -> str:
        stage_name = self.life_stages[stage_key]["ru"]
        modifier = self.stage_modifiers[stage_key]["ru"]
        motif_ru, _ = self._build_species_motif(creature)
        base = f"{stage_name} вида '{creature.creature_type.value.lower()}' из среды '{creature.habitat.value}'. "
        continuity = f"Сквозные признаки вида: {motif_ru}. " if motif_ru else ""
        bg_ru, _ = self._determine_background_type(creature.habitat)
        # Для стадии яйца в воздушной среде используем контекст "гнезда",
        # чтобы яйцо не "висело в небе" без опоры
        if stage_key == "egg" and creature.habitat == Habitat.AERIAL:
            egg_bg_ru, _ = self._egg_background_for_stage(creature)
            if egg_bg_ru:
                bg_ru = egg_bg_ru
        if stage_key == "egg":
            # Упрощённый RU-промпт для яйца
            return base + f"Описание: {modifier}. Фон: {bg_ru}."
        elif stage_key == "baby":
            return base + f"Описание: {modifier}. Голова: {creature.head_description.lower()}. Тело: мягкие, укороченные конечности. {continuity}Фон: {bg_ru}."
        else:  # adult
            base_prompt = self.generate_detailed_prompt(creature)
            return base_prompt + f" {continuity}"

    def _stage_en_prompt(self, creature: CreatureCharacteristics, stage_key: str) -> str:
        stage_name = self.life_stages[stage_key]["en"]
        modifier = self.stage_modifiers[stage_key]["en"]
        _, motif_en = self._build_species_motif(creature)
        creature_type_eng = self.english_translations.get(creature.creature_type.value, creature.creature_type.value.lower())
        habitat_eng = self.english_translations.get(creature.habitat.value, creature.habitat.value.lower())
        _, bg_en = self._determine_background_type(creature.habitat)
        # Egg override for aerial habitat: use nest/roost context
        if stage_key == "egg" and creature.habitat == Habitat.AERIAL:
            _, egg_bg_en = self._egg_background_for_stage(creature)
            if egg_bg_en:
                bg_en = egg_bg_en

        if stage_key == "egg":
            # Упрощённый промпт для яйца: только тип, среда, краткий модификатор и фон
            prompt = f"A {stage_name} of a {creature_type_eng} from {habitat_eng} environment. {modifier}. {bg_en}, high quality, detailed"
            return prompt
        elif stage_key == "baby":
            head_en = self._translate_to_english(creature.head_description)
            prompt = f"A {stage_name} {creature_type_eng} from {habitat_eng}. {modifier}. Head: {head_en}. Body: soft, stubby limbs. {('Continuity: ' + motif_en + '. ') if motif_en else ''}{bg_en}, high quality, detailed"
            return prompt
        else:  # adult
            return self.generate_english_prompt(creature)

    def generate_stage_prompts(self, creature: CreatureCharacteristics) -> Dict[str, Dict[str, str]]:
        """Генерация набора промптов для 4 стадий развития (RU/EN)"""
        stages = ["egg", "baby", "adult"]
        result: Dict[str, Dict[str, str]] = {}
        # Получаем специализированные негативные промпты
        try:
            from config.settings import get_stage_negative_prompt
        except Exception:
            get_stage_negative_prompt = lambda s, include_global=True: ""  # noqa: E731

        for s in stages:
            ru = self._stage_ru_prompt(creature, s)
            en = self._stage_en_prompt(creature, s)
            neg = get_stage_negative_prompt(s, include_global=True)
            result[s] = {
                "ru": ru,
                "en": en,
                "negative": neg
            }
        return result
    
    def _egg_background_for_stage(self, creature: CreatureCharacteristics) -> Tuple[Optional[str], Optional[str]]:
        """Возвращает (RU, EN) описание фона для стадии яйца в зависимости от среды.
        Сейчас детально обрабатываем воздушную среду: вместо неба используем контекст гнезда.
        """
        if creature.habitat == Habitat.AERIAL:
            nest_variants_ru_en: List[Tuple[str, str]] = [
                ("гнездо из прутьев на верхушке высокого дерева", "a twig nest on top of a tall tree"),
                ("гнездо на скальном уступе в горах", "a nest on a cliff ledge in the mountains"),
                ("гнездо в кронах густого леса", "a nest within the dense forest canopy"),
                ("гнездо на балке заброшенной башни", "a nest on a beam of an abandoned tower"),
                ("гнездо на парящей скале среди облаков", "a nest on a floating rock among clouds"),
            ]
            chosen_ru, chosen_en = random.choice(nest_variants_ru_en)
            return chosen_ru, chosen_en
        # Для прочих сред пока используем базовый фон
        return None, None
    def _determine_background_type(self, habitat: Habitat) -> Tuple[str, str]:
        """Определение описания фона по среде обитания (RU, EN)"""
        ru = {
            Habitat.FOREST_TROPICAL: "тропический лес",
            Habitat.GRASSLAND: "луговая равнина",
            Habitat.MOUNTAIN: "горная местность",
            Habitat.AQUATIC: "подводная среда с водой",
            Habitat.AERIAL: "небесная среда с облаками",
            Habitat.UNDERGROUND: "подземная среда в мягком свете",
            Habitat.AMPHIBIOUS: "береговая/болотная прибрежная среда",
            Habitat.COSMIC: "космическая среда с частицами и звёздами",
            Habitat.VOLCANIC: "вулканическая среда с раскалёнными породами",
            Habitat.ARCTIC: "арктическая ледяная среда",
            Habitat.DESERT: "песчаная пустынная среда",
            Habitat.SWAMP: "болотная среда с туманом"
        }
        en = {
            Habitat.FOREST_TROPICAL: "tropical forest environment",
            Habitat.GRASSLAND: "grassland plains environment",
            Habitat.MOUNTAIN: "mountain environment",
            Habitat.AQUATIC: "underwater aquatic environment",
            Habitat.AERIAL: "sky environment with clouds",
            Habitat.UNDERGROUND: "underground environment with soft light",
            Habitat.AMPHIBIOUS: "coastal/marsh shoreline environment",
            Habitat.COSMIC: "cosmic environment with particles and stars",
            Habitat.VOLCANIC: "volcanic environment with glowing rocks",
            Habitat.ARCTIC: "arctic icy environment",
            Habitat.DESERT: "sandy desert environment",
            Habitat.SWAMP: "swampy environment with mist"
        }

        return ru.get(habitat, "нейтральная среда"), en.get(habitat, "neutral environment")

    def _create_english_description(self, creature: CreatureCharacteristics) -> str:
        """Создание базового английского описания существа"""
        description = f"{self.english_translations.get(creature.creature_type.value, creature.creature_type.value.lower())} "
        description += f"with {self.english_translations.get(creature.surface, creature.surface.lower())} "
        description += f"and {self._translate_to_english(creature.head_description)}"
        return description

    def generate_json_description(self, creature: CreatureCharacteristics) -> str:
        """Генерация JSON описания существа"""
        return json.dumps({
            "habitat": creature.habitat.value,
            "type": creature.creature_type.value,
            "size": creature.size.value,
            "surface": creature.surface,
            "form_rules": creature.form_rules,
            "head_description": creature.head_description,
            "body_features": creature.body_features,
            "special_abilities": creature.special_abilities,
            "coloration": creature.coloration,
            "behavior_traits": creature.behavior_traits,
            "environmental_adaptations": creature.environmental_adaptations
        }, ensure_ascii=False, indent=2)


def main():
    """Основная функция для демонстрации генератора"""
    generator = CreatureGenerator()
    
    print("🎲 Генератор существ с детальными характеристиками")
    print("=" * 60)
    
    for i in range(3):
        print(f"\n📋 Существо #{i+1}")
        print("-" * 40)
        
        # Генерация существа
        creature = generator.generate_creature()
        
        # Вывод стадийных промптов
        stage_prompts = generator.generate_stage_prompts(creature)
        print("🎯 Стадии развития (RU/EN), с негативными промптами:")
        for stage_key in ["egg", "baby", "adult"]:
            print(f"\n - {stage_key.upper()} [RU]:")
            print(stage_prompts[stage_key]["ru"])
            print(f"\n - {stage_key.upper()} [EN]:")
            print(stage_prompts[stage_key]["en"])
            print(f"\n   Negative:")
            print(stage_prompts[stage_key]["negative"])
        
        # Вывод JSON описания
        print(f"\n📊 JSON описание:")
        json_desc = generator.generate_json_description(creature)
        print(json_desc)
        
        print("\n" + "=" * 60)


if __name__ == "__main__":
    main()


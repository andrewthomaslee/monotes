# Standard Imports
import logging
from logging import Logger
from datetime import datetime, timedelta
import random

# Third Party Imports
from pymongo import AsyncMongoClient
from beanie import init_beanie

# My Imports
from .models import User, Machine, Log, ActiveUsers, MachineMissingLog
from .config import CONFIG_SETTINGS


logging.basicConfig(level=logging.INFO)
logger: Logger = logging.getLogger(__name__)


# ------------Init-Beanie-------------#
async def init_db() -> None:
    logger.info("Initializing database...")
    client: AsyncMongoClient = AsyncMongoClient(CONFIG_SETTINGS.DB_URI)
    await init_beanie(
        database=client["admin"],
        document_models=[User, Machine, Log, ActiveUsers, MachineMissingLog],
    )
    logger.info("Database initialized")


# ------------Fake Data-------------#
async def create_sudo_user() -> None:
    sudo_user: User | None = await User.find_one(
        User.name == "sudo", User.admin == True, User.password == "sudo"
    )
    if sudo_user is None:
        await User(name="sudo", password="sudo", admin=True).save()
        logger.info("Created sudo user")


async def create_plain_user() -> None:
    plain_user: User | None = await User.find_one(
        User.name == "user", User.admin == False, User.password == "user"
    )
    if plain_user is None:
        await User(name="user", password="user", admin=False).save()
        logger.info("Created plain user")


adjectives: list[str] = [
    "adaptable",
    "adventurous",
    "affectionate",
    "ambitious",
    "amiable",
    "compassionate",
    "considerate",
    "courageous",
    "courteous",
    "diligent",
    "empathetic",
    "exuberant",
    "frank",
    "generous",
    "gregarious",
    "impartial",
    "intuitive",
    "inventive",
    "passionate",
    "persistent",
    "philosophical",
    "practical",
    "rational",
    "reliable",
    "resourceful",
    "sensible",
    "sincere",
    "sympathetic",
    "unassuming",
    "witty",
    "able",
    "amazing",
    "atomic",
    "automatic",
    "beautiful",
    "brave",
    "breezy",
    "bright",
    "bubbly",
    "calm",
    "careful",
    "charming",
    "cheerful",
    "clean",
    "clever",
    "cool",
    "creative",
    "cute",
    "dazzling",
    "determined",
    "electric",
    "elegant",
    "enchanting",
    "energetic",
    "excellent",
    "expert",
    "fabulous",
    "fantastic",
    "fearless",
    "fine",
    "fluffy",
    "friendly",
    "funny",
    "gentle",
    "giant",
    "gleaming",
    "glorious",
    "good",
    "gorgeous",
    "graceful",
    "grand",
    "great",
    "happy",
    "harmonious",
    "helpful",
    "hilarious",
    "honest",
    "honorable",
    "huge",
    "humble",
    "humorous",
    "imaginary",
    "impressive",
    "incredible",
    "innocent",
    "intelligent",
    "jolly",
    "joyful",
    "jubilant",
    "keen",
    "kind",
    "knowing",
    "knowledgeable",
    "laughing",
    "legendary",
    "light",
    "likely",
    "lively",
    "lovely",
    "loving",
    "loyal",
    "lucky",
    "luminous",
    "magical",
    "magnificent",
    "marvelous",
    "master",
    "mellow",
    "memorable",
    "merry",
    "mighty",
    "miraculous",
    "modern",
    "modest",
    "mysterious",
    "natural",
    "neat",
    "nice",
    "noble",
    "optimistic",
    "organized",
    "outstanding",
    "patient",
    "perfect",
    "playful",
    "pleasant",
    "polite",
    "powerful",
    "precious",
    "premium",
    "pretty",
    "proud",
    "peaceful",
    "quaint",
    "quick",
    "quiet",
    "radiant",
    "rapid",
    "rare",
    "ready",
    "real",
    "reassuring",
    "refined",
    "regular",
    "remarkable",
    "resilient",
    "resolute",
    "responsible",
    "rich",
    "righteous",
    "robust",
    "romantic",
    "royal",
    "safe",
    "savvy",
    "sensational",
    "serene",
    "sharp",
    "shimmering",
    "shiny",
    "silent",
    "silly",
    "simple",
    "skillful",
    "sleek",
    "smart",
    "smiling",
    "smooth",
    "solid",
    "sophisticated",
    "sparkling",
    "special",
    "spectacular",
    "speedy",
    "spirited",
    "splendid",
    "spotless",
    "stable",
    "stainless",
    "steady",
    "stellar",
    "still",
    "striking",
    "strong",
    "stunning",
    "stylish",
    "successful",
    "sunny",
    "super",
    "superb",
    "superior",
    "supportive",
    "surprising",
    "sweet",
    "swift",
    "talented",
    "terrific",
    "thankful",
    "thoughtful",
    "thriving",
    "tidy",
    "timely",
    "top",
    "tough",
    "tranquil",
    "tremendous",
    "true",
    "trustworthy",
    "truthful",
    "ultimate",
    "unbiased",
    "uncommon",
    "unique",
    "united",
    "unreal",
    "upbeat",
    "useful",
    "valiant",
    "valuable",
    "vast",
    "versatile",
    "vibrant",
    "victorious",
    "virtuous",
    "vivacious",
    "vivid",
    "warm",
    "wealthy",
    "welcoming",
    "whole",
    "wise",
    "wonderful",
    "wondrous",
    "young",
    "zany",
    "zealous",
]

nouns: list[str] = [
    "area",
    "book",
    "business",
    "case",
    "child",
    "company",
    "country",
    "day",
    "eye",
    "fact",
    "family",
    "government",
    "group",
    "hand",
    "home",
    "job",
    "life",
    "lot",
    "man",
    "money",
    "month",
    "mother",
    "mr",
    "night",
    "number",
    "part",
    "people",
    "place",
    "point",
    "problem",
    "apple",
    "art",
    "ball",
    "banana",
    "bed",
    "bell",
    "bird",
    "boat",
    "box",
    "boy",
    "bread",
    "brother",
    "car",
    "cat",
    "chair",
    "city",
    "class",
    "cloud",
    "computer",
    "cow",
    "cup",
    "dad",
    "desk",
    "dog",
    "door",
    "duck",
    "egg",
    "engine",
    "father",
    "fish",
    "flower",
    "food",
    "forest",
    "friend",
    "game",
    "garden",
    "girl",
    "glass",
    "gold",
    "grass",
    "hat",
    "heart",
    "horse",
    "house",
    "ice",
    "island",
    "jacket",
    "jelly",
    "jewel",
    "jungle",
    "key",
    "king",
    "kitchen",
    "kite",
    "lake",
    "lamp",
    "leaf",
    "leg",
    "letter",
    "lion",
    "love",
    "map",
    "milk",
    "mirror",
    "monkey",
    "moon",
    "morning",
    "mountain",
    "mouse",
    "music",
    "nest",
    "ocean",
    "orange",
    "oven",
    "paper",
    "park",
    "party",
    "pen",
    "pencil",
    "person",
    "picture",
    "pig",
    "plane",
    "plant",
    "plate",
    "pool",
    "potato",
    "queen",
    "quilt",
    "rabbit",
    "rain",
    "rainbow",
    "ring",
    "river",
    "road",
    "robot",
    "rock",
    "room",
    "rose",
    "sadness",
    "sand",
    "school",
    "sea",
    "ship",
    "shoe",
    "sister",
    "sky",
    "snow",
    "song",
    "sound",
    "soup",
    "star",
    "stone",
    "storm",
    "story",
    "street",
    "sun",
    "table",
    "teacher",
    "team",
    "television",
    "tent",
    "thing",
    "time",
    "tiger",
    "tomato",
    "tool",
    "town",
    "toy",
    "train",
    "tree",
    "truck",
    "umbrella",
    "university",
    "valley",
    "van",
    "vegetable",
    "village",
    "violin",
    "voice",
    "volcano",
    "wagon",
    "wall",
    "water",
    "wave",
    "way",
    "weather",
    "wind",
    "window",
    "winter",
    "woman",
    "wood",
    "word",
    "world",
    "xylophone",
    "yacht",
    "yak",
    "yard",
    "year",
    "yogurt",
    "zebra",
    "zoo",
]


async def generate_machine_name() -> str:
    adjective: str = random.choice(adjectives)
    noun: str = random.choice(nouns)
    return f"{adjective}-{noun}"


async def create_fake_machines() -> None:
    """Creates up to 50 fake machines with unique names."""
    existing_machines: list[Machine] = await Machine.find_all().to_list()
    num_existing: int = len(existing_machines)

    if num_existing >= 50:
        return None

    existing_names: set[str] = {m.name for m in existing_machines}
    names_to_create: int = 50 - num_existing
    new_names: set[str] = set()

    while len(new_names) < names_to_create:
        name: str = await generate_machine_name()
        if name not in existing_names and name not in new_names:
            new_names.add(name)

    fake_machines: list[Machine] = [
        Machine(
            name=name,
            joined_condition=random.randint(0, 5),
            special_note=random.choice(
                [
                    "What a great machine!",
                    "With the Frizz? No way!",
                    "I'm a machine?",
                    "Turtles all the way down.",
                    None,
                    None,
                    None,
                    None,
                    None,
                ]
            ),
            joined_time=datetime.now() - timedelta(days=random.randint(0, 365)),
        )
        for name in new_names
    ]

    if fake_machines:
        await Machine.insert_many(fake_machines)
        logger.info(f"Created {len(fake_machines)} fake machines")


async def generate_user_name() -> str:
    adjective: str = random.choice(adjectives)
    noun: str = random.choice(nouns)
    return f"{adjective.title()} {noun.title()}"


async def create_fake_users() -> None:
    check_db: list[User] = await User.find_all().to_list()
    if len(check_db) >= 20:
        return None

    fake_users: list[User] = [
        User(
            name=await generate_user_name(),
            password="password",
            admin=random.random() < 0.25,
            joined_time=datetime.now() - timedelta(days=random.randint(0, 365)),
        )
        for _ in range(18)
    ]
    await User.insert_many(fake_users)
    logger.info(f"Created {len(fake_users)} fake users")


async def load_fake_data() -> None:
    if CONFIG_SETTINGS.FAKE_DATA:
        await create_sudo_user()
        await create_plain_user()
        await create_fake_machines()
        await create_fake_users()

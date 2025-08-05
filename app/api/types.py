# app/api/types.py
from __future__ import annotations
import enum
from datetime import date, time
from typing import List, Optional
import strawberry
from pydantic import BaseModel

# --- Enums ---
@strawberry.enum
class ZodiacSign(enum.Enum):
    Aries = "Aries"
    Taurus = "Taurus"
    Gemini = "Gemini"
    Cancer = "Cancer"
    Leo = "Leo"
    Virgo = "Virgo"
    Libra = "Libra"
    Scorpio = "Scorpio"
    Sagittarius = "Sagittarius"
    Capricorn = "Capricorn"
    Pisces = "Pisces"

@strawberry.enum
class Children(enum.Enum):
    Wanted = "I want children"
    NotWanted = "I don't want children"
    NotSure = "Not sure"
    ChildrenAndMore = "I have children and want more"
    ChildrenAndNoMore = "I have children and don't want more"

@strawberry.enum
class CommunicationStyle(enum.Enum):
    Text = "I love texts"
    Phone = "Phone call"
    Video = "Video call"
    InPerson = "In person"

@strawberry.enum
class Pets(enum.Enum):
    Dog = "Dog"
    Cat = "Cat"
    Bird = "Bird"
    Fish = "Fish"
    Reptile = "Reptile"
    Other = "Other"
    NoPets = "No pets"
    NoPetsButWant = "No pets but want"
    AllergicToPets = "Allergic to pets"

@strawberry.enum
class Drinking(enum.Enum):
    NotMyThing = "Not my thing"
    No = "Don't drink alcohol"
    ExploringSobriety = "Exploring sobriety"
    Socially = "Socially"
    SpecialOccasions = "Special occasions"
    Everyday = "Everyday"
    WeekendsOnly = "Weekends only"

@strawberry.enum
class Smoking(enum.Enum):
    No = "No, I don't smoke"
    WithFriends = "Smoke with friends"
    Everyday = "Smoke everyday"
    Yes = "Yes, I smoke"
    Leaving = "Leaving smoking"
    WhenDrinking = "I smoke when drinking"

@strawberry.enum
class Fitness(enum.Enum):
    Never = "Never"
    Everyday = "Everyday"
    Sometimes = "Sometimes"
    Frequently = "Frequently"
    Rarely = "Rarely"

@strawberry.enum
class Dietary(enum.Enum):
    Vegan = "Vegan"
    Vegetarian = "Vegetarian"
    Paleo = "Paleo"
    Keto = "Keto"
    GlutenFree = "Gluten Free"
    Other = "Other"
    Kosher = "Kosher"
    Halal = "Halal"
    Meat = "Meat"
    Seafood = "Seafood"
    Pescatarian = "Pescatarian"

@strawberry.enum
class Sleeping(enum.Enum):
    Early = "Early bird"
    Late = "Night owl"
    NoPreference = "No preference"

@strawberry.enum
class Politics(enum.Enum):
    Liberal = "Liberal"
    Moderate = "Moderate"
    Conservative = "Conservative"
    NoInterest = "No interested in politics"
    Center = "Center"
    Left = "Left"
    Right = "Right"
    Socialist = "Socialist"
    Anarchist = "Anarchist"

@strawberry.enum
class Spirituality(enum.Enum):
    Atheist = "Atheist"
    Agnostic = "Agnostic"
    Buddhist = "Buddhist"
    Christian = "Christian"
    Hindu = "Hindu"
    Islam = "Islam"
    Jewish = "Jewish"
    Mormon = "Mormon"
    Sikh = "Sikh"
    Spiritual = "Spiritual"
    Other = "Other"
    Catholic = "Catholic"
    Evangelical = "Evangelical"
    Protestant = "Protestant"
    Orthodox = "Orthodox"

@strawberry.enum
class Gender(enum.Enum):
    Male = "Male"
    Female = "Female"
    NonBinary = "Non-binary"
    Other = "Other"

@strawberry.enum
class SexualOrientation(enum.Enum):
    Straight = "Straight"
    Gay = "Gay"
    Lesbian = "Lesbian"
    Bisexual = "Bisexual"
    Pansexual = "Pansexual"
    Asexual = "Asexual"
    Queer = "Queer"
    Arromantic = "Arromantic"
    Demisexual = "Demisexual"
    Other = "Other"

@strawberry.enum
class LookingFor(enum.Enum):
    Serious = "Serious relationship"
    Casual = "Casual relationship"
    Friendship = "Friendship"

# --- Data Types (Output) ---
@strawberry.type
class Photo:
    url: str
    sign: Optional[ZodiacSign]

@strawberry.type
class AstrologicalPositionType:
    name: str
    sign: str
    sign_icon: str
    degrees: float
    house: int

@strawberry.type
class NatalChartType:
    positions: List[AstrologicalPositionType]
    houses: List[AstrologicalPositionType]

    @classmethod
    def from_pydantic(cls, pydantic_obj: BaseModel) -> "NatalChartType":
        data = pydantic_obj.dict()
        return cls(**data)

@strawberry.type
class UserInfo:
    height: Optional[int]
    weight: Optional[int]
    school: Optional[str]
    languages: Optional[List[str]]
    interests: Optional[List[str]]
    education: Optional[str]
    children: Optional[Children]
    communication_style: Optional[CommunicationStyle]
    pets: Optional[Pets]
    drinking: Optional[Drinking]
    smoking: Optional[Smoking]
    fitness: Optional[Fitness]
    dietary: Optional[Dietary]
    sleeping: Optional[Sleeping]
    politics: Optional[Politics]
    spirituality: Optional[Spirituality]

@strawberry.type
class User:
    id: strawberry.ID
    email: str
    birth_date: date
    birth_time: time
    birth_place: str
    photos: List[Photo]
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    timezone: Optional[str] = None
    natal_chart: Optional[NatalChartType] = None
    user_info: Optional[UserInfo]
    gender: Gender
    looking_for: LookingFor
    sexual_orientation: Optional[List[SexualOrientation]]

@strawberry.type
class AuthPayload:
    token: str
    user: User

@strawberry.type
class LikeResponse:
    matched: bool

@strawberry.type
class CompatibilityBreakdown:
    category: str
    score: float
    description: str

# --- Input Types ---
@strawberry.input
class SignUpInput:
    email: str
    password: str
    birth_date: date
    birth_time: time
    birth_place: str
    gender: Gender
    looking_for: LookingFor

@strawberry.input
class LoginInput:
    email: str
    password: str

@strawberry.input
class LikeInput:
    user_id: strawberry.ID
    target_user_id: strawberry.ID

@strawberry.input
class PhotoInput:
    url: str
    sign: Optional[ZodiacSign] = None
    def to_dict(self) -> dict:
        return {"url": self.url, "sign": self.sign.value if self.sign else None}

@strawberry.input
class AddPhotosInput:
    user_id: strawberry.ID
    photos: List[PhotoInput]

from abc import ABC, abstractmethod


# --- INHERITANCE: Animal is the base class ---
# All animals share common attributes (name, weight, age) and a make_sound interface.
class Animal(ABC):
    # Each subclass must declare which enclosure type it needs (e.g. "Savannah", "Aquatic")
    required_enclosure: str = NotImplemented

    def __init__(self, name: str, weight: float, age: int):
        self.name = name
        self.weight = weight
        self.age = age

    @abstractmethod
    def make_sound(self) -> str:
        """Each animal subclass defines its own sound (or silence)."""
        pass

    @abstractmethod
    def diet(self) -> str:
        """Each animal subclass defines what it eats."""
        pass

    def __repr__(self):
        return f"{self.__class__.__name__}(name={self.name!r})"


# --- INHERITANCE: concrete animal classes extend Animal ---

class Lion(Animal):
    """Lion inherits from Animal and adds lion-specific behaviour."""
    required_enclosure = "Savannah"

    def __init__(self, name: str, weight: float, age: int, has_mane: bool):
        super().__init__(name, weight, age)
        self.has_mane = has_mane  # lion-specific attribute

    def make_sound(self) -> str:
        return "Roar!"

    def diet(self) -> str:
        return "meat"


class Giraffe(Animal):
    required_enclosure = "Savannah"

    def make_sound(self) -> str:
        return "Hum..."

    def diet(self) -> str:
        return "leaves"


class Zebra(Animal):
    required_enclosure = "Savannah"

    def make_sound(self) -> str:
        return "Bray!"

    def diet(self) -> str:
        return "grass"


class Antelope(Animal):
    required_enclosure = "Savannah"

    def make_sound(self) -> str:
        return "Snort!"

    def diet(self) -> str:
        return "grass and shrubs"


class Shark(Animal):
    required_enclosure = "Aquatic"

    def make_sound(self) -> str:
        return "(silence)"  # sharks make no sound

    def diet(self) -> str:
        return "fish and marine animals"

    def swim(self) -> str:
        return f"{self.name} is swimming."


# --- COMPOSITION: FeedingSchedule is composed into Enclosure ---
# Instead of inheriting a schedule, an Enclosure *has* a FeedingSchedule.
class FeedingSchedule:
    def __init__(self, frequency: str):
        # frequency examples: "daily", "weekly"
        self.frequency = frequency

    def __repr__(self):
        return f"FeedingSchedule({self.frequency!r})"


class Enclosure:
    """
    COMPOSITION: Enclosure owns a FeedingSchedule object and a list of Animals.
    This lets us swap or extend scheduling behaviour without subclassing Enclosure.
    """
    def __init__(
        self,
        name: str,
        temp_min: float,
        temp_max: float,
        feeding_schedule: FeedingSchedule,
    ):
        self.name = name
        self.temp_range = (temp_min, temp_max)
        # COMPOSITION: enclosure contains a feeding schedule
        self.feeding_schedule = feeding_schedule
        # COMPOSITION: enclosure contains a collection of animals
        self.animals: list[Animal] = []

    def add_animal(self, animal: Animal):
        self.animals.append(animal)

    def describe(self):
        print(f"\nEnclosure: {self.name}")
        print(f"  Temperature: {self.temp_range[0]}°C – {self.temp_range[1]}°C")
        print(f"  Feeding: {self.feeding_schedule.frequency}")
        print(f"  Animals ({len(self.animals)}):")
        for a in self.animals:
            print(f"    - {a.name} ({a.__class__.__name__}): needs {a.required_enclosure} enclosure, eats {a.diet()}, says '{a.make_sound()}'")


class Zoo:
    """Top-level container; owns a list of Enclosures (composition)."""
    def __init__(self, zoo_name: str):
        self.zoo_name = zoo_name
        # COMPOSITION: zoo contains enclosures
        self.enclosures: list[Enclosure] = []

    def add_enclosure(self, enclosure: Enclosure):
        self.enclosures.append(enclosure)

    def show(self):
        print(f"=== {self.zoo_name} ===")
        for enc in self.enclosures:
            enc.describe()


# --- Demo ---
if __name__ == "__main__":
    # Build animals
    lion = Lion("Simba", weight=190, age=5, has_mane=True)
    giraffe = Giraffe("Gerald", weight=800, age=7)
    zebra1 = Zebra("Zee", weight=350, age=3)
    antelope = Antelope("Annie", weight=60, age=2)
    shark = Shark("Bruce", weight=240, age=10)

    # Build enclosures with composed FeedingSchedule
    savannah = Enclosure("Savannah", 25, 31, FeedingSchedule("daily"))
    savannah.add_animal(zebra1)
    savannah.add_animal(giraffe)
    savannah.add_animal(antelope)

    # A separate lion enclosure
    lion_den = Enclosure("Lion Den", 24, 30, FeedingSchedule("daily"))
    lion_den.add_animal(lion)

    shark_tank = Enclosure("Shark Tank", 17, 18, FeedingSchedule("weekly"))
    shark_tank.add_animal(shark)

    zoo = Zoo("City Zoo")
    zoo.add_enclosure(savannah)
    zoo.add_enclosure(lion_den)
    zoo.add_enclosure(shark_tank)

    zoo.show()

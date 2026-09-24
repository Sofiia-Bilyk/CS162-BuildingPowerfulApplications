# Class hierarchy based on travel styles
# Structure:
#   Traveler (base)
#     ├── AdventureTraveler (level 1)
#     │     ├── Backpacker (level 2)
#     │     └── MountainClimber (level 2)
#     └── LuxuryTraveler (level 1)
#           ├── CruiseGoer (level 2)
#           └── ResortStayer (level 2)
#
# Polymorphic methods: pack() and describe_trip()


class Traveler:
    """Base class for all travelers."""

    def __init__(self, name, destination):
        self.name = name
        self.destination = destination

    def pack(self):
        """What the traveler puts in their bag."""
        return f"{self.name} packs the basics: passport, clothes, and cash."

    def describe_trip(self):
        """How the traveler describes their journey."""
        return f"{self.name} is heading to {self.destination}."

    def __str__(self):
        return f"{self.__class__.__name__}: {self.name} -> {self.destination}" #__class__ is needed to refer to the subclass where called instead of Traveler


class AdventureTraveler(Traveler):
    """Traveler who seeks outdoor and physical challenges."""

    def __init__(self, name, destination, activity):
        super().__init__(name, destination)
        self.activity = activity  # e.g. "hiking", "climbing"

    def pack(self):
        return f"{self.name} packs sturdy boots, a first-aid kit, and trail mix."

    def describe_trip(self):
        return (f"{self.name} is going to {self.destination} "
                f"for some serious {self.activity}!")


class LuxuryTraveler(Traveler):
    """Traveler who prefers comfort and premium services."""

    def __init__(self, name, destination, budget):
        super().__init__(name, destination)
        self.budget = budget  # budget in USD

    def pack(self):
        return f"{self.name} packs designer outfits, jewelry, and a laptop."

    def describe_trip(self):
        return (f"{self.name} is flying first-class to {self.destination} "
                f"with a ${self.budget:,} budget.")



class Backpacker(AdventureTraveler):
    """Adventure traveler who lives out of a single backpack."""

    def __init__(self, name, destination):
        super().__init__(name, destination, activity="backpacking")
        self.hostels_booked = 0  # backpackers rarely pre-book

    def pack(self):
        return (f"{self.name} packs everything into one 40L bag: "
                "sleeping bag, rain jacket, and instant noodles.")

    def describe_trip(self):
        return (f"{self.name} is wandering through {self.destination} "
                "with no fixed itinerary - pure freedom!")


class MountainClimber(AdventureTraveler):
    """Adventure traveler focused on reaching summits."""

    def __init__(self, name, destination, peak):
        super().__init__(name, destination, activity="climbing")
        self.peak = peak  # name of the mountain peak

    def pack(self):
        return (f"{self.name} packs crampons, an ice axe, rope, "
                "and high-altitude nutrition bars.")

    def describe_trip(self):
        return (f"{self.name} is attempting to climb {self.peak} "
                f"in {self.destination}. Wish them luck!")


class CruiseGoer(LuxuryTraveler):
    """Luxury traveler who explores destinations by cruise ship."""

    def __init__(self, name, destination, ship_name):
        super().__init__(name, destination, budget=5000)
        self.ship_name = ship_name

    def pack(self):
        return (f"{self.name} packs formal dinner attire, sunscreen, "
                "and a cocktail dress for every port.")

    def describe_trip(self):
        return (f"{self.name} is sailing the {self.destination} "
                f"aboard the {self.ship_name}.")


class ResortStayer(LuxuryTraveler):
    """Luxury traveler who relaxes at an all-inclusive resort."""

    def __init__(self, name, destination, resort_name):
        super().__init__(name, destination, budget=3000)
        self.resort_name = resort_name

    def pack(self):
        return (f"{self.name} packs swimwear, sunglasses, "
                "and a good book - nothing more needed.")

    def describe_trip(self):
        return (f"{self.name} is checking into {self.resort_name} "
                f"in {self.destination} and not leaving the pool.")




if __name__ == "__main__":
    travelers = [
        Backpacker("Sofia", "Southeast Asia"),
        MountainClimber("Liam", "Nepal", peak="Everest Base Camp"),
        CruiseGoer("Elena", "Mediterranean", ship_name="MSC Bellissima"),
        ResortStayer("Marco", "Maldives", resort_name="Soneva Fushi"),
    ]

    for traveler in travelers:
        print(traveler)           # __str__
        print(traveler.pack())           # polymorphic: pack()
        print(traveler.describe_trip())  # polymorphic: describe_trip()
        print()

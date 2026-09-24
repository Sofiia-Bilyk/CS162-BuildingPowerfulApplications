# dunder.py — demonstrates dunder methods in one Itinerary class

class Itinerary:
    """A travel itinerary: an ordered list of destination strings."""

    def __init__(self, destinations):
        """Initializes the itinerary with a list of destination names."""
        self.stops = list(destinations)

    def __repr__(self):
        """Returns an unambiguous string — shown in REPL and inside containers."""
        return f"Itinerary({self.stops})"

    def __eq__(self, other):
        """Two itineraries are equal if they have the same stops in the same order."""
        if not isinstance(other, Itinerary):
            return NotImplemented
        return self.stops == other.stops

    def __len__(self):
        """Returns the number of stops. Enables len() and truthiness checks."""
        return len(self.stops)

    def __contains__(self, destination):
        """Enables 'in' operator: 'Paris' in itinerary."""
        return destination in self.stops

    def __matmul__(self, other):
        """Merges two itineraries with '@': italy @ asia -> combined Itinerary."""
        if not isinstance(other, Itinerary):
            return NotImplemented
        return Itinerary(self.stops + other.stops)


if __name__ == "__main__":
    help(Itinerary)

    europe = Itinerary(["Rome", "Paris", "Berlin"])
    asia   = Itinerary(["Tokyo", "Bali"])
    europe2 = Itinerary(["Rome", "Paris", "Berlin"])

    print("__repr__:    ", repr(europe))
    print("__len__:     ", len(europe), "stops")
    print("__eq__:      ", europe == europe2)         # True
    print("__contains__:", "Paris" in europe)         # True
    print("__matmul__:  ", europe @ asia)             # merged itinerary

from enum import Enum, auto


# All possible actions on the platform
class Action(Enum):
    VIEW_CONTENT = auto()
    POST_IN_FORUM = auto()
    SEND_TO_BREAKOUT = auto()       # professor-level
    TOGGLE_STUDENT_DRAWING = auto() # privileged students or professors
    TECH_SUPPORT_ACCESS = auto()    # tech support only


# --- INHERITANCE: Person is the base class ---
# Students and Professors share a name and a set of base permissions.
class Person:
    # Default actions available to every authenticated user
    BASE_PERMISSIONS: set[Action] = {Action.VIEW_CONTENT, Action.POST_IN_FORUM}

    def __init__(self, name: str):
        self.name = name
        # COMPOSITION: each person holds their own permission set (built from class defaults)
        self._permissions: set[Action] = set(self.BASE_PERMISSIONS)
        # COMPOSITION: course roles stored as {course_id: role_label}
        self._course_roles: dict[str, str] = {}

    def grant(self, action: Action):
        """Grant an extra permission to this individual."""
        self._permissions.add(action)

    def can(self, action: Action) -> bool:
        """Check whether this person may perform an action."""
        return action in self._permissions

    def enroll(self, course_id: str, role: str):
        """Assign this person a role in a course."""
        self._course_roles[course_id] = role

    def role_in(self, course_id: str) -> str | None:
        return self._course_roles.get(course_id)

    def __repr__(self):
        return f"{self.__class__.__name__}({self.name!r})"


# --- INHERITANCE: Student and Professor extend Person ---

class Student(Person):
    """Students inherit base permissions; nothing extra by default."""
    pass


class Professor(Person):
    """
    INHERITANCE: Professors extend Person with additional default permissions
    that reflect their elevated role on the platform.
    """
    # Professors get everything students have, plus professor-specific actions
    BASE_PERMISSIONS: set[Action] = Person.BASE_PERMISSIONS | {
        Action.SEND_TO_BREAKOUT,
        Action.TOGGLE_STUDENT_DRAWING,
    }


# --- COMPOSITION: TechSupport wraps any Person to add support privileges ---
# We use composition (not inheritance) here so any person can become tech support
# without changing their class.
class TechSupport:
    """
    COMPOSITION: TechSupport is composed with a Person instance.
    It delegates identity to the wrapped person and adds full platform access.
    """
    def __init__(self, person: Person):
        self._person = person  # composed Person
        # Tech support can perform every action
        self._all_actions: set[Action] = set(Action)

    @property
    def name(self):
        return self._person.name

    def can(self, action: Action) -> bool:
        return action in self._all_actions

    def role_in(self, course_id: str) -> str | None:
        return self._person.role_in(course_id)

    def __repr__(self):
        return f"TechSupport({self._person.name!r})"


# --- Demo ---
if __name__ == "__main__":
    # Create users
    alice = Student("Alice")
    bob = Student("Bob")
    carol = Professor("Carol")
    dave = Professor("Dave")

    # Enroll in courses (COMPOSITION: roles live inside person objects)
    alice.enroll("CS101", "student")
    bob.enroll("CS101", "student")
    carol.enroll("CS101", "teacher")
    dave.enroll("CS101", "student")   # professor taking a class as student

    # Give Bob a special privilege (individual grant)
    bob.grant(Action.TOGGLE_STUDENT_DRAWING)

    # Wrap a tech-support person using composition
    tech = TechSupport(Student("Eve"))

    users = [alice, bob, carol, dave, tech]

    print("=== Permission Check ===")
    checks = [Action.VIEW_CONTENT, Action.SEND_TO_BREAKOUT,
              Action.TOGGLE_STUDENT_DRAWING, Action.TECH_SUPPORT_ACCESS]

    for user in users:
        perms = [a.name for a in checks if user.can(a)]
        print(f"{user!r:30s} -> {perms}")

    print("\n=== Course Roles ===")
    for user in users:
        role = user.role_in("CS101")
        print(f"  {user.name} in CS101: {role or '(not enrolled)'}")

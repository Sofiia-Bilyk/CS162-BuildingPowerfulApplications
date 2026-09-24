# PCW 16 – Inheritance & Composition

## Zoo Management (`zoo_management/zoo.py`)

**Inheritance**
- `Animal` (abstract base) → `Lion`, `Giraffe`, `Zebra`, `Antelope`, `Shark`
- Shared state (`name`, `weight`, `age`) and interface (`make_sound`, `diet`, `required_enclosure`) defined once in `Animal`; each subclass overrides only what differs

**Composition**
- `Enclosure` *has-a* `FeedingSchedule` — schedule behaviour is a separate object, not a subclass
- `Enclosure` *has-a* list of `Animal` objects
- `Zoo` *has-a* list of `Enclosure` objects

---

## Identity Access Management (`iam/iam.py`)

**Inheritance**
- `Person` (base) → `Student`, `Professor`
- `Professor` overrides `BASE_PERMISSIONS` to include elevated actions (`SEND_TO_BREAKOUT`, `TOGGLE_STUDENT_DRAWING`)

**Composition**
- Each `Person` *has-a* `_permissions` set — individual grants possible via `person.grant()`
- Each `Person` *has-a* `_course_roles` dict — roles are per-course, not class-wide
- `TechSupport` *wraps* any `Person` — adds full platform access without modifying the person's class

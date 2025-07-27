from statemachine import StateMachine, State
from backend.models import PetState

class PetStateMachine(StateMachine):
    egg = State('Egg', initial=True)
    baby = State('Baby')
    teen = State('Teen')
    adult = State('Adult')
    dead = State('Dead')

    hatch = egg.to(baby)
    grow_to_teen = baby.to(teen)
    grow_to_adult = teen.to(adult)
    die = (egg.to(dead) | baby.to(dead) | teen.to(dead) | adult.to(dead))

    def on_hatch(self):
        pass  # логика при переходе из яйца в детеныша

    def on_grow_to_teen(self):
        pass  # логика при переходе в подростка

    def on_grow_to_adult(self):
        pass  # логика при переходе во взрослого

    def on_die(self):
        pass  # логика при смерти 
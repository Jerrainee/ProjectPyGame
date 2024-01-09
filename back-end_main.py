from random import randint

"""
ТЕМА, ОБЯЗАТЕЛЬНО СОЕДИНИ БЭК С ФРОНТОМ, ИНАЧЕ ЭТО ВСЕ РАБОТАТЬ НЕ БУДЕТ И ПАША ТИЛЬТАНЕТ (((

ПЕРЕОПРЕДЕЛЯТЬ ФУНКЦИИ НЕ НАДО.
ДОБАВЬТЕ БАЗОВЫЕ ПОЛЯ КЛАССОВ, ДОБАВЬТЕ ФУНКЦИИ И ТРЕБУЕМЫЙ ФУНКЦИОНАЛ ДЛЯ СВЯЗИ ВЗАИМОДЕЙСТВИЯ
"""


class Score:
    def __init__(self):
        self.score = 0.0
        self.exp = 0.0
        self.level = 1

    def add_score(self, value, coef):
        if coef == 0.0:
            self.score += value

            self.exp += value
        else:
            self.score += value * coef

            self.exp += value * coef

        self.check_level()

    def check_level(self):
        exp = self.exp

        if exp > 100:
            exp -= 100

            self.level += 1

        else:
            pass

        self.exp = exp

    def remove_score(self, value):
        self.score -= value


class Item:
    def __init__(self, name, id, type):
        self.name = name
        self.id = id
        self.type = type

    def __del__(self):
        del self.name
        del self.id
        del self.type

    def get_id(self):
        return self.id

    def get_name(self):
        return self.name

    def get_type(self):
        return self.type


class Boss:
    def __init__(self, hero):
        self.base_health = Health(20)
        self.soul = Soul(0.5)
        self.charge = 0.0
        self.dead_cond = False
        self.hero = hero

    def deal_damage(self):
        self.base_health.received_hit()

        self.check_death_state()

    def give_short_damage(self):
        self.soul.given_hit()

        if self.soul.soul_state is True:
            should_crit = True if randint(1, 2) == 10 else False

            if should_crit:
                self.hero.base_health.received_hit()
                self.hero.base_health.received_hit()
                self.soul.reset()
            else:
                self.hero.base_health.received_hit()
        else:
            self.hero.base_health.received_hit()

        self.charge_long_distance_shot()

    def give_long_damage(self):
        if self.charge == 100:
            self.soul.given_hit()

            if self.soul.soul_state is True:
                should_crit = True if randint(1, 2) == 10 else False

                if should_crit:
                    self.hero.base_health.received_hit()
                    self.hero.base_health.received_hit()
                    self.soul.reset()
                else:
                    self.hero.base_health.received_hit()
            else:
                self.hero.base_health.received_hit()
            self.charge = 0.0
        else:
            print('Not charged yet.')

        #  лонгшот должен отличаться от обычного удара и надо его эпик его нарисовать

    def charge_long_distance_shot(self):
        self.charge += 25

    def is_dead(self):
        return self.dead_cond

    def death_condition_met(self):
        print('Enemy (type=Boss) is dead.')

        should_drop_anything = None

        if randint(1, 10) == 1:
            should_drop_anything = True

        else:
            should_drop_anything = False

        if should_drop_anything:
            self.drop_items()

        self.give_hero_score()

        print("Death of Boss validated. Deleting miniboss.")

        del self

    def drop_items(self):
        item = None  # выберите рандомный айтем и присвойте его этой переменной

        # киньте этот айтем на поле и дайте игроку возможность его подобрать и пусть игрок подбирает

    def give_hero_score(self):
        basic_value = 100

        self.hero.exp.add_score(basic_value)

    def check_death_state(self):
        hp = []

        for i in range(len(self.base_health.base_health)):
            hp.append(self.base_health.base_health[i])

        hp_set = set(hp)

        if hp_set == {0}:
            self.dead_cond = True

            print('Boss death condition met! Initiating basic response to death -> defcon method')

            self.death_condition_met()

        else:
            print('Boss is still alive.')


class MiniBoss:
    def __init__(self, hero):
        self.base_health = Health(10)
        self.soul = Soul(0.33)
        self.charge = 0.0
        self.dead_cond = False
        self.hero = hero

    def deal_damage(self):
        self.base_health.received_hit()

        self.check_death_state()

    def give_short_damage(self):
        self.soul.given_hit()

        if self.soul.soul_state is True:
            should_crit = True if randint(1, 10) == 10 else False

            if should_crit:
                self.hero.base_health.received_hit()
                self.hero.base_health.received_hit()
                self.soul.reset()
            else:
                self.hero.base_health.received_hit()
        else:
            self.hero.base_health.received_hit()

        self.charge_long_distance_shot()

    def give_long_damage(self):
        if self.charge == 100:
            self.soul.given_hit()

            if self.soul.soul_state is True:
                should_crit = True if randint(1, 10) == 10 else False

                if should_crit:
                    self.hero.base_health.received_hit()
                    self.hero.base_health.received_hit()
                    self.soul.reset()
                else:
                    self.hero.base_health.received_hit()
            else:
                self.hero.base_health.received_hit()
            self.charge = 0.0
        else:
            print('Not charged yet.')

        #  лонгшот должен отличаться от обычного удара и надо его эпик его нарисовать

    def charge_long_distance_shot(self):
        self.charge += 25

    def is_dead(self):
        return self.dead_cond

    def death_condition_met(self):
        print('Enemy (type=Miniboss) is dead.')

        should_drop_anything = None

        if randint(1, 10) == 1:
            should_drop_anything = True

        else:
            should_drop_anything = False

        if should_drop_anything:
            self.drop_items()

        self.give_hero_score()

        print("Death of miniboss validated. Deleting miniboss.")

        del self

    def drop_items(self):
        item = None  # выберите рандомный айтем и присвойте его этой переменной

        # киньте этот айтем на поле и дайте игроку возможность его подобрать и пусть игрок подбирает

    def give_hero_score(self):
        basic_value = randint(25, 40)

        self.hero.exp.add_score(basic_value)

    def check_death_state(self):
        hp = []

        for i in range(len(self.base_health.base_health)):
            hp.append(self.base_health.base_health[i])

        hp_set = set(hp)

        if hp_set == {0}:
            self.dead_cond = True

            print('Mini boss death condition met! Initiating basic response to death -> defcon method')

            self.death_condition_met()

        else:
            print('Mini boss is still alive.')


class Enemy:
    def __init__(self, hero):
        self.base_health = Health(3)
        self.soul = Soul(0.1)
        self.dead_cond = False
        self.hero = hero

    def deal_damage(self):
        self.base_health.received_hit()

        self.check_death_state()

    def give_damage(self):
        self.soul.given_hit()

        if self.soul.soul_state is True:
            should_crit = True if randint(1, 10) == 10 else False

            if should_crit:
                self.hero.base_health.received_hit()
                self.hero.base_health.received_hit()
                self.soul.reset()
            else:
                self.hero.base_health.received_hit()
        else:
            self.hero.base_health.received_hit()

    def is_dead(self):
        return self.dead_cond

    def death_condition_met(self):
        print('Enemy (type=Enemy) is dead.')

        should_drop_anything = None

        if randint(1, 10) == 1:
            should_drop_anything = True

        else:
            should_drop_anything = False

        if should_drop_anything:
            self.drop_items()

        self.give_hero_score()

        print("Death of enemy validated. Deleting entity.")

        del self

    def drop_items(self):
        item = None  # выберите рандомный айтем и присвойте его этой переменной

        # киньте этот айтем на поле и дайте игроку возможность его подобрать и пусть игрок его подбирает

    def give_hero_score(self):
        basic_value = randint(10, 25)

        self.hero.exp.add_score(basic_value)

    def check_death_state(self):
        hp = []

        for i in range(len(self.base_health.base_health)):
            hp.append(self.base_health.base_health[i])

        hp_set = set(hp)

        if hp_set == {0}:
            self.dead_cond = True

            print('Enemy death condition met! Initiating basic response to death -> defcon method')

            self.death_condition_met()

        else:
            print('Enemy is still alive.')


class Hero:
    def __init__(self):
        self.base_health = Health(5)
        self.soul = Soul(0.25)
        self.exp = Score()
        self.attack_buff = False
        self.items = {'medical': [], 'attack': [], 'defense': [], 'soul': [], 'key': [], 'misc': []}

    def restore_health(self):
        self.base_health.restore_health(self)

    def damage(self, enemy):
        self.soul.given_hit()

        if self.soul.soul_state is True:
            should_crit = True if randint(1, 10) == 10 else False

            if should_crit:
                enemy.deal_damage()
                enemy.deal_damage()
                self.soul.reset()
            else:
                enemy.deal_damage()
        else:
            enemy.deal_damage()

            if self.attack_buff:
                enemy.deal_damage()
                self.attack_buff = False

        self.exp.add_score(25, 1)

    def received_hit(self):
        self.base_health.received_hit()

    def used_defensive_item(self, item):
        times = item.def_value

        for i in range(times):
            self.base_health.add_health()

        item_id = item.id

        index = 0
        for i in range(len(self.items['defense'])):
            if item_id == self.items['defense'][i].id:
                index = i

        self.items['defense'].pop(index)

    def used_attack_item(self, item):
        self.attack_buff = True

        item_id = item.id

        index = 0
        for i in range(len(self.items['attack'])):
            if item_id == self.items['attack'][i].id:
                index = i

        self.items['attack'].pop(index)

    def used_key(self, key):
        chest_is_here = None  # сделайте проверку, есть ли в зоне использования сундук

        if chest_is_here:
            self.items['key'].pop()
            # открытие сундука, поздравление игрока

        else:
            print("Can't use key here. There are no chests nearby.")

    def used_medical_item(self, item):
        item_name = item.name

        if item_name == 'heal':
            self.base_health.restore_health(self)

        elif item_name == 'hp':
            self.base_health.add_health()

        item_id = item.id

        index = 0
        for i in range(len(self.items['medical'])):
            if item_id == self.items['medical'][i].id:
                index = i

        self.items['medical'].pop(index)

    def used_soul_item(self, item):
        item_name = item.name

        if item_name == "increment":
            self.soul.usual_increment += 0.25
        elif item_name == 'base_charge':
            self.soul.charged()

        item_id = item.id

        index = 0
        for i in range(len(self.items['soul'])):
            if item_id == self.items['soul'][i].id:
                index = i

        self.items['soul'].pop(index)

    def used_misc_item(self, item):
        print("Can't use misc items.")

    def picked_up_item(self, item):
        if item.type == 'medical':
            self.items['medical'].append(item)

        elif item.type == 'attack':
            self.items['attack'].append(item)

        elif item.type == 'defense':
            self.items['defense'].append(item)

        elif item.type == 'soul':
            self.items['soul'].append(item)

        elif item.type == 'key':
            self.items['key'].append(item)

        else:
            self.items['misc'].append(item)


class Health:
    def __init__(self, amount):
        self.base_health = []

        for i in range(amount):
            self.base_health.append(1)

    def received_hit(self):
        for i in range(len(self.base_health) - 1, 0, -1):

            if self.base_health[i] == 1:
                self.base_health[i] = 0

                if set(self.base_health) == {0}:
                    print("Hero is dead.")

                break
        else:
            print("Hero is dead.")

    def restore_health(self, hero):
        if hero.soul.soul_state or 'heal' in hero.items:  # надо добавить айтемы в игру!!!!

            for i in range(len(self.base_health) - 1):

                if self.base_health[i] == 0:
                    self.base_health[i] = 1
                    hero.soul_state = False
                    break
            else:
                print("Base health already satisfied.")
        else:
            print("Soul state criteria is not met.")

    def add_health(self):
        self.base_health = [1] + self.base_health


class Soul:
    def __init__(self, usual_increment):
        self.soul_state = False
        self.soul_cond = 0.0
        self.usual_increment = usual_increment

    def given_hit(self):
        self.soul_cond += self.usual_increment
        if self.soul_cond >= 1:
            self.soul_cond = 1
            self.soul_state = True

    def reset(self):
        self.soul_state = False
        self.soul_cond = 0.0

    def charged(self):
        self.soul_state = True
        self.soul_cond = 1


hero = Hero()
# test commands here

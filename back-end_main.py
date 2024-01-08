from random import randint


class EnemyEntity:
    def __init__(self):
        self.base_health = Health(3)
        self.soul = Soul(0.1)

    def deal_damage(self):
        pass

    def give_damage(self, hero):
        pass


class Hero:
    def __init__(self):
        self.base_health = Health(5)
        self.soul = Soul(0.25)
        self.exp = 0
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
        pass

    def used_key(self, key):
        pass

    def used_medical_item(self, item):
        pass

    def used_soul_item(self, item):
        pass

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
        if hero.soul.soul_state or 'heal' in hero.items:  # необходимо добавить айтемы в игру!

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


hero = Hero()
# test commands here




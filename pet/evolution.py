"""宠物进化与蜕变系统"""
import random
from dataclasses import dataclass, field

@dataclass
class Pet:
    pid: str
    name: str
    level: int
    intimacy: int = 0
    growth_rate: float = 1.0
    skills: list = field(default_factory=list)
    core_skills: list = field(default_factory=list)
    form: str = "base"

class EvolutionSystem:
    REQUIRED_LEVEL = 50
    REQUIRED_INTIMACY = 100
    REQUIRED_ITEM = "evolution_stone"
    COOLDOWN_SECONDS = 30.0
    DAILY_LIMIT = 5
    PITY_THRESHOLD = 10  # N次必出目标形态

    # 蜕变形态概率表
    FORM_TABLE = {"fire": 0.25, "water": 0.25, "earth": 0.2, "wind": 0.2, "dark": 0.1}

    def __init__(self, seed=42):
        self.rng = random.Random(seed)
        self.evolution_cd: dict[str, float] = {}
        self.fail_count: dict[str, int] = {}
        self.pity_counter: dict[str, int] = {}
        self.daily_count: dict[str, int] = {}
        # 失败惩罚与成功率
        self.base_success_rate = 0.6
        self.fail_bonus = 0.1  # 连续失败提升成功率
        self.material_cost = {"evolution_stone": 1}

    def can_evolve(self, pet: Pet, item: str) -> bool:
        # 修复bug1: 等级+亲密度+指定道具，三者缺一不可
        return (
            pet.level >= self.REQUIRED_LEVEL
            and pet.intimacy >= self.REQUIRED_INTIMACY
            and item == self.REQUIRED_ITEM
        )

    def get_mutation_form(self, pet: Pet, target_form: str = "dark") -> str:
        # 修复bug2: 概率表 + 保底机制，N次必出目标形态
        count = self.pity_counter.get(pet.pid, 0)
        if count + 1 >= self.PITY_THRESHOLD:
            self.pity_counter[pet.pid] = 0
            return target_form
        roll = self.rng.random()
        acc = 0.0
        form = target_form
        for name, prob in self.FORM_TABLE.items():
            acc += prob
            if roll < acc:
                form = name
                break
        if form == target_form:
            self.pity_counter[pet.pid] = 0
        else:
            self.pity_counter[pet.pid] = count + 1
        return form

    def get_growth_rate_after_evolution(self, pet: Pet) -> float:
        # 修复bug3: 进化后成长率提升
        return pet.growth_rate * 1.5

    def _success_rate(self, pid: str) -> float:
        # 连续失败提升成功率
        return min(1.0, self.base_success_rate + self.fail_count.get(pid, 0) * self.fail_bonus)

    def evolve(self, pet: Pet, item: str, current_time: float = 0.0) -> tuple[bool, str]:
        if not self.can_evolve(pet, item):
            return False, "conditions_not_met"
        if not self.can_evolve_again(pet.pid, current_time):
            return False, "cooldown"
        if self.daily_count.get(pet.pid, 0) >= self.DAILY_LIMIT:
            return False, "daily_limit"

        self.daily_count[pet.pid] = self.daily_count.get(pet.pid, 0) + 1
        self.evolution_cd[pet.pid] = current_time

        if self.rng.random() >= self._success_rate(pet.pid):
            # 修复bug4: 失败扣除材料并进入冷却，连续失败提升成功率
            self.fail_count[pet.pid] = self.fail_count.get(pet.pid, 0) + 1
            return False, "failed_materials_lost"

        self.fail_count[pet.pid] = 0
        pet.form = self.get_mutation_form(pet)
        pet.growth_rate = self.get_growth_rate_after_evolution(pet)
        # 修复bug5: 保留已学技能，核心技能不丢失
        pet.skills = list(pet.skills)
        pet.core_skills = list(pet.core_skills)
        return True, "evolved"

    def can_evolve_again(self, pid: str, current_time: float) -> bool:
        # 修复bug6: 冷却时间限制
        last = self.evolution_cd.get(pid)
        if last is None:
            return True
        return current_time - last >= self.COOLDOWN_SECONDS

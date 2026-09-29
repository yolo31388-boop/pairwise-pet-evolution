"""宠物进化与蜕变系统"""
import random
from dataclasses import dataclass, field

REQUIRED_LEVEL = 50
REQUIRED_INTIMACY = 100
REQUIRED_ITEM = "evolution_stone"

MUTATION_FORMS = ["fire", "water", "earth", "wind", "dark"]
MUTATION_PITY = 10  # 连续N次未出新形态后必出未获得过的形态

GROWTH_RATE_BONUS = 0.5  # 进化后成长率提升

EVOLUTION_COOLDOWN = 50.0  # 进化冷却秒数
DAILY_EVOLVE_LIMIT = 5  # 每日进化次数上限


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
    def __init__(self, seed=42):
        self.rng = random.Random(seed)
        self.evolution_cd: dict[str, float] = {}
        self.fail_count: dict[str, int] = {}
        self.pity_counter: dict[str, int] = {}
        self.seen_forms: dict[str, set] = {}
        self.daily_count: dict[str, int] = {}
        # 失败惩罚与成功率
        self.base_success_rate = 0.6
        self.fail_bonus = 0.1  # 每次连续失败提升的成功率
        self.material_cost = {"evolution_stone": 1}

    def can_evolve(self, pet: Pet, item: str) -> bool:
        # 等级 + 亲密度 + 指定道具，三者缺一不可
        return (
            pet.level >= REQUIRED_LEVEL
            and pet.intimacy >= REQUIRED_INTIMACY
            and item == REQUIRED_ITEM
        )

    def get_mutation_form(self, pet: Pet) -> str:
        # 概率表 + 保底：连续未出新形态达到阈值后必出未获得过的形态
        pid = pet.pid
        self.pity_counter[pid] = self.pity_counter.get(pid, 0) + 1
        seen = self.seen_forms.setdefault(pid, set())
        unseen = [f for f in MUTATION_FORMS if f not in seen]
        if unseen and self.pity_counter[pid] >= MUTATION_PITY:
            form = self.rng.choice(unseen)
            self.pity_counter[pid] = 0
        else:
            form = self.rng.choice(MUTATION_FORMS)
            if form not in seen:
                self.pity_counter[pid] = 0
        seen.add(form)
        return form

    def get_growth_rate_after_evolution(self, pet: Pet) -> float:
        # 进化后成长率提升，每级属性增加更多
        return pet.growth_rate + GROWTH_RATE_BONUS

    def evolve(self, pet: Pet, item: str, current_time: float = 0.0) -> tuple[bool, str]:
        if not self.can_evolve_again(pet.pid, current_time):
            return False, "cooldown"
        if self.daily_count.get(pet.pid, 0) >= DAILY_EVOLVE_LIMIT:
            return False, "daily_limit"
        if not self.can_evolve(pet, item):
            return False, "cannot"

        # 失败概率：连续失败提升成功率；失败扣除材料并进入冷却
        success_rate = min(
            1.0, self.base_success_rate + self.fail_count.get(pet.pid, 0) * self.fail_bonus
        )
        self.evolution_cd[pet.pid] = current_time
        self.daily_count[pet.pid] = self.daily_count.get(pet.pid, 0) + 1
        if self.rng.random() >= success_rate:
            self.fail_count[pet.pid] = self.fail_count.get(pet.pid, 0) + 1
            return False, "failed"

        self.fail_count[pet.pid] = 0
        pet.form = self.get_mutation_form(pet)
        pet.growth_rate = self.get_growth_rate_after_evolution(pet)
        # 保留已学技能，核心技能不丢失
        for skill in pet.core_skills:
            if skill not in pet.skills:
                pet.skills.append(skill)
        return True, "evolved"

    def can_evolve_again(self, pid: str, current_time: float) -> bool:
        last = self.evolution_cd.get(pid)
        if last is None:
            return True
        return current_time - last >= EVOLUTION_COOLDOWN

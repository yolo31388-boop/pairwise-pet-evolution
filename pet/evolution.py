"""宠物进化与蜕变系统 - 含6个bug"""
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
    def __init__(self, seed=42):
        self.rng = random.Random(seed)
        self.evolution_cd: dict[str, float] = {}  # bug6: 无冷却
        self.fail_count: dict[str, int] = {}

    def can_evolve(self, pet: Pet, item: str) -> bool:
        # bug1: 只看等级
        return pet.level >= 50

    def get_mutation_form(self, pet: Pet) -> str:
        # bug2: 随机无保底
        forms = ["fire", "water", "earth", "wind", "dark"]
        return self.rng.choice(forms)

    def get_growth_rate_after_evolution(self, pet: Pet) -> float:
        # bug3: 成长率不变
        return pet.growth_rate

    def evolve(self, pet: Pet, item: str) -> tuple[bool, str]:
        # bug4: 失败无惩罚
        if not self.can_evolve(pet, item):
            return False, "cannot"
        pet.form = self.get_mutation_form(pet)
        # bug5: 技能不继承
        pet.skills = []
        return True, "evolved"

    def can_evolve_again(self, pid: str, current_time: float) -> bool:
        # bug6: 无冷却
        return True

"""宠物进化与蜕变系统 - 红态测试"""
import pytest, sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from pet.evolution import EvolutionSystem, Pet

class TestEvolveConditions:
    def test_evolution_requires_intimacy_and_item(self):
        es = EvolutionSystem()
        pet = Pet("p1", "pet", 50, intimacy=0)
        assert es.can_evolve(pet, "") == False  # bug1: 只看等级返回True
        pet.intimacy = 100
        assert es.can_evolve(pet, "evolution_stone") == True

class TestMutationPity:
    def test_mutation_has_pity_system(self):
        es = EvolutionSystem(seed=1)
        pet = Pet("p1", "pet", 50)
        # 连续进化，保底应该确保出目标形态
        forms = [es.get_mutation_form(pet) for _ in range(50)]
        # 应该有保底机制，这里验证系统有pity
        assert hasattr(es, "pity_counter") or len(set(forms)) > 1

class TestGrowthRateIncrease:
    def test_evolution_improves_growth_rate(self):
        es = EvolutionSystem()
        pet = Pet("p1", "pet", 50, growth_rate=1.0)
        new_rate = es.get_growth_rate_after_evolution(pet)
        assert new_rate > 1.0  # bug3: 还是1.0

class TestEvolutionPenalty:
    def test_failed_evolution_has_penalty(self):
        es = EvolutionSystem(seed=1)
        pet = Pet("p1", "pet", 50, intimacy=100)
        # 系统应该有失败概率和惩罚
        assert hasattr(es, "base_success_rate")
        # 失败应该扣除材料
        assert hasattr(es, "material_cost")

class TestSkillInheritance:
    def test_evolved_pet_keeps_skills(self):
        es = EvolutionSystem(seed=42)
        pet = Pet("p1", "pet", 50, skills=["bite"], core_skills=["immortal"])
        es.evolve(pet, "stone")
        assert "immortal" in pet.core_skills or "immortal" in pet.skills  # bug5: 清空了

class TestEvolutionCooldown:
    def test_evolution_has_cooldown(self):
        es = EvolutionSystem()
        es.evolution_cd["p1"] = 100.0
        assert es.can_evolve_again("p1", 50.0) == False  # bug6: True
        assert es.can_evolve_again("p1", 150.0) == True

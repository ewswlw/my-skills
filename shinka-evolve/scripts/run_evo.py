"""Template evolution launcher using ShinkaEvolve Python API.

Copy this to your task directory and customize as needed.
Defaults: Gemini-only, 50 generations, 2 islands, $5 budget cap.
"""
from __future__ import annotations

from shinka.core import ShinkaEvolveRunner, EvolutionConfig
from shinka.database import DatabaseConfig
from shinka.launch import LocalJobConfig


def main():
    job_conf = LocalJobConfig(eval_program_path="evaluate.py")

    db_conf = DatabaseConfig(
        num_islands=2,
        archive_size=40,
        elite_selection_ratio=0.3,
        migration_interval=10,
    )

    evo_conf = EvolutionConfig(
        init_program_path="initial.py",
        num_generations=50,
        language="python",
        llm_models=["gemini-2.5-flash-preview", "gemini-2.5-pro-preview"],
        llm_dynamic_selection="ucb",
        llm_kwargs={"temperatures": [0.0, 0.5, 1.0], "max_tokens": 16384},
        embedding_model=None,
        max_api_costs=5.0,
        patch_types=["diff", "full", "cross"],
        patch_type_probs=[0.6, 0.3, 0.1],
        meta_rec_interval=10,
        meta_llm_models=["gemini-2.5-flash-preview"],
        use_text_feedback=False,
    )

    runner = ShinkaEvolveRunner(
        evo_config=evo_conf,
        job_config=job_conf,
        db_config=db_conf,
        max_evaluation_jobs=2,
        max_proposal_jobs=2,
        max_db_workers=4,
    )
    runner.run()


if __name__ == "__main__":
    main()

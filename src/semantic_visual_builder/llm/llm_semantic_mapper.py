"""Controlled LLM semantic mapping with deterministic fallback support."""

from __future__ import annotations

from semantic_visual_builder.data.data_profiler import DatasetProfile
from semantic_visual_builder.knowledge.graph_matrix import GraphMatrix
from semantic_visual_builder.knowledge.product_kb import ProductKnowledgeBase
from semantic_visual_builder.llm.json_repair import JsonRepair
from semantic_visual_builder.llm.llm_mapping_result import (
    LlmMappingResult,
    LlmVisualPlanDraft,
)
from semantic_visual_builder.llm.llm_response_parser import LlmResponseParser
from semantic_visual_builder.llm.ollama_client import OllamaClient
from semantic_visual_builder.llm.prompt_builder import VisualIntentPromptBuilder
from semantic_visual_builder.llm.prompts import (
    VISUAL_INTENT_MAPPING_SYSTEM_PROMPT,
    VISUAL_REFINEMENT_SYSTEM_PROMPT,
    VISUAL_REPAIR_SYSTEM_PROMPT,
)
from semantic_visual_builder.planning.visual_plan_schema import VisualPlan
from semantic_visual_builder.validation.llm_output_validator import LlmOutputValidator


class LlmSemanticMapper:
    """Use Ollama for strict JSON semantic mapping."""

    def __init__(
        self,
        ollama_client: OllamaClient,
        prompt_builder: VisualIntentPromptBuilder,
        response_parser: LlmResponseParser,
        output_validator: LlmOutputValidator,
        json_repair: JsonRepair,
    ):
        self.ollama_client = ollama_client
        self.prompt_builder = prompt_builder
        self.response_parser = response_parser
        self.output_validator = output_validator
        self.json_repair = json_repair

    def map_to_draft(
        self,
        model: str,
        user_message: str,
        dataset_profile: DatasetProfile | None,
        product_kb: ProductKnowledgeBase | None,
        graph_matrix: GraphMatrix | None,
        current_plan_summary: str | None = None,
        current_plan: VisualPlan | None = None,
    ) -> LlmMappingResult:
        raw_response = ""
        if current_plan is not None:
            prompt = self.prompt_builder.build_refinement_prompt(
                user_message=user_message,
                dataset_profile=dataset_profile,
                product_kb=product_kb,
                graph_matrix=graph_matrix,
                current_plan=current_plan,
            )
        else:
            prompt = self.prompt_builder.build_prompt(
                user_message=user_message,
                dataset_profile=dataset_profile,
                product_kb=product_kb,
                graph_matrix=graph_matrix,
                current_plan_summary=current_plan_summary,
            )
        try:
            raw_response = self.ollama_client.generate(
                model=model,
                prompt=prompt,
                system=VISUAL_REFINEMENT_SYSTEM_PROMPT
                if current_plan is not None
                else VISUAL_INTENT_MAPPING_SYSTEM_PROMPT,
                temperature=0.0,
            )
        except Exception as exc:
            return LlmMappingResult(
                raw_response="", parsed_json=None, draft=None, errors=[str(exc)]
            )

        parsed_json = None
        used_repair = False
        try:
            parsed_json = self.response_parser.parse_json_response(raw_response)
        except ValueError as exc:
            repair_prompt = self.json_repair.build_repair_prompt(raw_response, str(exc))
            try:
                repaired_response = self.ollama_client.generate(
                    model=model,
                    prompt=repair_prompt,
                    system=VISUAL_REPAIR_SYSTEM_PROMPT,
                    temperature=0.0,
                )
                raw_response = repaired_response
                parsed_json = self.response_parser.parse_json_response(
                    repaired_response
                )
                used_repair = True
            except Exception as repair_exc:
                return LlmMappingResult(
                    raw_response=raw_response,
                    parsed_json=None,
                    draft=None,
                    used_repair=used_repair,
                    errors=[str(exc), str(repair_exc)],
                )

        if parsed_json is None:
            return LlmMappingResult(
                raw_response=raw_response,
                parsed_json=None,
                draft=None,
                errors=["LLM response could not be parsed."],
            )

        validation = self.output_validator.validate_draft_json(
            parsed_json, graph_matrix
        )
        if not validation.is_valid:
            return LlmMappingResult(
                raw_response=raw_response,
                parsed_json=parsed_json,
                draft=None,
                used_repair=used_repair,
                errors=[message.message for message in validation.messages],
            )

        try:
            draft = self._draft_from_json(parsed_json)
        except ValueError as exc:
            return LlmMappingResult(
                raw_response=raw_response,
                parsed_json=parsed_json,
                draft=None,
                used_repair=used_repair,
                errors=[str(exc)],
            )

        return LlmMappingResult(
            raw_response=raw_response,
            parsed_json=parsed_json,
            draft=draft,
            used_repair=used_repair,
            errors=[],
        )

    def _draft_from_json(self, data: dict[str, object]) -> LlmVisualPlanDraft:
        roles = data.get("roles")
        if not isinstance(roles, dict):
            raise ValueError("roles must be an object.")
        style = data.get("style")
        if style is None:
            style = {}
        elif not isinstance(style, dict):
            raise ValueError("style must be an object.")
        action = self._optional_str(data, "action")
        chart_type = self._optional_str(data, "chart_type")
        diagram_type = self._optional_str(data, "diagram_type")
        renderer = self._optional_str(data, "renderer")
        confidence = data.get("confidence")
        return LlmVisualPlanDraft(
            visual_kind=str(data.get("visual_kind", "")),
            intent=str(data.get("intent", "")),
            action=action,
            chart_type=chart_type,
            diagram_type=diagram_type,
            roles=roles,
            filters=self._optional_list(data, "filters"),
            grouping=self._optional_list(data, "grouping"),
            style=style,
            renderer=renderer,
            confidence=float(confidence) if confidence is not None else None,
            assumptions=self._optional_list(data, "assumptions"),
            questions=self._optional_list(data, "questions"),
            diagram_nodes=self._optional_list(data, "diagram_nodes"),
            diagram_edges=self._optional_list(data, "diagram_edges"),
        )

    def _optional_str(self, data: dict[str, object], key: str) -> str | None:
        value = data.get(key)
        if value is None or isinstance(value, str):
            return value
        return str(value)

    def _optional_list(self, data: dict[str, object], key: str) -> list[object]:
        value = data.get(key)
        if isinstance(value, list):
            return list(value)
        return []

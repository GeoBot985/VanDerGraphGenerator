"""Coordinate multi-turn visual plan refinement."""

from __future__ import annotations

from dataclasses import dataclass, field

from semantic_visual_builder.llm.llm_mapping_result import LlmMappingResult
from semantic_visual_builder.llm.llm_semantic_mapper import LlmSemanticMapper
from semantic_visual_builder.planning.clarification import ClarificationOption, ClarificationRequest
from semantic_visual_builder.planning.clarification_engine import ClarificationEngine
from semantic_visual_builder.planning.deterministic_fallback_patch_planner import (
    DeterministicFallbackPatchPlanner,
)
from semantic_visual_builder.planning.field_mapper import FieldMapper
from semantic_visual_builder.planning.visual_plan import get_role
from semantic_visual_builder.planning.visual_plan import summarize_visual_plan
from semantic_visual_builder.planning.visual_plan_patch import VisualPlanPatch
from semantic_visual_builder.planning.visual_plan_patch_applier import (
    VisualPlanPatchApplier,
)
from semantic_visual_builder.planning.visual_plan_schema import VisualPlan
from semantic_visual_builder.state.app_state import AppState
from semantic_visual_builder.validation.capability_validator import CapabilityValidator
from semantic_visual_builder.validation.validation_result import ValidationResult
from semantic_visual_builder.validation.visual_plan_validator import VisualPlanValidator


@dataclass
class RefinementResult:
    visual_plan: VisualPlan | None
    validation_result: ValidationResult
    mapping_method: str
    clarification_requests: list[ClarificationRequest] = field(default_factory=list)
    used_fallback: bool = False
    messages: list[str] = field(default_factory=list)


class RefinementOrchestrator:
    """Refine an accepted plan using LLM or deterministic fallbacks."""

    def __init__(
        self,
        llm_mapper: LlmSemanticMapper,
        deterministic_refinement_engine: object | None = None,
        field_mapper: FieldMapper | None = None,
        visual_plan_validator: VisualPlanValidator | None = None,
        capability_validator: CapabilityValidator | None = None,
        clarification_engine: ClarificationEngine | None = None,
        deterministic_fallback_patch_planner: DeterministicFallbackPatchPlanner
        | None = None,
        patch_applier: VisualPlanPatchApplier | None = None,
    ):
        self.llm_mapper = llm_mapper
        self.deterministic_refinement_engine = deterministic_refinement_engine
        self.field_mapper = field_mapper or FieldMapper()
        self.deterministic_fallback_patch_planner = (
            deterministic_fallback_patch_planner or DeterministicFallbackPatchPlanner()
        )
        self.patch_applier = patch_applier or VisualPlanPatchApplier()
        self.visual_plan_validator = visual_plan_validator or VisualPlanValidator()
        self.capability_validator = capability_validator or CapabilityValidator()
        self.clarification_engine = clarification_engine or ClarificationEngine()

    def refine_plan(
        self,
        current_plan: VisualPlan,
        user_message: str,
        app_state: AppState,
        use_llm: bool = True,
    ) -> RefinementResult:
        dataset_profile = app_state.dataset_context.profile
        product_kb = app_state.product_kb
        graph_matrix = app_state.graph_matrix
        selected_model = app_state.model_registry.selected_model
        messages: list[str] = []
        llm_result = None
        attempted_llm = bool(
            use_llm and app_state.llm_mapping_enabled and selected_model
        )

        if attempted_llm:
            llm_result = self._map_refinement(
                model=selected_model,
                user_message=user_message,
                dataset_profile=dataset_profile,
                product_kb=product_kb,
                graph_matrix=graph_matrix,
                current_plan=current_plan,
                app_state=app_state,
            )
            if llm_result.draft is not None:
                refined = self.patch_applier.apply_patch(
                    current_plan, VisualPlanPatch.from_llm_draft(llm_result.draft)
                )
                keyword_chart_type = self.deterministic_fallback_patch_planner.extract_chart_type_from_message(user_message)
                if keyword_chart_type and keyword_chart_type != refined.chart_type:
                    refined.chart_type = keyword_chart_type
                    messages.append(
                        f"Chart type overridden to '{keyword_chart_type}' from explicit keyword in refinement request."
                    )
                refined = self._preserve_visual_structure_for_style_only_refinement(
                    current_plan, refined, user_message, llm_result.draft, messages
                )
                refined = self._apply_deterministic_style_patch_if_needed(
                    current_plan, refined, user_message, messages
                )
                refined = self.field_mapper.normalize_roles_for_chart_type(
                    refined, dataset_profile
                )
                if dataset_profile is not None and self._needs_field_completion(refined):
                    completed_refined = self.field_mapper.complete_missing_roles(
                        user_message, dataset_profile, refined
                    )
                    if completed_refined != refined:
                        refined = completed_refined
                        messages.append(
                            "Completed missing LLM role fields with deterministic "
                            "field mapping."
                        )
                refined.metadata.mapping_method = (
                    "llm_with_repair" if llm_result.used_repair else "llm"
                )
                validation = self._validate(
                    refined, dataset_profile, product_kb, graph_matrix
                )
                clarification_requests = (
                    self.clarification_engine.detect_needed_clarification(
                        refined, dataset_profile
                    )
                )
                if validation.is_valid and not clarification_requests:
                    refined.metadata.is_preview_stale = True
                    return RefinementResult(
                        visual_plan=refined,
                        validation_result=validation,
                        mapping_method=refined.metadata.mapping_method or "llm",
                        used_fallback=False,
                        messages=messages,
                    )
                if not clarification_requests:
                    clarification_requests = self._clarification_from_validation(
                        refined, validation, dataset_profile
                    )
                unsupported_visual = any(
                    message.message.startswith("Unsupported chart_type")
                    or message.message.startswith("Unsupported diagram_type")
                    for message in validation.messages
                )
                if unsupported_visual:
                    messages.extend(message.message for message in validation.messages)
                    messages.append(
                        "The suggested visual type is not supported by the graph "
                        "matrix contract."
                    )
                    return RefinementResult(
                        visual_plan=None,
                        validation_result=validation,
                        mapping_method="llm_rejected",
                        used_fallback=False,
                        messages=messages,
                    )
                messages.extend(message.message for message in validation.messages)
                messages.append(
                    "Refined plan requires clarification before it can replace "
                    "the current plan."
                )
                return RefinementResult(
                    visual_plan=None,
                    validation_result=validation,
                    mapping_method=refined.metadata.mapping_method or "llm",
                    clarification_requests=clarification_requests,
                    used_fallback=False,
                    messages=messages,
                )
            messages.extend(llm_result.errors or ["LLM refinement failed."])
            messages.append("The LLM response did not pass the graph matrix contract.")
            messages.append(
                "I used deterministic fallback patch planning where possible."
            )
        else:
            if use_llm and not app_state.llm_mapping_enabled:
                messages.append(
                    "I could not use LLM semantic refinement because it is "
                    "disabled. I used deterministic fallback patch planning "
                    "where possible."
                )
            elif use_llm and not selected_model:
                messages.append(
                    "I could not use LLM semantic refinement because no model "
                    "is selected. I used deterministic fallback patch planning "
                    "where possible."
                )

        if hasattr(self.deterministic_fallback_patch_planner, "build_patch"):
            patch = self.deterministic_fallback_patch_planner.build_patch(
                current_plan, user_message
            )
        elif hasattr(self.deterministic_refinement_engine, "apply_refinement"):
            refined_plan = self.deterministic_refinement_engine.apply_refinement(
                current_plan, user_message
            )
            patch = self._patch_from_plan(current_plan, refined_plan)
        else:
            patch = VisualPlanPatch()
        refined = self.patch_applier.apply_patch(current_plan, patch)
        refined = self.field_mapper.normalize_roles_for_chart_type(
            refined, dataset_profile
        )
        refined.metadata.mapping_method = "deterministic_fallback"
        validation = self._validate(refined, dataset_profile, product_kb, graph_matrix)
        clarification_requests = self.clarification_engine.detect_needed_clarification(
            refined, dataset_profile
        )
        if validation.is_valid and not clarification_requests:
            refined.metadata.is_preview_stale = True
            return RefinementResult(
                visual_plan=refined,
                validation_result=validation,
                mapping_method=refined.metadata.mapping_method
                or "deterministic_fallback",
                used_fallback=True,
                messages=messages,
            )
        if not clarification_requests:
            clarification_requests = self._clarification_from_validation(
                refined, validation, dataset_profile
            )
        messages.extend(message.message for message in validation.messages)
        messages.append(
            "Deterministic refinement requires clarification before it can "
            "replace the current plan."
        )
        return RefinementResult(
            visual_plan=None,
            validation_result=validation,
            mapping_method=refined.metadata.mapping_method or "deterministic_fallback",
            clarification_requests=clarification_requests,
            used_fallback=True,
            messages=messages,
        )

    def _validate(
        self, plan: VisualPlan, dataset_profile, product_kb, graph_matrix
    ) -> ValidationResult:
        validation = self.visual_plan_validator.validate(
            plan, dataset_profile, graph_matrix
        )
        if product_kb is not None:
            capability_result = self.capability_validator.validate_against_capabilities(
                plan, product_kb
            )
            validation.messages.extend(capability_result.messages)
        return validation

    _ROLE_QUESTIONS: dict[tuple[str, str], str] = {
        ("stacked_bar", "stack"): "A stacked bar chart needs a column to split the bars into groups. Which column should be used for grouping?",
        ("stacked_area", "stack"): "A stacked area chart needs a column to split the areas into series. Which column should be used?",
        ("heatmap", "x_category"): "A heatmap needs a column for the horizontal axis. Which column should I use?",
        ("heatmap", "y_category"): "A heatmap needs a column for the vertical axis. Which column should I use?",
        ("scatter", "x"): "A scatter chart needs a numeric column for the X axis. Which column should I use?",
        ("scatter", "y"): "A scatter chart needs a numeric column for the Y axis. Which column should I use?",
        ("bubble", "size"): "A bubble chart needs a column to set the bubble size. Which column should I use?",
        ("line", "x"): "A line chart needs a column for the horizontal axis (time or order). Which column should I use?",
        ("radar", "category"): "A radar chart needs a column for the axis labels. Which column should I use?",
    }

    def _clarification_from_validation(
        self,
        plan: VisualPlan,
        validation: ValidationResult,
        dataset_profile,
    ) -> list[ClarificationRequest]:
        if not validation.messages:
            return []
        raw = validation.messages[0].message
        question = self._humanize_role_question(raw, plan)
        options = self._column_options(dataset_profile)
        return [
            ClarificationRequest(
                question=question,
                reason=raw,
                field_name="category" if plan.visual_kind == "chart" else None,
                options=options,
            )
        ]

    def _humanize_role_question(self, raw_message: str, plan: VisualPlan) -> str:
        import re
        m = re.match(r"(\w+) plans? must include role: (\w+)", raw_message)
        if m:
            chart_type, role = m.group(1), m.group(2)
            key = (chart_type, role)
            if key in self._ROLE_QUESTIONS:
                return self._ROLE_QUESTIONS[key]
            return (
                f"To build a {chart_type.replace('_', ' ')} chart I need to know "
                f"which column to use for {role.replace('_', ' ')}. Which column should I use?"
            )
        return raw_message

    def _column_options(self, dataset_profile) -> list[ClarificationOption]:
        if dataset_profile is None:
            return []
        return [
            ClarificationOption(label=col.name, value=col.name)
            for col in dataset_profile.columns
        ]

    def _patch_from_plan(
        self, base: VisualPlan, updated: VisualPlan
    ) -> VisualPlanPatch:
        style = None
        if updated.style != base.style:
            style = updated.style
        render_target = None
        if updated.render_target != base.render_target:
            render_target = updated.render_target
        notes = updated.notes if updated.notes != base.notes else None
        data_roles = (
            updated.data_roles if updated.data_roles != base.data_roles else None
        )
        filters = updated.filters if updated.filters != base.filters else None
        grouping = updated.grouping if updated.grouping != base.grouping else None
        diagram_nodes = (
            updated.diagram_nodes
            if updated.diagram_nodes != base.diagram_nodes
            else None
        )
        diagram_edges = (
            updated.diagram_edges
            if updated.diagram_edges != base.diagram_edges
            else None
        )
        return VisualPlanPatch(
            visual_kind=updated.visual_kind
            if updated.visual_kind != base.visual_kind
            else None,
            intent=updated.intent if updated.intent != base.intent else None,
            chart_type=updated.chart_type
            if updated.chart_type != base.chart_type
            else None,
            diagram_type=updated.diagram_type
            if updated.diagram_type != base.diagram_type
            else None,
            data_roles=data_roles,
            filters=filters,
            grouping=grouping,
            diagram_nodes=diagram_nodes,
            diagram_edges=diagram_edges,
            style=style,
            render_target=render_target,
            notes=notes,
        )

    def _apply_deterministic_style_patch_if_needed(
        self,
        current_plan: VisualPlan,
        refined: VisualPlan,
        user_message: str,
        messages: list[str],
    ) -> VisualPlan:
        fallback_patch = self.deterministic_fallback_patch_planner.build_patch(
            current_plan, user_message
        )
        if fallback_patch.style is None:
            return refined
        patched = self._merge_missing_style_from_fallback(
            current_plan, refined, fallback_patch
        )
        if patched == refined:
            return refined
        if refined == current_plan:
            messages.append(
                "Applied deterministic style refinement because the LLM "
                "returned no style change."
            )
        else:
            messages.append(
                "Applied deterministic style refinement for style details the "
                "LLM did not preserve."
            )
        return patched

    def _merge_missing_style_from_fallback(
        self,
        current_plan: VisualPlan,
        refined: VisualPlan,
        fallback_patch: VisualPlanPatch,
    ) -> VisualPlan:
        if fallback_patch.style is None:
            return refined

        updated = refined
        style_patch = VisualPlanPatch(style=type(fallback_patch.style)())
        has_changes = False

        if (
            fallback_patch.style.background is not None
            and refined.style.background == current_plan.style.background
        ):
            style_patch.style.background = fallback_patch.style.background
            has_changes = True
        if (
            fallback_patch.style.plot_background is not None
            and refined.style.plot_background == current_plan.style.plot_background
        ):
            style_patch.style.plot_background = fallback_patch.style.plot_background
            has_changes = True
        if (
            fallback_patch.style.colour_scheme is not None
            and refined.style.colour_scheme == current_plan.style.colour_scheme
        ):
            style_patch.style.colour_scheme = fallback_patch.style.colour_scheme
            has_changes = True
        if (
            fallback_patch.style.title_size is not None
            and refined.style.title_size == current_plan.style.title_size
        ):
            style_patch.style.title_size = fallback_patch.style.title_size
            has_changes = True
        if fallback_patch.style.palette:
            merged_palette = dict(refined.style.palette or {})
            for key, value in fallback_patch.style.palette.items():
                if (
                    key not in merged_palette
                    or merged_palette.get(key) == current_plan.style.palette.get(key)
                ):
                    merged_palette[key] = value
                    has_changes = True
            if has_changes:
                style_patch.style.palette = merged_palette

        if has_changes:
            updated = self.patch_applier.apply_patch(updated, style_patch)
        return updated

    def _map_refinement(
        self,
        model: str,
        user_message: str,
        dataset_profile,
        product_kb,
        graph_matrix,
        current_plan: VisualPlan,
        app_state: AppState,
    ) -> LlmMappingResult:
        """Route refinement through multi-turn chat when history is available.

        Falls back to the single-shot generate-based mapper when the mapper
        does not support chat history or there is no conversation history.
        """
        history = self._conversation_history(app_state)
        chat_capable = hasattr(self.llm_mapper, "map_to_draft_with_history")
        if chat_capable and history:
            return self.llm_mapper.map_to_draft_with_history(  # type: ignore[attr-defined]
                model=model,
                user_message=user_message,
                dataset_profile=dataset_profile,
                product_kb=product_kb,
                graph_matrix=graph_matrix,
                current_plan=current_plan,
                conversation_messages=history,
            )
        return self.llm_mapper.map_to_draft(
            model=model,
            user_message=user_message,
            dataset_profile=dataset_profile,
            product_kb=product_kb,
            graph_matrix=graph_matrix,
            current_plan_summary=summarize_visual_plan(current_plan),
            current_plan=current_plan,
        )

    def _conversation_history(self, app_state: AppState) -> list[dict[str, str]]:
        """Return prior conversation turns (excluding the current message)."""
        conversation = getattr(app_state, "conversation_state", None)
        if conversation is None:
            return []
        messages = getattr(conversation, "messages", None)
        if not messages:
            return []
        history: list[dict[str, str]] = []
        for turn in messages[:-1]:
            role = getattr(turn, "role", None)
            content = getattr(turn, "content", "")
            if role in {"user", "assistant"} and content:
                history.append({"role": role, "content": str(content)})
        return history

    def _preserve_visual_structure_for_style_only_refinement(
        self,
        current_plan: VisualPlan,
        refined: VisualPlan,
        user_message: str,
        llm_draft,
        messages: list[str],
    ) -> VisualPlan:
        fallback_patch = self.deterministic_fallback_patch_planner.build_patch(
            current_plan, user_message
        )
        if fallback_patch.chart_type is not None:
            return refined
        if llm_draft.chart_type is None:
            return refined
        if refined.chart_type == current_plan.chart_type:
            return refined
        style_requested = self._looks_like_style_only_request(user_message, fallback_patch)
        if not style_requested:
            return refined

        patched = self.patch_applier.apply_patch(
            refined,
            VisualPlanPatch(
                chart_type=current_plan.chart_type,
                diagram_type=current_plan.diagram_type,
            ),
        )
        if patched != refined:
            messages.append(
                "Preserved the existing chart type because the refinement request "
                "only asked for style changes."
            )
        return patched

    def _looks_like_style_only_request(
        self,
        user_message: str,
        fallback_patch: VisualPlanPatch,
    ) -> bool:
        if fallback_patch.style is not None and any(
            (
                fallback_patch.style.background is not None,
                fallback_patch.style.plot_background is not None,
                fallback_patch.style.colour_scheme is not None,
                fallback_patch.style.title is not None,
                fallback_patch.style.title_size is not None,
                bool(fallback_patch.style.palette),
                fallback_patch.style.font_family is not None,
                fallback_patch.style.grid is not None,
                fallback_patch.style.legend_position is not None,
                bool(fallback_patch.style.highlights),
                bool(fallback_patch.style.labels),
            )
        ):
            return True

        lowered = user_message.lower()
        style_keywords = (
            "colour",
            "color",
            "background",
            "font",
            "title",
            "subtitle",
            "grid",
            "legend",
            "label",
            "labels",
            "size",
            "bigger",
            "smaller",
            "darker",
            "lighter",
            "highlight",
        )
        structure_keywords = (
            "bar",
            "pie",
            "line",
            "area",
            "scatter",
            "bubble",
            "treemap",
            "waterfall",
            "funnel",
            "radar",
            "gauge",
            "kpi",
            "donut",
            "diagram",
            "flowchart",
            "sequence",
            "network",
            "timeline",
            "swimlane",
            "chart type",
            "graph type",
        )
        has_style_keyword = any(keyword in lowered for keyword in style_keywords)
        has_structure_keyword = any(keyword in lowered for keyword in structure_keywords)
        return has_style_keyword and not has_structure_keyword

    def _needs_field_completion(self, plan: VisualPlan) -> bool:
        return not plan.data_roles or any(role.field is None for role in plan.data_roles) or (
            plan.visual_kind == "chart"
            and plan.chart_type is not None
            and any(
                get_role(plan, required_role) is None
                or get_role(plan, required_role).field is None
                for required_role in {
                    "category",
                    "measure",
                    "x",
                    "y",
                    "time_or_order",
                    "value",
                    "x_category",
                    "y_category",
                    "series",
                    "stack",
                }
                if get_role(plan, required_role) is not None
            )
        )

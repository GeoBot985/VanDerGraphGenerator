"""Recipe panel helpers."""

from __future__ import annotations

from semantic_visual_builder.state.app_state import AppState


class RecipePanel:
    """Summarize active recipe state for the UI."""

    def active_recipe_text(self, app_state: AppState) -> str:
        name = app_state.active_recipe_name or "No active recipe"
        path = (
            str(app_state.active_recipe_path)
            if app_state.active_recipe_path
            else "No active recipe path"
        )
        lines = [f"Active recipe: {name}", f"Path: {path}"]
        report = app_state.recipe_compatibility_report
        if report is not None:
            lines.append(f"Compatibility score: {report.overall_score:.0%}")
            lines.append(f"Can apply: {'yes' if report.can_apply else 'no'}")
        application = app_state.recipe_application_result
        if application is not None:
            lines.append(
                f"Application status: {'success' if application.success else 'failed'}"
            )
        recipe = app_state.active_recipe
        if recipe is not None:
            default_id = recipe.metadata.default_style_profile_id
            if default_id:
                default_name = recipe.metadata.default_style_profile_name or default_id
                lines.append(f"Default style: {default_name} ({default_id})")
            else:
                lines.append("Default style: none")
        return "\n".join(lines)

    def compatibility_text(self, app_state: AppState) -> str:
        report = app_state.recipe_compatibility_report
        if report is not None:
            lines = [
                "Compatibility report:",
                f"Overall score: {report.overall_score:.0%}",
                f"Can apply: {'yes' if report.can_apply else 'no'}",
            ]
            for match in report.field_matches:
                lines.append(
                    f"- {match.expected_field} -> {match.matched_field or 'unmatched'} "
                    f"({match.score:.2f}, {match.match_reason})"
                )
            if report.warnings:
                lines.append("Warnings:")
                lines.extend(f"- {warning}" for warning in report.warnings)
            if report.errors:
                lines.append("Errors:")
                lines.extend(f"- {error}" for error in report.errors)
            return "\n".join(lines)

        result = app_state.recipe_compatibility_result
        if result is None:
            return "Compatibility: not checked"
        if not result.messages:
            return "Compatibility: valid"
        lines = ["Compatibility report:"]
        for message in result.messages:
            lines.append(f"- {message.severity.value.upper()}: {message.message}")
        return "\n".join(lines)

    def available_recipes_text(self, app_state: AppState) -> str:
        if not app_state.available_recipes:
            return "Available recipes: none"
        lines = ["Available recipes:"]
        for recipe in app_state.available_recipes:
            default_id = recipe.metadata.default_style_profile_id
            suffix = f" [default style: {default_id}]" if default_id else ""
            lines.append(f"- {recipe.recipe_name}{suffix}")
        return "\n".join(lines)

    def default_style_offer_text(self, app_state: AppState) -> str:
        """Return offer text when a recipe has a default style after application."""
        result = app_state.recipe_application_result
        if result is None or not result.default_style_profile_id:
            return ""
        name = result.default_style_profile_name or result.default_style_profile_id
        return (
            f"This recipe has a default style: {name}.\n"
            "Apply it now? (Set Active Style as Recipe Default)"
        )

"""Summarize visual recipes."""

from __future__ import annotations

from .recipe_schema import VisualRecipe


def summarize_recipe(recipe: VisualRecipe) -> str:
    lines = [f"Recipe: {recipe.recipe_name}"]
    if recipe.description:
        lines.append(f"Description: {recipe.description}")
    if recipe.renderer is not None:
        lines.append(f"Renderer: {recipe.renderer.renderer}")
    lines.append("Expected fields:")
    for expected in recipe.expected_fields:
        semantic = expected.semantic_type or "any"
        requirement = "required" if expected.required else "optional"
        lines.append(
            f"- {expected.role}: {expected.field_name} ({semantic}, {requirement})"
        )
    lines.append("Style:")
    if recipe.style.title:
        lines.append(f"- Title: {recipe.style.title}")
    if recipe.style.colour_scheme:
        lines.append(f"- Colour scheme: {recipe.style.colour_scheme}")
    if recipe.style.orientation:
        lines.append(f"- Orientation: {recipe.style.orientation}")
    return "\n".join(lines)

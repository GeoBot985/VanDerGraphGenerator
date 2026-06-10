"""Import smoke tests."""


def test_package_imports() -> None:
    import semantic_visual_builder
    import semantic_visual_builder.app
    import semantic_visual_builder.knowledge
    import semantic_visual_builder.llm
    import semantic_visual_builder.planning
    import semantic_visual_builder.renderers
    import semantic_visual_builder.validation

    assert semantic_visual_builder.__version__ == "0.0.0"

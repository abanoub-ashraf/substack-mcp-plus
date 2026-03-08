from src.handlers.strategy_handler import StrategyHandler


def test_analyze_post_collection_filters_url_and_embed_noise():
    handler = StrategyHandler()

    posts = [
        {
            "title": "SwiftUI async image loading",
            "content": (
                "Here is the real lesson about AsyncImage caching. "
                "https://cdn.example.com/embed/post and com embed post should not dominate. "
                "SwiftUI image caching matters for scrolling performance."
            ),
        }
    ]

    result = handler.analyze_post_collection(posts)
    theme_names = {item["theme"] for item in result["themes"]}

    assert "swiftui" in theme_names
    assert "https" not in theme_names
    assert "com" not in theme_names
    assert "embed" not in theme_names
    assert "post" not in theme_names
    assert "button" not in theme_names
    assert "editor" not in theme_names
    assert "published" not in theme_names


def test_study_topic_on_substack_surfaces_empty_result_warning():
    handler = StrategyHandler()

    result = handler.study_topic_on_substack(
        "AI for work",
        {
            "themes": [],
            "recommended_to_study": [],
            "warnings": ["No credible public Substack results were found for this query from the available discovery providers."],
        },
    )

    assert result["study_order"] == []
    assert result["warnings"]
    assert "No strong Substack sources" in result["warnings"][-1]

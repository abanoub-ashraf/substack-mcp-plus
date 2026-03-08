import pytest

from src.handlers.research_handler import ResearchHandler


def test_is_researchable_substack_url_filters_internal_paths():
    handler = ResearchHandler()

    assert handler._is_researchable_substack_url("https://example.substack.com/p/post")
    assert handler._is_researchable_substack_url("https://www.oneusefulthing.org/p/change-blindness")
    assert handler._is_researchable_substack_url("https://www.oneusefulthing.org")
    assert not handler._is_researchable_substack_url("https://substack.com/sign-in")
    assert not handler._is_researchable_substack_url("https://substack.com/api/v1/search")
    assert not handler._is_researchable_substack_url("https://substack.com/publish/post/123")


def test_extract_themes_surfaces_repeated_topic_words():
    handler = ResearchHandler()
    results = [
        {
            "title": "AI agents for product teams",
            "snippet": "How teams use AI agents in workflow systems",
            "description": "",
            "body_excerpt": "",
        },
        {
            "title": "AI workflow design on Substack",
            "snippet": "Workflow ideas for AI research and writing",
            "description": "",
            "body_excerpt": "",
        },
    ]

    themes = handler._extract_themes(results)
    theme_names = {item["theme"] for item in themes}

    assert "ai" in theme_names
    assert "workflow" in theme_names


def test_extract_themes_filters_web_noise_tokens():
    handler = ResearchHandler()
    results = [
        {
            "title": "SwiftUI async image caching",
            "snippet": "https://example.com embed com post swiftui asyncimage caching",
            "description": "",
            "body_excerpt": "",
        }
    ]

    themes = handler._extract_themes(results)
    theme_names = {item["theme"] for item in themes}

    assert "swiftui" in theme_names
    assert "https" not in theme_names
    assert "com" not in theme_names
    assert "embed" not in theme_names
    assert "post" not in theme_names


def test_looks_like_junk_result_rejects_enable_javascript_pages():
    handler = ResearchHandler()

    assert handler._looks_like_junk_result(
        "https://enable-javascript.com/",
        "turn on JavaScript | enable-javascript.com",
        "This site requires javascript to run correctly.",
    )


def test_build_recommendations_prefers_richer_post_results():
    handler = ResearchHandler()
    results = [
        {
            "title": "Thin result",
            "url": "https://alpha.substack.com/",
            "publication": "alpha",
            "page_type": "publication",
            "provider": "duckduckgo_html",
        },
        {
            "title": "Rich post",
            "url": "https://beta.substack.com/p/rich-post",
            "publication": "beta",
            "page_type": "post",
            "provider": "substack_direct",
            "description": "Deep write-up",
            "body_excerpt": "A substantial excerpt about the niche.",
            "author": "Beta Author",
        },
    ]

    recommendations = handler._build_recommendations(results)

    assert recommendations[0]["publication"] == "beta"
    assert recommendations[0]["score"] > recommendations[1]["score"]


def test_normalize_candidate_url_unwraps_duckduckgo_redirect():
    handler = ResearchHandler()

    url = "https://duckduckgo.com/l/?uddg=https%3A%2F%2Fwww.oneusefulthing.org%2Fp%2Fchange-blindness"

    assert (
        handler._normalize_candidate_url(url)
        == "https://www.oneusefulthing.org/p/change-blindness"
    )


@pytest.mark.asyncio
async def test_duckduckgo_search_gracefully_falls_back_after_202():
    handler = ResearchHandler()

    class FakeResponse:
        def __init__(self, status, body):
            self.status = status
            self._body = body

        async def text(self):
            return self._body

        async def __aenter__(self):
            return self

        async def __aexit__(self, exc_type, exc, tb):
            return False

    class FakeSession:
        def __init__(self):
            self.calls = 0

        def get(self, url):
            self.calls += 1
            if self.calls == 1:
                return FakeResponse(202, "")
            return FakeResponse(
                200,
                """
                <div class="result">
                  <div class="result__title">
                    <a href="https://www.oneusefulthing.org/p/change-blindness">Change Blindness</a>
                  </div>
                  <div class="result__snippet">A Substack post on AI and perception.</div>
                </div>
                """,
            )

    results = await handler._duckduckgo_search(FakeSession(), "ai", 5)

    assert len(results) == 1
    assert results[0]["url"] == "https://www.oneusefulthing.org/p/change-blindness"
    assert results[0]["provider"] == "duckduckgo_html_alt"


@pytest.mark.asyncio
async def test_search_falls_back_to_bing_when_duckduckgo_is_empty(monkeypatch):
    handler = ResearchHandler()

    async def fake_direct(session, query, max_results):
        return []

    async def fake_duckduckgo(session, query, max_results):
        return []

    async def fake_bing(session, query, max_results):
        return [
            {
                "title": "SwiftUI Notes",
                "url": "https://builder.substack.com/p/swiftui-notes",
                "publication": "builder",
                "snippet": "Thoughts on SwiftUI performance.",
                "provider": "bing_html",
                "page_type": "post",
            }
        ]

    monkeypatch.setattr(handler, "_direct_substack_search", fake_direct)
    monkeypatch.setattr(handler, "_duckduckgo_search", fake_duckduckgo)
    monkeypatch.setattr(handler, "_bing_search", fake_bing)

    results = await handler._search(object(), "swiftui", 5)

    assert len(results) == 1
    assert results[0]["provider"] == "bing_html"


def test_result_is_not_credible_for_custom_domain_without_enrichment():
    handler = ResearchHandler()

    result = {
        "title": "turn on JavaScript | enable-javascript.com",
        "url": "https://enable-javascript.com/",
        "snippet": "This site requires JavaScript to run correctly.",
    }

    assert handler._result_is_credible(result, {}) is False


@pytest.mark.asyncio
async def test_inspect_url_accepts_custom_domain_post(monkeypatch):
    handler = ResearchHandler()

    class DummySession:
        async def __aenter__(self):
            return self

        async def __aexit__(self, exc_type, exc, tb):
            return False

    async def fake_fetch_page_details(session, url):
        return {
            "resolved_url": url,
            "resolved_title": "Change Blindness",
            "description": "AI, cognition, and perception.",
            "author": "Ethan Mollick",
            "published_at": "2026-01-01T00:00:00Z",
            "body_excerpt": "Why smart people miss obvious changes.",
            "page_type": "post",
            "publication": "oneusefulthing.org",
        }

    monkeypatch.setattr("src.handlers.research_handler.aiohttp.ClientSession", lambda **kwargs: DummySession())
    monkeypatch.setattr(handler, "_fetch_page_details", fake_fetch_page_details)

    result = await handler.inspect_url("https://www.oneusefulthing.org/p/change-blindness")

    assert result["url"] == "https://www.oneusefulthing.org/p/change-blindness"
    assert result["publication"] == "oneusefulthing.org"


def test_page_looks_like_substack_from_footer_markers():
    handler = ResearchHandler()
    html = """
    <html>
      <body>
        <div>Ready for more?</div>
        <a href="https://substack.com/privacy">Privacy</a>
        <a href="https://substack.com/terms">Terms</a>
        <div>Start your Substack</div>
        <div>This site requires JavaScript to run correctly.</div>
      </body>
    </html>
    """

    from bs4 import BeautifulSoup

    soup = BeautifulSoup(html, "html.parser")
    assert (
        handler._page_looks_like_substack(
            soup,
            "https://www.oneusefulthing.org/p/change-blindness",
            "https://www.oneusefulthing.org/p/change-blindness",
        )
        is True
    )


def test_research_warnings_are_present_when_empty():
    handler = ResearchHandler()

    warnings = handler._research_warnings([])

    assert warnings
    assert "No credible public Substack results" in warnings[0]

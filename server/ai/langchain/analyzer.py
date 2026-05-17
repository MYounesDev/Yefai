import logging
from dataclasses import dataclass
from typing import Any

from services.vector_search_service import VectorSearchService

logger = logging.getLogger(__name__)

try:
    import openai  # type: ignore[import-untyped]

    HAS_OPENAI = True
except ImportError:
    HAS_OPENAI = False


@dataclass
class LLMConfig:
    provider: str = "openai"
    model: str = "gpt-4o"
    temperature: float = 0.1
    max_tokens: int = 1024
    api_key: str = ""
    base_url: str | None = None


class RAGAnalyzer:
    def __init__(self, config: LLMConfig | None = None):
        self._config = config or LLMConfig()
        self._vector = VectorSearchService()

    def analyze_anomaly(
        self,
        query_embedding: list[float],
        image_name: str,
        anomaly_score: float,
        wear_type: str,
        wear_value_um: float,
        top_k: int = 5,
        language: str = "tr",
        prediction: dict | None = None,
    ) -> dict[str, Any]:
        similar = self._vector.search_similar(
            query_embedding=query_embedding,
            exclude_image_name=image_name,
            top_k=top_k,
            min_similarity=0.3,
        )

        cases = []
        for r in similar.results:
            cases.append(
                {
                    "rank": r.rank,
                    "image_name": r.image_name,
                    "similarity": r.similarity,
                    "wear_type": r.wear_type,
                    "wear": r.wear,
                    "set_name": r.set_name,
                }
            )

        from ai.langchain.prompts import build_analysis_context

        ctx = build_analysis_context(
            image_name=image_name,
            anomaly_score=anomaly_score,
            wear_type=wear_type,
            wear_value_um=wear_value_um,
            similar_cases=cases,
            language=language,
            prediction=prediction,
        )

        llm_response = self._call_llm(ctx["system"], ctx["prompt"])

        return {
            "image_name": image_name,
            "anomaly_score": anomaly_score,
            "wear_type": wear_type,
            "similar_cases": cases,
            "llm_analysis": llm_response,
            "prompt_used": ctx,
        }

    def chat(
        self,
        question: str,
        query_embedding: list[float],
        top_k: int = 5,
        language: str = "tr",
    ) -> dict[str, Any]:
        similar = self._vector.search_similar(
            query_embedding=query_embedding,
            top_k=top_k,
            min_similarity=0.1,
        )

        cases = []
        for r in similar.results:
            cases.append(
                {
                    "rank": r.rank,
                    "image_name": r.image_name,
                    "similarity": r.similarity,
                    "wear_type": r.wear_type,
                    "wear": r.wear,
                    "set_name": r.set_name,
                }
            )

        from ai.langchain.prompts import build_rag_context

        ctx = build_rag_context(
            question=question,
            similar_cases=cases,
            top_k=top_k,
            language=language,
        )

        llm_response = self._call_llm(ctx["system"], ctx["prompt"])

        return {
            "question": question,
            "similar_cases": cases,
            "response": llm_response,
        }

    def _call_llm(self, system_prompt: str, user_prompt: str) -> str:
        if not self._config.api_key:
            return "[LLM_API_KEY tanımlı değil. G4 gate'ini tamamla: .env → LLM_API_KEY ekle.]"

        if HAS_OPENAI and self._config.provider == "openai":
            return self._call_openai(system_prompt, user_prompt)

        return (
            f"[LLM provider '{self._config.provider}' desteklenmiyor. openai yüklü: {HAS_OPENAI}]"
        )

    def _call_openai(self, system_prompt: str, user_prompt: str) -> str:
        client = openai.OpenAI(
            api_key=self._config.api_key,
            base_url=self._config.base_url,
        )
        resp = client.chat.completions.create(
            model=self._config.model,
            temperature=self._config.temperature,
            max_tokens=self._config.max_tokens,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
        )
        return resp.choices[0].message.content or ""


def create_analyzer_from_env() -> RAGAnalyzer:
    from db.config import get_settings

    settings = get_settings()
    api_key = getattr(settings, "llm_api_key", "") or ""
    provider = getattr(settings, "llm_provider", "openai") or "openai"
    model = getattr(settings, "llm_model", "gpt-4o") or "gpt-4o"

    return RAGAnalyzer(
        config=LLMConfig(
            provider=provider,
            model=model,
            api_key=api_key,
        )
    )

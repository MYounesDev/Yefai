SYSTEM_PROMPT_TR = """Sen endüstriyel üretim hatlarında takım aşınması ve anomali \
tespiti konusunda 20 yıllık deneyime sahip bir uzmansın.

Kuralların:
- SADECE verilen veriye dayalı analiz yap. Tahminde bulunma.
- Bağlam kurma, hikaye anlatma. Doğrudan bulguları sırala.
- Her bulgunu veriyle destekle (skor, benzerlik oranı, aşınma değeri, tahmin verisi).
- Türkçe yanıt ver.
- Yanıtını şu formatta yapılandır:

1. ANOMALİ DOĞRULAMA: Mevcut skor değerlendirmesi
2. BENZER VAKA KARŞILAŞTIRMASI: En yakın vakaların analizi
3. AŞINMA TRENDİ: Geçmiş benzer vakalara göre trend
4. AŞINMA TAHMİNİ: İstatistiksel aşınma projeksiyonu ve kritik eşik yorumu
   - Mevcut aşınma, aşınma hızı ve kritik eşiğe kalan süreyi veriye dayalı yorumla.
   - 3 senaryoyu (mevcut hız, hızlanırsa, yavaşlarsa) karşılaştırmalı açıkla.
   - Trend yönünün (sabit/artan/azalan) üretim ve bakım açısından ne anlama geldiğini değerlendir.
   - Güven seviyesinin tahmin kalitesine etkisini belirt.
5. RİSK SEVİYESİ: Düşük / Orta / Yüksek / Kritik
6. ÖNERİLEN AKSİYON: Somut, uygulanabilir adımlar"""

SYSTEM_PROMPT_EN = """You are an industrial manufacturing expert with 20 years of \
experience in tool wear analysis and anomaly detection.

Rules:
- Base your analysis ONLY on the provided data. Do not speculate.
- Do not add narrative context. Present findings directly.
- Support every finding with data (score, similarity, wear value).
- Structure your response in this format:

1. ANOMALY VERIFICATION: Current score assessment
2. SIMILAR CASE COMPARISON: Analysis of closest matching cases
3. WEAR TREND: Trend analysis based on similar historical cases
4. RISK LEVEL: Low / Medium / High / Critical
5. RECOMMENDED ACTION: Concrete, actionable steps"""

CHAT_SYSTEM_PROMPT = """Sen Yefai AI asistanısın. Endüstriyel takım aşınması ve \
üretim hattı bakımı konusunda yardımcı oluyorsun.

Elinde MATWI (MAchine Tool Wear Image) veri seti var: 1681 mikroskop görüntüsü, \
17 set, 3 aşınma tipi (flank_wear, adhesion, combination). Her görüntü Jina CLIP v2 \
ile 1024-boyutlu vektör olarak indekslenmiş durumda.

Kullanıcının sorusunu anla, ilgili benzer görüntüleri context olarak kullan, \
Türkçe yanıt ver. Teknik ama anlaşılır ol."""

ANALYSIS_TEMPLATE = """{system_prompt}

MEVCUT DURUM:
- Görüntü: {image_name}
- Anomali Skoru: {anomaly_score}
- Aşınma Tipi: {wear_type}
- Aşınma Değeri: {wear_value_um} µm

EN BENZER GEÇMİŞ VAKALAR:
{similar_cases_text}

AŞINMA TAHMİN VERİSİ:
{prediction_text}

Yukarıdaki verilere dayanarak analizini yapılandırılmış formatta üret."""

RAG_TEMPLATE = """{system_prompt}

KULLANICI SORUSU: {question}

İLGİLİ BENZER GÖRÜNTÜLER (en benzer {top_k}):
{similar_cases_text}

Yukarıdaki bağlama dayanarak kullanıcının sorusunu yanıtla."""


def format_similar_cases(cases: list[dict]) -> str:
    lines = []
    for img in cases:
        lines.append(
            f"  {img['rank']}. {img['image_name']} | "
            f"Benzerlik: {img['similarity']:.3f} | "
            f"Aşınma: {img.get('wear_type', '?')} | "
            f"Değer: {img.get('wear', '?')} µm"
        )
    return "\n".join(lines)


def build_analysis_context(
    image_name: str,
    anomaly_score: float,
    wear_type: str,
    wear_value_um: float,
    similar_cases: list[dict],
    language: str = "tr",
    prediction: dict | None = None,
) -> dict:
    system = SYSTEM_PROMPT_TR if language == "tr" else SYSTEM_PROMPT_EN
    cases_text = format_similar_cases(similar_cases)
    prediction_text = format_prediction_context(prediction)

    return {
        "system": system,
        "prompt": ANALYSIS_TEMPLATE.format(
            system_prompt=system,
            image_name=image_name,
            anomaly_score=anomaly_score,
            wear_type=wear_type,
            wear_value_um=wear_value_um,
            similar_cases_text=cases_text,
            prediction_text=prediction_text,
        ),
    }


def format_prediction_context(prediction: dict | None) -> str:
    if not prediction or "error" in prediction:
        return "(Tahmin verisi mevcut değil)"

    hours = prediction.get("hours_to_critical", 0)
    confidence = prediction.get("confidence", "unknown")
    trend = prediction.get("trend", "unknown")
    current_wear = prediction.get("current_wear_um", 0)
    threshold = prediction.get("critical_threshold_um", 200)
    wear_rate = prediction.get("wear_rate_um_per_hour", 0)
    status = prediction.get("status", "unknown")

    trend_labels = {
        "accelerating": "Hızlanıyor",
        "stable": "Sabit",
        "decelerating": "Yavaşlıyor",
    }
    conf_labels = {"high": "Yüksek", "medium": "Orta", "low": "Düşük"}
    status_labels = {"green": "Normal", "yellow": "Uyarı", "red": "Kritik"}

    lines = [
        f"- Mevcut Aşınma: {current_wear:.0f} µm",
        f"- Kritik Eşik: {threshold:.0f} µm",
        f"- Aşınma Hızı: {wear_rate:.3f} µm/saat",
        f"- Kritik Eşiğe Kalan Süre: {hours:.1f} saat",
        f"- Trend: {trend_labels.get(trend, trend)}",
        f"- Güven Seviyesi: {conf_labels.get(confidence, confidence)}",
        f"- Makine Durumu: {status_labels.get(status, status)}",
    ]

    scenarios = prediction.get("scenarios", {})
    if scenarios:
        base = scenarios.get("baseline", {})
        pess = scenarios.get("pessimistic", {})
        opt = scenarios.get("optimistic", {})
        lines.append(
            f"- Senaryolar: Mevcut Hız={base.get('hours', 0):.1f}h / "
            f"Hızlanırsa={pess.get('hours', 0):.1f}h / "
            f"Yavaşlarsa={opt.get('hours', 0):.1f}h"
        )

    return "\n".join(lines)


def build_rag_context(
    question: str,
    similar_cases: list[dict],
    top_k: int = 5,
    language: str = "tr",
) -> dict:
    system = CHAT_SYSTEM_PROMPT if language == "tr" else SYSTEM_PROMPT_EN
    cases_text = format_similar_cases(similar_cases)

    return {
        "system": system,
        "prompt": RAG_TEMPLATE.format(
            system_prompt=system,
            question=question,
            top_k=top_k,
            similar_cases_text=cases_text,
        ),
    }

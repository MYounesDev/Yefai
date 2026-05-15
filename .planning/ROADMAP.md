# Roadmap — Yefai Predictive Maintenance Platform

> Yüksek seviye faz yapısı. Her faz bağımsız olarak planlanır (`/gsd-plan-phase N`).
> Fazlar bağımlılık sırasına göre numaralandırılmıştır.

---

## Milestone: Yefai v1.0 — Demo MVP

**Hedef:** MATWI veri seti üzerinde gerçek zamanlı anomali tespiti yapan, RAG chatbot'lu,
çok kanallı bildirim gönderen Tauri masaüstü uygulaması. Hackathon/demo sunumuna hazır.

**Zaman hedefi:** 6-8 hafta (part-time)
**Granularity:** Coarse (5 faz)

---

## Phase 1: Veri Altyapısı & PostgreSQL

**Amaç:** MATWI veri setini işle, parse et, PostgreSQL + pgvector'e yükle.

**Kapsam:**
- 17 zip dosyasını ayıkla, labels.csv ve sets.csv'den metadata çıkar
- Sensör CSV'lerini parse et (Accelerometer, Acoustic, Force X/Y/Z)
- Train/test split (%80/%20) — set bazında, aynı set bölünmez
- PostgreSQL şeması: `sets`, `images`, `sensors`, `anomalies`, `embeddings`
- pgvector eklentisi kurulumu ve embedding sütunu
- Görüntü-sensör timestamp eşleştirme (sync hatalarını logla)
- Veri kalite raporu (kaç eşleşen çift, kaç eksik)

**Bağımlılıklar:** Yok
**Deliverable:** Dolu PostgreSQL veritabanı, veri kalite raporu
**Tahmini süre:** 1-1.5 hafta

---

## Phase 2: AI Inference Pipeline

**Amaç:** TimesFM 2.5 ve Anomalib modellerini entegre et, inference pipeline kur.

**Kapsam:**
- TimesFM 2.5 model yükleme (HuggingFace'ten)
- Context window: son 50 sensör adımı → next-step tahmini
- Tahmin vs gerçek → anomali skoru hesaplama
- Anomalib (PatchCore) model yükleme ve görüntü anomali tespiti
- CLIP/SigLIP ile multimodal embedding üretimi
- Toplu embedding: 1663 görüntü → pgvector
- Birleşik anomali skoru (füzyon: sensör + görüntü)
- Inference endpoint'leri (FastAPI)

**Bağımlılıklar:** Phase 1 (veri gerekli)
**Deliverable:** Çalışan inference API, embedding'ler pgvector'de
**Tahmini süre:** 1.5-2 hafta

---

## Phase 3: RAG Chatbot

**Amaç:** Veri seti üzerinde doğal dil sorgulama yapabilen, görsel ve tablo yanıtları verebilen chatbot.

**Kapsam:**
- RAG pipeline: soru → embedding → pgvector similarity → context → LLM
- LLM entegrasyonu (Gemini Flash / Claude sonnet)
- Prompt template: sistem prompt'u + context + soru
- Görsel yanıt: ilgili görüntüleri base64 ile LLM'e context olarak ver
- Tıklanabilir görsel: yanıttaki görsele tıkla → büyük modal
- Tablo yanıtı: sayısal veriler sortable tablo formatında
- Chat UI komponenti (streaming yanıt, mesaj geçmişi)
- Örnek sorular: "Set 3'teki en yüksek aşınma?", "Flank wear olan ürünleri göster"

**Bağımlılıklar:** Phase 1 (pgvector), Phase 2 (embedding'ler)
**Deliverable:** Chatbot UI + RAG pipeline, 10 örnek soru ile test
**Tahmini süre:** 2 hafta

---

## Phase 4: Gerçek Zamanlı Dashboard & Anomali Yönetimi

**Amaç:** Test verisini simüle gerçek zamanlı akış olarak göster, anomali tespitinde uyarı.

**Kapsam:**
- WebSocket sunucusu: test verisini 1 sn aralıklarla stream et
- Canlı dashboard: sensör grafikleri (LineChart), görüntü akışı
- Anomali tespit anında kırmızı vurgu + detay paneli
- Anomali detayları: seri numarası, takım ID, aşınma tipi, zaman, skor
- Streaming agent: anomali → log → bildirim → öneri otomatik zinciri
- Geçmiş anomali listesi (filtreleme, sıralama)
- Dashboard tema: koyu (dark) endüstriyel UI

**Bağımlılıklar:** Phase 2 (inference), Phase 3 (opsiyonel - chatbot ayrı çalışır)
**Deliverable:** Canlı dashboard, anomali tespit ve gösterim
**Tahmini süre:** 1.5-2 hafta

---

## Phase 5: Tauri Desktop + PUQ AI Entegrasyonu

**Amaç:** Her şeyi Tauri masaüstü uygulamasında birleştir, PUQ AI ile bildirim/otomasyon sistemini kur.

**Kapsam:**
- Tauri v2 projesi kurulumu, Next.js frontend'i WebView'de göm
- Next.js → `output: "export"` (static export)
- Tauri Rust komutları: dosya seçici, sistem bildirimi, yerel port başlatma
- FastAPI sunucusunu Tauri sidecar olarak başlat/durdur
- Sistem tepsisi (system tray) entegrasyonu
- **PUQ AI webhook client:** FastAPI'den anomali tespitinde webhook tetikleme
- **PUQ AI Telegram workflow'u:** anomali mesajı (seri no, görüntü, skor, zaman)
- **PUQ AI E-posta workflow'u:** detaylı anomali raporu + görüntü eki
- **PUQ AI SMS workflow'u:** kritik anomali → kısa mesaj
- **PUQ AI raporlama workflow'u:** günlük/haftalık özet (schedule tetiklemeli)
- Webhook retry + log mekanizması (PG'ye logla)
- OS native notification fallback (PUQ AI offline ise)
- macOS packaging: `.dmg` oluşturma

**Bağımlılıklar:** Phase 4 (dashboard), PUQ AI hesabı + API token
**Deliverable:** Çalışan `.dmg`, PUQ AI üzerinden en az 3 kanal bildirim aktif
**Tahmini süre:** 2 hafta

---

## Phase Order & Dependencies

```
Phase 1 ──────► Phase 2 ──────► Phase 4 ──────► Phase 5
(Veri)          (AI)            (Dashboard)      (Tauri+Bildirim)
                    │
                    └──► Phase 3 (RAG Chatbot) ──► Phase 5
```

- Phase 1 ve 2 sıralı (veri olmadan AI çalışmaz)
- Phase 3, Phase 2 tamamlanınca paralel başlayabilir (farklı developer varsa)
- Phase 4, Phase 2'ye bağımlı
- Phase 5 her şeyi birleştirir

---

## Teknik Borç & Sonraki Versiyonlar (v1.1+)

| Konu | Açıklama |
|------|----------|
| Model fine-tuning | Kendi veri setimizle TimesFM fine-tune |
| Gerçek kamera entegrasyonu | IP kamera / RTSP stream |
| Multi-instance | Aynı anda birden fazla makine izleme |
| Windows/Linux build | Cross-platform Tauri build |
| NovaVision CV pipeline | Görüntü işleme pipeline'ı alternatifi (no-code CV) |
| Kullanıcı yönetimi | Rol tabanlı erişim (operatör, yönetici, admin) |
| Anomali geçmişi analitiği | Trend grafikleri, raporlama |
| Edge deployment | NVIDIA Jetson / Raspberry Pi'de çalıştırma |

---

## Nasıl Başlanır?

```bash
# Phase 1'i başlat:
/gsd-plan-phase 1

# Veya direkt:
/gsd-phase --number 1 --name "Veri Altyapısı & PostgreSQL"
```

---

*Last updated: 2026-05-15 — GSD initialization*

# Scope & Phase Gates

## Kesinlikle yapılacaklar
- v1.0'ı AI Backend kapsamı olarak ele al: FastAPI, Supabase, AI pipeline, RAG API, PUQ AI webhook ve yedek parça krizi simülasyonu.
- Frontend/Desktop işleri ancak ilgili sonraki aşama veya açık faz kapsamında istenirse ele al.
- Faz başlamadan önce ilgili manual gate'i kontrol et:
  - G1: Supabase projesi, pgvector ve `.env` bağlantıları Phase 1 öncesi hazır olmalı.
  - G2: Docker Desktop, NovaVision CLI/token ve local install Phase 2B öncesi hazır olmalı.
  - G3: PUQ AI hesabı, workflow webhook URL'leri ve test mesajları Phase 3B öncesi hazır olmalı.
  - G4: LLM provider/API key Phase 3A öncesi hazır olmalı.
- Gate tamamlanmamışsa faz execution başlatma; mock/skeleton/testable contract üretilebilen alanlarda açıkça mock mode ile ilerle.
- Faz bağımlılıklarına uy:
  - Phase 1 tamamlanmadan Phase 2A/2B gerçek veri entegrasyonuna geçme.
  - Phase 2A skor/embedding çıktıları olmadan Phase 3A RAG ve Phase 2.5 tahmin gerçek sonuç iddiası yapma.
  - Phase 2B inference altyapısı ve G3 hazır olmadan Phase 3B live bildirim iddiası yapma.
  - Phase 4 sadece Phase 3A ve 3B çıktıları entegre edildikten sonra production-ready entegrasyon olarak ele alınır.
- Paralel çalışma yapısını koru: 2A ∥ 2B, 3A ∥ 3B ∥ 2.5; sadece bağımlılık sınırlarını ihlal etme.

## Kesinlikle yapılmayacaklar
- v1.0 backend fazlarına Next.js dashboard UI, Tauri desktop shell veya gerçek WebSocket dashboard işini dahil etme.
- Manual gate eksikse gerçek dış servis çalışıyor gibi kabul etme.
- Bir faz tamamlanmadan onun gerçek deliverable'ına bağlı sonraki fazı "tamam" sayma.
- Faz kapsamını büyütmek için yeni faz açma; özellikle yedek parça krizi mevcut fazlara dağıtılmıştır.
- Gerçek ERP/MRO/CMMS, gerçek satın alma, gerçek tedarikçi veritabanı, multi-tenant cloud deployment, mobil uygulama ve sensör tabanlı TimesFM anomalisi v1.0'a sokma.

## Out of scope / v1.1+
- TimesFM ile sensör tabanlı anomaly detection.
- Model fine-tuning beyond demo/few-shot hedefi.
- Gerçek ERP/MRO/satın alma execute entegrasyonu.
- Gerçek tedarikçi veritabanı ve dinamik stok optimizasyonu.
- Frontend dashboard/Tauri üretim özellikleri, açıkça istenmedikçe.

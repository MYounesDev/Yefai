# Gelecek Tahmini (Predictive Forecasting) Planı — v1.0 Revizyonu

> Yefai v1.0 platformuna gelecek tahmini özelliğinin eklenmesi için plan.
> Amaç: Anomali olmadan ÖNCE, mevcut aşınma hızından kritik eşiğe ne zaman ulaşılacağını tahmin etmek.
> **v1.0 kısıtı:** TimesFM ertelenmiştir. SADECE görüntü tabanlı (Anomalib) veri ile çalışılır.

---

## 📋 Genel Bakış

### Amaç

Operatörlere **proaktif bilgilendirme** sağlamak:
- "Takım #12, mevcut aşınma hızıyla ~20 saat içinde kritik eşiğe (200 µm) ulaşacak"
- "Bu takımda flank wear baskın (%87 olasılıkla)"
- "Aşınma hızı son 3 kontrolde %15 arttı — planlı bakımı öne çekin"

### v1.0 vs v1.1 Farkı

| Özellik | v1.0 (bu plan) | v1.1+ (sonra) |
|---------|---------------|---------------|
| Veri kaynağı | Sadece görüntü (Anomalib) | Görüntü + sensör |
| Tahmin yöntemi | Aşınma hızı × lineer projeksiyon | TimesFM zaman serisi tahmini |
| Tahmin ufku | 1-3 kontrol aralığı (saat-gün) | 50 adım ileri |
| Güven aralığı | Basit (sabit ±%15) | İstatistiksel (quantile) |
| Senaryo analizi | Hız sabit/artan/azalan | ML tabanlı simülasyon |
| Sensör füzyonu | Yok | Var |

### Kapsam

**Dahil:**
- ✅ Aşınma ilerleme hızı takibi (µm/saat)
- ✅ Kritik eşiğe kalan süre hesaplama
- ✅ Aşınma tipi olasılıkları (Anomalib'den gelen)
- ✅ Zaman serisi görselleştirme (geçmiş + projeksiyon)
- ✅ Basit senaryo: "hız sabit kalırsa / hızlanırsa / yavaşlarsa"
- ✅ Güven göstergesi (basit)
- ✅ Bildirim sistemi entegrasyonu (Phase 5 ile)

**Dahil Değil:**
- ❌ TimesFM zaman serisi tahmini → v1.1
- ❌ Sensör verisiyle tahmin → v1.1
- ❌ İstatistiksel güven aralığı → v1.1
- ❌ Otomatik sipariş sistemi
- ❌ Makine kontrolü (hız değiştirme vb.)
- ❌ ERP entegrasyonu

### İş Değeri
- **Plansız duruş önleme**: Arıza olmadan önce müdahale
- **Maliyet tasarrufu**: Planlı bakım < Acil onarım
- **Karar desteği**: Veri odaklı bakım kararları

---

## 🎯 Nasıl Yapılır? (v1.0 Yöntemi)

### 1. Aşınma İlerleme Hızı Takibi

**Kullanılacak: Anomalib PatchCore + Supabase geçmiş verisi**

- Her görüntüden Anomalib anomali skoru (0-1) al
- Anomali skorunu yaklaşık aşınma seviyesine (µm) eşle
  - Kalibrasyon: skor 0.0 → 0 µm, skor 0.5 → 100 µm, skor 1.0 → 200+ µm
- Aynı takımın son N kontrolündeki aşınma değerlerini Supabase'den çek
- Lineer regresyon ile aşınma hızını hesapla: µm/saat veya µm/kontrol
- Hesapla: `kalan_süre = (200 - mevcut_aşınma) / aşınma_hızı`

### 2. Aşınma Tipi Tespiti

**Kullanılacak: Anomalib (mevcut sınıflandırma)**

- Anomalib zaten aşınma tipi sınıflandırması yapıyor (FR-2.3)
- Mevcut etiketler: Flank wear, Adhesive wear, Combination
- Ek olarak: Crater wear tespiti (MATWI veri setinde varsa)

### 3. Kritik Eşik Projeksiyonu

**Birleştirme:**
- Anomalib anomali skoru → yaklaşık aşınma seviyesi
- Geçmiş kontroller → aşınma hızı
- Mevcut durum → kalan süre hesaplama
- Hız değişim trendi → basit güven göstergesi

**Çıktı:**
- Tahmini kritik eşik zamanı (saat cinsinden)
- En olası aşınma tipi
- Basit güven göstergesi (düşük/orta/yüksek — hızın kararlılığına göre)

### 4. Basit Senaryo Analizi (v1.0)

**3 senaryo, sabit çarpanlarla:**

1. **Mevcut hızda devam**: Aşınma hızı sabit → lineer projeksiyon
2. **Kötümser**: Aşınma hızı %25 artsa → daha erken kritik
3. **İyimser**: Aşınma hızı %25 azalsa (soğutma/bakım etkisi) → daha geç kritik

> v1.1'de TimesFM ile gerçek ML tabanlı senaryo simülasyonu yapılacak.

---

## 🛠️ Kullanılacak Teknolojiler

### Backend (Python) — Hepsi Mevcut

| Teknoloji | Amaç | Durum |
|-----------|------|-------|
| **Anomalib (PatchCore)** | Görüntü anomali tespiti + aşınma tipi | Phase 2'de geliyor |
| **NumPy/SciPy** | Lineer regresyon, hız hesaplama | Standart |
| **Supabase** | Geçmiş kontrolleri sorgulama | Phase 1'de geliyor |

### Frontend (TypeScript/React) — Hepsi Mevcut

| Teknoloji | Amaç | Durum |
|-----------|------|-------|
| **Recharts** | Zaman serisi grafikleri (geçmiş + projeksiyon) | Phase 4'te eklenecek |
| **Framer Motion** | Animasyonlar | Mevcut stack |
| **React Query** | API veri yönetimi | Phase 4'te eklenecek |

### Veritabanı

**Yeni alan (yeni tablo gerekmez):**
- `anomalies` tablosuna ek alanlar:
  - `estimated_wear_um`: Tahmini aşınma seviyesi (µm)
  - `wear_rate_um_per_hour`: Aşınma hızı
  - `hours_to_critical`: Kritik eşiğe kalan saat
  - `confidence`: Güven göstergesi (low/medium/high)

---

## 📊 Çıktılar Neye Benzer?

### 1. Ana Tahmin Paneli

```
┌─────────────────────────────────────────────────┐
│  🔮 TAHMIN - Makine #5 / Takım #12              │
├─────────────────────────────────────────────────┤
│                                                 │
│  📍 MEVCUT DURUM                                │
│  • Aşınma Seviyesi: 145 µm (Kritik: 200 µm)    │
│  • Aşınma Hızı: 2.8 µm/saat                    │
│  • Son Kontrol: 15 dk önce                      │
│                                                 │
│  ⚠️ TAHMİN                                      │
│                                                 │
│  🔴 Kritik eşiğe ~20 saat kaldı                 │
│     • Mevcut hızda: 20 saat                     │
│     • Hızlanırsa: 16 saat                       │
│     • Yavaşlarsa: 27 saat                       │
│                                                 │
│  Aşınma Tipi Olasılıkları:                      │
│  Flank Wear        ████████████████████  87%    │
│  Adhesive Wear     ██████████            34%    │
│  Combination       ██████                18%    │
│                                                 │
│  Güven: ORTA (son 3 ölçüm kararlı)              │
│                                                 │
│  💡 ÖNERİ: Takım değişimi planlanmalı           │
│                                                 │
└─────────────────────────────────────────────────┘
```

### 2. Aşınma Projeksiyon Grafiği

**Görsel öğeler:**
- Mavi çizgi: Geçmiş kontrollerdeki aşınma değerleri
- Mavi noktalar: Gerçek ölçümler
- Kırmızı kesikli çizgi: Lineer projeksiyon
- Kırmızı yatay çizgi: Kritik eşik (200 µm)
- Kırmızı dikey noktalı çizgi: Tahmini kritik anı
- Yeşil dikey çizgi: Şu anki zaman

### 3. Aşınma Hızı Trendi

```
Son 5 kontrol:
Kontrol #8:  ████████████ 120 µm  (hız: 3.1 µm/saat)
Kontrol #9:  █████████████ 135 µm  (hız: 2.9 µm/saat)
Kontrol #10: █████████████ 142 µm  (hız: 2.8 µm/saat)
Kontrol #11: █████████████ 145 µm  (hız: 2.8 µm/saat) ← Şimdi
Kontrol #12: █████████████  ???    (tahmini: 156 µm)
```

### 4. Çoklu Makine Durum Özeti

```
┌──────────┬──────────┬──────────┬──────────┐
│ Makine 1 │ Makine 2 │ Makine 3 │ Makine 4 │
│   🟢     │   🟢     │   🟡     │   🟢     │
│  45 µm   │  30 µm   │ 160 µm   │  60 µm   │
│ ~5 gün   │ ~7 gün   │ ~14 saat │ ~4 gün   │
└──────────┴──────────┴──────────┴──────────┘
┌──────────┬──────────┬──────────┬──────────┐
│ Makine 5 │ Makine 6 │ Makine 7 │ Makine 8 │
│   🔴     │   🟢     │   🟠     │   🟢     │
│ 145 µm   │  20 µm   │ 180 µm   │  35 µm   │
│ ~20 saat │ ~10 gün  │  ~8 saat │ ~6 gün   │
└──────────┴──────────┴──────────┴──────────┘
```

### 5. Bildirim Örneği (Phase 5 — Telegram/Email)

```
🔴 KRİTİK EŞİK UYARISI

Makine: #5
Takım: #12

⏰ Tahmini Kritik: ~20 saat içinde
📊 Mevcut Aşınma: 145 µm / 200 µm
📈 Aşınma Hızı: 2.8 µm/saat
🔧 Beklenen Sorun: Flank Wear (%87)

💡 Öneri: Takım değişimi planlanmalı

🔗 Detaylar için tıklayın
```

---

## 🔗 Mevcut Sisteme Entegrasyon

### Phase 2 (AI Inference) ile:
- Anomalib çıktısına `estimated_wear_um` alanı ekle
- Aşınma tipi olasılıklarını kaydet (zaten yapılıyor)

### Phase 4 (Dashboard) ile:
- **Yeni panel**: "Tahmin" sekmesi (mevcut dashboard içinde)
- Aşınma projeksiyon grafiği (Recharts)
- Çoklu makine durum kartları
- Mevcut gerçek zamanlı grafiklerle yan yana

### Phase 5 (Bildirim) ile:
- Kritiklik seviyesine göre bildirim:
  - <12 saat: Telegram + Email (acil)
  - 12-48 saat: Sadece dashboard uyarısı
  - >48 saat: Haftalık özette bilgi

### Yeni API Endpoint'leri (FastAPI)

```
GET  /api/predictions/{machine_id}
     → Makine için tahmin: kalan süre, aşınma hızı, senaryolar

GET  /api/predictions/{machine_id}/history
     → Geçmiş kontroller ve aşınma trendi

GET  /api/predictions/factory/overview
     → Tüm makinelerin özet durumu
```

### Yeni Frontend Rotaları (Next.js)

```
/dashboard/prediction/{machineId}
  → Detaylı tahmin sayfası

/dashboard/factory-overview
  → Tüm makineler durum kartları
```

---

## 📅 Implementasyon Adımları

### Adım 1: Backend — Aşınma Hızı Hesaplama
**Süre:** 1 gün
**Hangi fazda:** Phase 2 sonuna ek
- Anomalib skor → µm eşleme fonksiyonu
- Aynı takımın geçmiş kontrollerini Supabase'den çekme
- Lineer regresyon ile hız hesaplama
- Kritik eşiğe kalan süre hesaplama

### Adım 2: Backend — Tahmin API'si
**Süre:** 1 gün
**Hangi fazda:** Phase 4 başı
- `/api/predictions/{machine_id}` endpoint'i
- `/api/predictions/factory/overview` endpoint'i
- Basit senaryo hesaplama (sabit çarpanlı)

### Adım 3: Frontend — Tahmin Bileşenleri
**Süre:** 2 gün
**Hangi fazda:** Phase 4 içinde
- Aşınma projeksiyon grafiği (Recharts)
- Tahmin paneli komponenti
- Çoklu makine durum kartları
- Aşınma tipi bar chart

### Adım 4: API Entegrasyonu
**Süre:** 0.5 gün
**Hangi fazda:** Phase 4 içinde
- React Query hooks
- API endpoint'lerini bağla

### Adım 5: Bildirim Entegrasyonu
**Süre:** 1 gün
**Hangi fazda:** Phase 5 içinde
- Kritiklik seviyesine göre bildirim formatı
- PUQ AI webhook payload'ı

**Toplam Ek Süre:** ~5.5 gün (mevcut fazların içine dağıtılmış)
**Mevcut sürelere etkisi:** Phase 2 +1 gün, Phase 4 +2.5 gün, Phase 5 +1 gün

---

## 🎯 Başarı Kriterleri (v1.0)

### Teknik
- ✅ Anomalib skorundan aşınma seviyesi tahmini yapılabiliyor
- ✅ Aşınma hızı hesaplanabiliyor (son N kontrol üzerinden)
- ✅ Kritik eşiğe kalan süre gösteriliyor
- ✅ API yanıt süresi < 500ms
- ✅ Grafik render süresi < 500ms

### Kullanıcı Deneyimi
- ✅ Tahmin paneli anlaşılır ve okunabilir
- ✅ Grafikler interaktif (hover ile detay)
- ✅ Durum kartları renk kodlu (yeşil/sarı/kırmızı)
- ✅ Mobil responsive

### v1.0 için makul hedefler
- ✅ Aşınma ilerleme yönü doğru tahmin ediliyor (>%90)
- ✅ Operatör yaklaşan kritik durumu görebiliyor
- ❌ Hassas zaman tahmini → v1.1 (TimesFM ile)
- ❌ İstatistiksel güven aralığı → v1.1

---

## 🚀 Faz Yapısına Yerleştirme

```
Phase 1: Veri Altyapısı
    ↓
Phase 2: AI Inference (+ aşınma hızı hesaplama, +1 gün)
    ↓
Phase 3: RAG Chatbot
    ↓
Phase 4: Dashboard (+ tahmin paneli, +2.5 gün)
    ↓
Phase 5: Tauri + Bildirim (+ tahmin bildirimi, +1 gün)
```

**Phase 2.5 olarak ayrı faz YOK.** Tahmin özelliği mevcut fazlara dağıtılmıştır. Bu sayede:
- Yeni faz eklenmez, roadmap sadeleşir
- Her faz kendi sorumluluk alanındaki tahmin parçasını yapar
- Toplam süre artışı ~5.5 gün (kabul edilebilir)

---

## 📝 Notlar

- **v1.0'da beklenti yönetimi önemli**: Bu bir "trend göstergesi", hassas tahmin değil
- **TimesFM ile farkı**: v1.0 lineer projeksiyon yapar, v1.1'de TimesFM non-lineer paternleri yakalar
- **Demo avantajı**: Aşınma trend grafiği + "X saat kaldı" göstergesi hackathon'da etkileyici
- **Veri kalitesi kritik**: Aşınma hızı hesabı için aynı takımın en az 3-4 kontrol noktası gerekli

---

## 🔮 v1.1'e Geçiş Yolu

Bu plan v1.1'de şunlarla yükseltilecek:
- TimesFM 2.5 ile gerçek zaman serisi tahmini (horizon=50)
- Sensör verisi füzyonu (accelerometer + force + acoustic)
- İstatistiksel güven aralığı (quantile regression)
- ML tabanlı senaryo simülasyonu

v1.0'daki tüm API endpoint'leri ve frontend bileşenleri v1.1'de genişletilecek şekilde tasarlanır (geriye dönük uyumlu).

---

*Son güncelleme: 2026-05-15 — v1.0 scope'una uyarlandı (TimesFM yok)*

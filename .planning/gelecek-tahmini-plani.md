# Gelecek Tahmini (Predictive Forecasting) Planı

> Yefai platformuna gelecek tahmini özelliğinin eklenmesi için yüksek seviye plan.
> Amaç: Anomali olmadan ÖNCE, gelecekte ne zaman sorun çıkacağını tahmin etmek ve görselleştirmek.

---

## 📋 Genel Bakış

### Amaç

Operatörlere **proaktif bilgilendirme** sağlamak:
- "18-24 saat içinde flank wear bekleniyor"
- "Bu takım %87 olasılıkla 1 gün içinde kritik seviyeye ulaşacak"
- "Kesme hızını %10 azaltırsanız +24 saat kazanırsınız"

### Kapsam

**Dahil:**
- ✅ Gelecek tahmini (1-50 adım ileri)
- ✅ Aşınma tipi olasılıkları (flank, adhesive, crater, combination)
- ✅ Zaman serisi görselleştirme (grafik + timeline)
- ✅ Senaryo analizi ("ne olur?" simülasyonları)
- ✅ Çoklu sensör füzyonu
- ✅ Güven skoru hesaplama
- ✅ Bildirim sistemi entegrasyonu

**Dahil Değil:**
- ❌ Otomatik sipariş sistemi
- ❌ Makine kontrolü (hız değiştirme vb.)
- ❌ ERP entegrasyonu
- ❌ Stok yönetimi

### İş Değeri

- **Plansız duruş önleme**: Arıza olmadan önce müdahale
- **Maliyet tasarrufu**: Planlı bakım < Acil onarım
- **Üretim verimliliği**: Kesintisiz üretim planlaması
- **Karar desteği**: Veri odaklı bakım kararları

---

## 🎯 Nasıl Yapılır?

### 1. Zaman Serisi Tahmini

**Kullanılacak: TimesFM 2.5**

- Mevcut implementasyonda sadece 1 adım ileri tahmin yapılıyor
- **Değişiklik**: `horizon` parametresini 1'den 50'ye çıkar
- Çıktı: 50 adım ilerisi için tahmin + güven aralığı (üst/alt sınır)
- Aşınma hızını hesapla: kaç µm/saat artıyor?
- Kritik eşiğe (200 µm) ne zaman ulaşacağını hesapla

### 2. Aşınma Tipi Tahmini

**Kullanılacak: CLIP/SigLIP**

- Takım görüntüsünü analiz et
- 4 aşınma tipinin olasılığını hesapla:
  - Flank wear (yan aşınma)
  - Adhesive wear (yapışma)
  - Crater wear (krater)
  - Combination wear (kombine)
- Çıktı: Her tip için 0-1 arası olasılık

### 3. Sensör + Görüntü Füzyonu

**Birleştirme:**
- Zaman serisi tahmini → aşınma hızı
- Görüntü analizi → aşınma tipi
- Mevcut durum → kalan süre hesaplama
- Geçmiş doğruluk oranı → güven skoru

**Çıktı:**
- Tahmini arıza zamanı (saat cinsinden)
- En olası aşınma tipi
- Güven skoru (%0-100)

### 4. Senaryo Analizi

**3 farklı senaryo oluştur:**

1. **Mevcut hızda devam**: Hiçbir şey değişmezse ne olur?
2. **Hız %10 azaltma**: Üretim yavaşlatılırsa ne kadar süre kazanılır?
3. **Soğutma artırma**: Soğutma iyileştirilirse ne olur?

Her senaryo için:
- Tahmini arıza zamanı
- Risk seviyesi (düşük/orta/yüksek/kritik)
- Kazanılan zaman

---

## 🛠️ Kullanılacak Teknolojiler

### Backend (Python)

| Teknoloji | Amaç |
|-----------|------|
| **TimesFM 2.5** | Zaman serisi tahmini (horizon genişletme) |
| **Anomalib** | Görüntü anomali tespiti (mevcut) |
| **CLIP/SigLIP** | Aşınma tipi sınıflandırma |
| **NumPy/Pandas** | Veri işleme ve hesaplamalar |
| **SciPy/Statsmodels** | Güven aralığı hesaplama |

### Frontend (TypeScript/React)

| Teknoloji | Amaç |
|-----------|------|
| **Recharts** | Zaman serisi grafikleri |
| **Plotly.js** | İnteraktif grafikler (opsiyonel) |
| **Framer Motion** | Animasyonlar |
| **React Query** | API veri yönetimi |

### Veritabanı

**Yeni tablolar:**
- `predictions`: Tahmin kayıtları
- `prediction_outcomes`: Tahmin sonuçları (doğru/yanlış)

---

## 📊 Çıktılar Neye Benzer?

### 1. Ana Tahmin Paneli

```
┌─────────────────────────────────────────────────┐
│  🔮 GELECEK TAHMİNİ - Makine #5                 │
├─────────────────────────────────────────────────┤
│                                                 │
│  📍 MEVCUT DURUM                                │
│  • Takım Aşınması: 145 µm (Normal: <200 µm)    │
│  • Çalışma Süresi: 847 saat                    │
│                                                 │
│  ⚠️ TAHMİN EDİLEN SORUNLAR                      │
│                                                 │
│  1. 🔴 Flank Wear (Yan Aşınma)                  │
│     • Olasılık: %87                            │
│     • Tahmini Zaman: 18-24 saat içinde         │
│     • Kritik Eşik: 200 µm                      │
│                                                 │
│  2. 🟡 Adhesive Wear (Yapışma)                  │
│     • Olasılık: %34                            │
│     • Tahmini Zaman: 3-4 gün içinde            │
│                                                 │
│  💡 ÖNERİLER                                    │
│  • Takım değişimi planlanmalı                  │
│  • Kesme hızını %10 azaltmak +24 saat kazandırır│
│                                                 │
└─────────────────────────────────────────────────┘
```

### 2. Zaman Serisi Tahmin Grafiği

**Görsel öğeler:**
- Mavi çizgi: Geçmiş gerçek veriler
- Kırmızı kesikli çizgi: Gelecek tahmini
- Açık kırmızı alan: Güven aralığı
- Kırmızı yatay çizgi: Kritik eşik (200 µm)
- Kırmızı dikey çizgi: Tahmini arıza anı
- Yeşil dikey çizgi: Şu anki zaman

**Özellikler:**
- Zoom & Pan (yakınlaştırma)
- Hover ile detay gösterme
- PNG/PDF export

### 3. Aşınma Tipi Olasılık Grafiği

```
Flank Wear        ████████████████████████░░░░  87%
Adhesive Wear     █████████████░░░░░░░░░░░░░░  34%
Crater Wear       ████░░░░░░░░░░░░░░░░░░░░░░░  12%
Combination       ██████░░░░░░░░░░░░░░░░░░░░░  18%
```

Renk kodları:
- 🔴 Yüksek (>70%)
- 🟠 Orta (40-70%)
- 🟡 Düşük (20-40%)
- 🟢 Çok Düşük (<20%)

### 4. Senaryo Karşılaştırma Tablosu

| Senaryo | Arıza Zamanı | Olasılık | Risk | Kazanç |
|---------|--------------|----------|------|--------|
| Mevcut hızda devam | 20 saat | %87 | 🔴 Yüksek | - |
| Hız %10 azaltma | 44 saat | %65 |  Orta | +24 saat |
| Soğutma artırma | 60 saat | %45 | 🟢 Düşük | +40 saat |

### 5. Zaman Çizelgesi (Timeline)

```
ŞİMDİ
  ↓
  🟢 Aşınma: 145 µm
  │
  │  +6 saat
  ├──────────────────
  🟡 Aşınma: ~170 µm (Dikkat seviyesi)
  │
  │  +12 saat
  ├──────────────────
  🟠 Aşınma: ~190 µm (Uyarı seviyesi)
  │
  │  +18-24 saat
  ├──────────────────
  🔴 Aşınma: ~210 µm (KRİTİK - Arıza bekleniyor)
```

### 6. Çoklu Makine Heatmap

```
┌──────────┬──────────┬──────────┬──────────┐
│ Makine 1 │ Makine 2 │ Makine 3 │ Makine 4 │
│   🟢     │   🟢     │   🟡     │   🟢     │
│   12%    │   8%     │   45%    │   15%    │
│  15 gün  │  20 gün  │  4 gün   │  12 gün  │
└──────────┴──────────┴──────────┴──────────┘
┌──────────┬──────────┬──────────┬──────────┐
│ Makine 5 │ Makine 6 │ Makine 7 │ Makine 8 │
│   🔴     │   🟢     │   🟠     │   🟢     │
│   87%    │   5%     │   68%    │   10%    │
│  1 gün   │  25 gün  │  2 gün   │  18 gün  │
└──────────┴──────────┴──────────┴──────────┘
```

### 7. Bildirim Örneği (Telegram/Email)

```
🔴 GELECEK TAHMİNİ

Makine: #5
Takım: #12

⏰ Tahmini Arıza: 18-24 saat içinde
📊 Olasılık: %87
🔧 Beklenen Sorun: Flank Wear

💡 Öneriler:
• Takım değişimi planlanmalı
• Kesme hızını %10 azaltmak +24 saat kazandırır
• Soğutma sıvısı kontrolü önerilir

🔗 Detaylar için tıklayın
```

---

## 🔗 Nasıl Entegre Edilir?

### Mevcut Sisteme Entegrasyon

**Phase 2 (AI Inference) ile:**
- TimesFM'in `horizon` parametresini genişlet (1 → 50)
- CLIP ile aşınma tipi sınıflandırma ekle
- Füzyon fonksiyonu ekle (sensör + görüntü)

**Phase 4 (Dashboard) ile:**
- Yeni sekme: "Gelecek Tahmini"
- Mevcut gerçek zamanlı grafiklerle yan yana göster
- Tahmin paneli ekle

**Phase 5 (Bildirim) ile:**
- Kritiklik seviyesine göre bildirim gönder:
  - <24 saat: Telegram + SMS + Email
  - 24-72 saat: Telegram + Email
  - >72 saat: Sadece dashboard

### Yeni API Endpoint'leri

```
GET  /api/predictions/{machine_id}
     → Makine için gelecek tahmini

GET  /api/predictions/{machine_id}/scenarios
     → Senaryo analizleri

GET  /api/predictions/factory/heatmap
     → Tüm makinelerin durumu

POST /api/predictions/{prediction_id}/feedback
     → Tahmin sonucunu kaydet (doğru/yanlış)
```

### Yeni Frontend Sayfaları

```
/dashboard/prediction/{machineId}
  → Detaylı tahmin sayfası

/dashboard/factory-overview
  → Tüm makineler heatmap

/dashboard/scenarios/{machineId}
  → Senaryo karşılaştırma
```

---

## 📅 Implementasyon Adımları

### Adım 1: Backend - TimesFM Horizon Genişletme
**Süre:** 2 gün
- TimesFM model fonksiyonunu güncelle
- Güven aralığı hesaplama ekle
- Test yaz

### Adım 2: Backend - Aşınma Tipi Sınıflandırma
**Süre:** 2 gün
- CLIP entegrasyonu
- 4 aşınma tipi için sınıflandırma
- Test yaz

### Adım 3: Backend - Füzyon ve Tahmin Servisi
**Süre:** 3 gün
- Sensör + görüntü füzyonu
- Senaryo analizi fonksiyonu
- Güven skoru hesaplama
- Veritabanı şeması ve kayıt

### Adım 4: Frontend - Tahmin Bileşenleri
**Süre:** 4 gün
- Ana tahmin paneli
- Zaman serisi grafiği (Recharts)
- Aşınma tipi bar chart
- Senaryo karşılaştırma tablosu
- Timeline bileşeni
- Heatmap bileşeni

### Adım 5: API Entegrasyonu
**Süre:** 1 gün
- React Query hooks
- API endpoint'leri bağla
- Hata yönetimi

### Adım 6: Bildirim Entegrasyonu
**Süre:** 2 gün
- Tahmin bildirimi formatla
- Kritiklik seviyesine göre kanal seçimi
- Telegram/Email/SMS entegrasyonu

### Adım 7: Test ve Doğrulama
**Süre:** 2 gün
- Unit testler
- Integration testler
- Frontend testler
- End-to-end test

**Toplam Süre:** ~16 gün (2.5 hafta)

---

## 🎯 Başarı Kriterleri

### Teknik
- ✅ TimesFM 50 adım ileri tahmin yapabiliyor
- ✅ Aşınma tipi olasılıkları toplamı %100
- ✅ Güven skoru 0-1 arası
- ✅ API yanıt süresi < 2 saniye
- ✅ Grafik render süresi < 500ms

### Kullanıcı Deneyimi
- ✅ Tahmin paneli anlaşılır ve okunabilir
- ✅ Grafikler interaktif (zoom, hover)
- ✅ Bildirimler zamanında geliyor
- ✅ Mobil responsive

### İş Değeri
- ✅ Tahmin doğruluğu > %80
- ✅ Yanlış alarm oranı < %20
- ✅ Operatörler tahminlere güveniyor
- ✅ Plansız duruş azalıyor

---

## 🚀 Roadmap'e Ekleme

**Öneri: Phase 2.5 olarak ekle**

```
Phase 2: AI Inference Pipeline
    ↓
Phase 2.5: Gelecek Tahmini (YENİ)
    ↓
Phase 3: RAG Chatbot
    ↓
Phase 4: Dashboard (tahmin paneli dahil)
    ↓
Phase 5: Tauri + Bildirim
```

**Alternatif: Phase 4'e dahil et**
- Phase 4 süresini 1.5 haftadan 3 haftaya çıkar
- Dashboard ile birlikte geliştirilir

---

## 📝 Notlar

- **Otomasyon yok**: Sadece bilgilendirme ve görselleştirme
- **Karar kullanıcıda**: Sistem öneri verir, operatör karar verir
- **Geri bildirim döngüsü**: Tahminlerin doğruluğu kaydedilir, model iyileştirmesi için kullanılır
- **Demo için ideal**: Hackathon/sunum için çok etkileyici özellik

---

*Son güncelleme: 2026-05-15*

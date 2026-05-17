# puq.ai — Kapsamlı İnceleme

> **Tarih:** 15 Mayıs 2026
> **Kaynak:** https://docs.puq.ai/

---

## 1. puq.ai Nedir?

**puq.ai**, görsel bir **AI destekli workflow (iş akışı) otomasyon platformudur.** Kod yazmadan; API'ler, AI modelleri ve araçları birbirine bağlayarak güçlü otomasyonlar oluşturmanızı sağlar.

Sürükle-bırak (drag-and-drop) bir arayüzle, CRM'lerden biletleme sistemlerine, veritabanlarından AI modellerine kadar yüzlerce servisi görsel olarak birbirine bağlayabilirsiniz. Her workflow bir API olarak yayınlanabilir, belirli zamanlarda çalışacak şekilde planlanabilir veya webhook'lar ile tetiklenebilir.

Kısacası: **Zapier/Make benzeri bir otomasyon platformu, ama AI-first yaklaşımıyla — yani içinde gömülü AI modelleri, LLM desteği, vektör arama, OCR, ses/görüntü üretimi gibi yapay zeka yetenekleriyle geliyor.**

---

## 2. Ne İşe Yarar? — Temel Yetenekler

### 2.1. Görsel Workflow Oluşturma
- Sürükle-bırak ile akış tasarımı
- Her node (düğüm) tek bir sorumluluk taşır: veri al, işle, çıktı üret
- Node'lar birbirine bağlanarak pipeline oluşturur
- AI Copilot ile doğal dilde workflow tanımlama ("müşteri talebi geldiğinde ticket aç ve ekibine yönlendir" gibi)

### 2.2. AI Modelleri ile Entegrasyon
- **OpenAI** (GPT, Assistants API, embeddings, fine-tuning)
- **Claude (Anthropic)** (mesajlaşma, token sayma, batch işleme, prompt optimizasyonu)
- **Mistral AI** (hızlı metin üretimi, reasoning)
- **DeepL / Google Translate** (çeviri)
- **ElevenLabs** (text-to-speech, ses klonlama, müzik, ses efektleri)
- **AWS Comprehend / Textract** (dil analizi, OCR, fatura/ fiş okuma)
- **Pinecone / Qdrant** (vektör arama, RAG sistemleri)
- **Stability AI / fat.ai** (görsel ve video üretimi)

### 2.3. 200+ Entegrasyon (Bağlantı)
- **Google:** Gmail, Drive, Sheets, Docs, Calendar, Analytics, Tasks, Contacts
- **Microsoft:** Outlook, OneDrive, To-Do, Outlook Calendar
- **CRM & Satış:** Salesforce, HubSpot, Pipedrive, Zoho CRM
- **İletişim:** Slack, Webex, Zoom, Pushbullet
- **Depolama:** Box, Dropbox, OneDrive, Google Drive
- **Veritabanı:** Firebase Realtime DB, Cloud Firestore
- **Geliştirici:** GitHub, SSH, HTTP Utilities
- **Dosya & Medya:** YouTube, Reddit, Notion, RSS, Mailchimp, Eventbrite, Xero

### 2.4. API Katmanı (AI Router)
puq.ai'nin kendisi de bir **AI Router** olarak çalışır:
- Tek bir API endpoint'i (`https://api.puq.ai/`) üzerinden birden çok AI model sağlayıcısına erişim
- API token yönetimi
- Workflow'ları harici sistemlerden HTTP ile tetikleme
- Kredi bakiyesi sorgulama, model listeleme

### 2.5. Yayınlama & Debug
- Workflow versiyonlama (otomatik)
- Schedule ile periyodik çalıştırma
- Webhook ile event-driven tetikleme
- Her adımın log'landığı execution geçmişi ve debug arayüzü

---

## 3. Node Kategorileri (Workflow Bileşenleri)

| Kategori | Açıklama |
|---|---|
| **Trigger Nodes** | Workflow'u başlatan düğümler (Schedule, Webhook) |
| **Core Nodes** | Veri dönüşümü, HTTP, JSON/XML, CSV, Loop, Router, SSH, QR Code, RSS, Data Validator, Delay, Encryption, Image Tools, Server Monitor |
| **AI Nodes** | LLM'ler, çeviri, OCR, ses, görüntü, vektör arama, dil analizi |
| **Universal AI Nodes** | OpenAI ve Claude için birleşik arayüz |
| **Communication Nodes** | E-posta, mesajlaşma, bildirim |
| **Commerce Nodes** | E-ticaret, ödeme, fatura |
| **Sales & CRM Nodes** | Müşteri yönetimi, lead takibi |
| **Marketing Nodes** | E-posta kampanyaları, segmentasyon |
| **Support Nodes** | Ticket sistemleri, yardım masası |
| **Files & Content Nodes** | Dosya yönetimi, CMS |
| **Developer Tools** | Veritabanı, CI/CD, kuyruklar |
| **Analytics Nodes** | Metrik takibi, raporlama |
| **Productivity Nodes** | Görev yönetimi, takvim, formlar |
| **Payment Nodes** | Ödeme işleme (Stripe vb.) |
| **HR Nodes** | Çalışan yönetimi |
| **Forms & Surveys Nodes** | Form ve anket entegrasyonları |
| **Flow Control Nodes** | Dallanma, döngü, gecikme, routing |

---

## 4. Nerelerde Kullanılır? — Kullanım Senaryoları

### 4.1. CRM Otomasyonu
- Web sitesinden gelen lead'leri yakala → verileri zenginleştir → CRM'e (HubSpot/Salesforce) otomatik ekle
- Müşteri etkileşimlerini takip et ve segmentlere ayır

### 4.2. Destek/Kesintisiz (Support Triage)
- Gelen ticket'ları AI ile sınıflandır (acil/normal/düşük)
- Doğru ekibe otomatik yönlendir
- Müşteriye otomatik yanıt oluştur

### 4.3. Pazarlama Otomasyonu
- AI ile içerik üretimi (blog, sosyal medya, e-posta)
- Mailchimp ile otomatik kampanya yönetimi
- Sosyal medya takibi ve otomatik paylaşım

### 4.4. Veri Dönüşümü & Raporlama
- Google Sheets'ten veri al → temizle/dönüştür → veritabanına yaz
- Periyodik analitik raporları oluştur ve e-posta ile gönder

### 4.5. Fatura & Belge İşleme
- E-posta ekini otomatik tara (OCR ile)
- Fatura verilerini çıkar → muhasebe sistemine aktar → onay akışı başlat

### 4.6. AI-as-a-Service (AI Router)
- Tek bir API üzerinden OpenAI, Claude, Mistral gibi modellere eriş
- CI/CD pipeline'larında AI model çağrıları yap
- Batch işlemleri (toplu metin analizi, toplu çeviri)

### 4.7. E-ticaret & Sipariş Yönetimi
- Stok seviyelerini izle → kritik seviyede uyarı gönder
- Sipariş al → ödeme doğrula → kargo sürecini başlat

### 4.8. İnsan Kaynakları
- Yeni çalışan onboarding'i (hesap oluşturma, e-posta atama, doküman paylaşma)
- İzin talebi akışları

### 4.9. Ses & Medya Üretimi
- ElevenLabs ile sesli asistanlar, podcast otomasyonu
- AI ile görsel/video üretimi (pazarlama ve içerik ekipleri için)

---

## 5. Kimler Kullanır?

| Rol | Ne Amaçla |
|---|---|
| **Geliştiriciler** | Backend görevlerini otomatize etmek, workflow'ları API olarak yayınlamak |
| **Ops/SRE Ekipleri** | Süreçleri standartlaştırmak, manuel hataları azaltmak |
| **Data & AI Ekipleri** | AI modellerini iş mantığına entegre etmek, RAG sistemleri kurmak |
| **İş Kullanıcıları** | Kod yazmadan tekrarlayan işleri otomatize etmek |
| **Pazarlama Ekipleri** | İçerik üretimi, kampanya yönetimi, lead yönetimi |
| **Müşteri Destek Ekipleri** | Ticket triage, otomatik yanıt, yönlendirme |

---

## 6. Rakiplerinden Farkı

puq.ai, Make (eski Integromat) ve Zapier gibi platformlara benzer **ancak**:

- **AI-first yaklaşımı:** Tüm AI modelleri (OpenAI, Claude, Mistral, ElevenLabs, Pinecone vb.) native node olarak gömülü gelir
- **AI Copilot:** Doğal dil ile workflow oluşturma
- **AI Router:** Tek API üzerinden çoklu AI sağlayıcıya erişim
- **Versiyonlu workflow yönetimi:** Her yayın otomatik versiyonlanır
- **Ücretsiz başlangıç:** Hemen hesap açıp kullanmaya başlama imkanı

---

## 7. Güvenlik

- Rol bazlı erişim kontrolü (RBAC)
- API token ile kimlik doğrulama
- Şifrelenmiş ortam değişkenleri ve secret'lar
- Şifrelenmiş veri depolama

---

## 8. Özet

> **puq.ai, kod yazmayı gerektirmeyen, AI gücüyle çalışan bir görsel otomasyon platformudur.**
>
> Görsel bir arayüzle workflow'lar oluşturur, AI modellerini sürükle-bırak ile iş akışlarınıza eklersiniz. 200'den fazla entegrasyonu vardır. Workflow'ları API olarak yayınlayabilir, schedule ile çalıştırabilir veya webhook ile tetikleyebilirsiniz.
>
> **Kullanım alanları:** CRM otomasyonu, destek ticket triage, pazarlama içerik üretimi, belge işleme (OCR), e-ticaret, veri dönüşümü, AI-as-a-Service, ses/görsel üretimi, insan kaynakları süreçleri.
>
> **En büyük gücü:** AI modellerini (OpenAI, Claude, Mistral, ElevenLabs, Pinecone, AWS AI vb.) native olarak workflow'lara gömülü getirmesi ve tek bir API altında toplamasıdır.

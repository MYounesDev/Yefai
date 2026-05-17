# **Nesne Yönelimli Programlama ve Yazılım Mimarisinin Temelleri: SOLID, DRY, KISS ve YAGNI Prensiplerinin Karşılaştırmalı Analizi**

## **Giriş: Yazılım Krizleri ve İyi Tasarımın Evrimi**

Yazılım geliştirme disiplininin ilk yıllarında, sistemler genellikle küçük çaplıydı ve donanım kısıtlamaları nedeniyle kod tabanları tek bir geliştiricinin zihninde bütünüyle tutulabilecek kadar basitti. Ancak, bilgi işlem kapasitesinin artması ve iş dünyasının yazılımdan beklentilerinin eksponansiyel olarak büyümesiyle birlikte, projelerin karmaşıklığı da kontrolden çıkmaya başladı. İhtiyaçlar hızla değişirken, yazılım ekipleri mevcut kod tabanlarına sürekli yeni özellikler eklemek, yamalar yapmak ve acil durum çözümleri üretmek zorunda kaldı. Bu sürecin doğal bir sonucu olarak, yazılım dünyasında "Spaghetti code" (Spagetti kod) olarak bilinen, her bir modülün diğerine ölümcül ve karmaşık düğümlerle bağlı olduğu kaotik mimariler ortaya çıktı.

Nesne Yönelimli Programlama (OOP \- Object-Oriented Programming) bu kaosu çözmek vaadiyle popülerleşmiş olsa da, temel tasarım prensipleri olmadan kullanıldığında yalnızca "Nesne Yönelimli Spagetti" yaratmaktan öteye gidemedi. Sektördeki geliştiriciler, bir modülde yaptıkları ufak bir değişikliğin, sistemin tamamen alakasız bir köşesinde çöküşe yol açtığı kabus dolu senaryolarla her gün yüzleşmeye başladılar. Yazılım, doğası gereği "yumuşak" (soft) ve esnek olması gerekirken, giderek katılaşan ve dokunulması tehlikeli hale gelen bir yapıya dönüşüyordu.

Bu kaosu akademik ve pratik bir çerçevede ilk kez net bir şekilde tanımlayan kişi, 2000 yılında yayınladığı "Design Principles and Design Patterns" adlı çığır açıcı makalesiyle Robert C. Martin (yazılım sektöründeki bilinen adıyla Uncle Bob) olmuştur.1 Martin, başarılı ve faydalı yazılımların iş dünyasının doğası gereği sürekli evrim geçirmek zorunda olduğunu, ancak iyi tasarım prensipleri uygulanmadığında bu evrimin "Yazılım Çürümesi" (Software Rot) adı verilen amansız bir hastalığa dönüşeceğini açıkça ortaya koymuştur.1

Yazılım çürümesinin arkasında yatan ve geliştiricilere, özellikle de sektöre yeni adım atmış Junior yazılımcılara devasa acılar yaşatan dört temel klinik belirti bulunmaktadır. Bu belirtiler birbiriyle ilişkilidir ve sistemin kalitesini adım adım aşağı çeker:

| Çürüme Belirtisi | Kavramsal Tanım | Gerçek Dünya Yansıması ve Geliştirici Üzerindeki Etkisi |
| :---- | :---- | :---- |
| **Rigidity (Esnemezlik / Katılık)** | Yazılımın, en basit değişiklik isteklerinde bile aşırı direniş göstermesi durumudur. Alt seviyede yapılan ufak bir yapısal değişiklik, tüm üst seviye modüllerin de değiştirilmesini zincirleme olarak zorunlu kılar.3 | Sistemin betonlaşmasıdır. Yönetim basit bir buton rengi değişikliği istediğinde, geliştiricinin veritabanı şemasına kadar inmek zorunda kalmasıdır. Kod tabanında küçük bir iş, haftalarca süren bir eziyete dönüşür. |
| **Fragility (Kırılganlık)** | Yazılımın belirli bir yerinde yapılan değişikliğin, kavramsal olarak hiçbir bağı olmayan, projenin tamamen alakasız diğer alanlarını bozması ve çökertmesi eğilimidir.3 | Jenga oynamaya benzer. Geliştirici bir modülü düzeltirken diğeri kırılır. Bu durum, ekiplerde "çalışıyorsa dokunma" kültürünü ve kodda değişiklik yapma korkusunu doğurur.4 |
| **Immobility (Hareketsizlik)** | Yazılımın içindeki faydalı ve iyi çalışan bir parçanın, yüksek bağımlılıklar nedeniyle başka projelerde veya aynı projenin farklı bir bölümünde tekrar kullanılamamasıdır.3 | Geliştirici, daha önce yazılmış mükemmel bir fatura hesaplama algoritmasını yeni bir ekranda kullanmak ister; ancak algoritma kullanıcı arayüzüne o kadar sıkı bağlıdır ki, kopyalanamaz. Aynı mantık sıfırdan tekrar yazılır. |
| **Viscosity (Akışkanlık Direnci)** | Sisteme mimari açıdan "doğru" bir ekleme veya düzeltme yapmanın, "hack" (geçici, kirli ve hızlı çözüm) yapmaktan çok daha zor ve zaman alıcı olması durumudur.4 | Sistemin tasarımı, geliştiriciyi sürekli olarak yanlış yapmaya teşvik eder. Doğru çözümü uygulamak günler alacağından, geliştirici "şimdilik if-else ile geçiştirelim" diyerek teknik borcu artırır. |

Bu acı dolu ve yüksek maliyetli deneyimler, yazılım mimarisini tesadüflere bırakmamak adına yapısal bir anayasa oluşturma ihtiyacını doğurmuştur. Daha sonra 2004 yılı civarında Michael Feathers tarafından baş harfleri birleştirilerek "SOLID" akronimi haline getirilen bu beş temel prensip, nesne yönelimli programlamanın evrensel kuralları niteliğini kazanmıştır.2 Burada güdülen amaç, yeni başlayan geliştiricilere kuralları körü körüne ezberletmek değil; yazılımı esnek, bağımsız test edilebilir ve gelecekteki değişim rüzgarlarına karşı dirençli hale getirmenin mantığını aşılamaktır.5

## ---

**SOLID'in 5 Atlısı: Mimari Derinlik ve Gerçek Dünya Senaryoları**

Her bir prensibi salt teorik birer tanım olmaktan çıkarıp, gerçek dünyadaki iş mantığı sorunları, müşteri talepleri ve "Anti-Pattern" (uygulanmadığında başa gelen felaket) perspektifinden incelemek, konunun kavramsal derinliğini artırmaktadır.

### **1\. Single Responsibility Principle (SRP) \- Tek Sorumluluk Prensibi**

**Basit Tanım ve Amacı:** Tek Sorumluluk Prensibi, "Bir sınıfın değişmek için yalnızca bir nedeni olmalıdır" şeklindeki meşhur ifadeyle tanımlanır.2 Diğer bir deyişle, bir sınıf, modül veya fonksiyon yalnızca tek bir iş yapmalı ve tek bir sorumluluğa odaklanmalıdır. Sektördeki en büyük yanılgılardan biri, bu prensibin "bir sınıf sadece tek bir fonksiyon içerebilir" şeklinde anlaşılmasıdır. Aslında burada kastedilen "sorumluluk", yazılımın hizmet ettiği iş aktörleridir. Eğer bir sınıf, birden fazla farklı iş birimine (örneğin hem veritabanı yöneticisine hem de arayüz tasarımcısına veya pazarlama ekibine) aynı anda hizmet ediyorsa ve bu birimlerden gelecek farklı talepler aynı sınıfın güncellenmesini gerektiriyorsa, SRP ihlal ediliyor demektir.2

**Kötü Senaryo (Anti-Pattern): "Her İşin Adamı" (God Object) Sınıfı** Gerçek dünyadan yaygın bir senaryoyu ele alalım. Bir e-ticaret platformu geliştirilirken, sisteme yeni kayıt olan kullanıcıları yönetmek üzere bir KullaniciYonetici sınıfı tasarlanmıştır. Bu sınıf, kullanıcının bilgilerini doğrulamak, veritabanına kaydetmek ve ardından kullanıcıya bir "Hoş Geldiniz" e-postası göndermekle görevlendirilmiştir.7

// KÖTÜ SENARYO (Anti-Pattern)

Sınıf KullaniciYonetici:

Fonksiyon KullaniciKaydet(kullanici\_bilgileri):

// 1\. Sorumluluk: İş mantığı ve veri doğrulama

Eğer kullanici\_bilgileri.Email boş ise:

HataFırlat("Geçersiz e-posta\!")

    // 2\. Sorumluluk: Altyapı ve Veritabanı işlemleri  
    Veritabani.Baglan()  
    Veritabani.SQLCalistir("INSERT INTO Kullanicilar...", kullanici\_bilgileri)  
      
    // 3\. Sorumluluk: İletişim ve Dış Servisler  
    EpostaServisi.Baglan()  
    EpostaServisi.Gonder(kullanici\_bilgileri.Email, "Sistemimize hoş geldiniz, aramıza katıldığınız için mutluyuz\!")

*Eğer bunu uygulamasaydık ne olurdu?* Bu tasarım ilk bakışta masum ve pratik görünebilir. Ancak iş dünyası asla yerinde durmaz. Birkaç ay sonra pazarlama departmanı, e-posta formatının düz metin yerine göze hitap eden, resimli bir HTML şablonuna geçirilmesini talep eder. Geliştirici, sadece bir e-posta metni değiştirmek için KullaniciYonetici sınıfını açmak zorunda kalır. Tam bu sırada yanlışlıkla veritabanı bağlantı satırında bir karakter silinir.2 Pazarlama ekibinin talebi (birinci değişim nedeni) yüzünden, veritabanı kayıt sistemi (ikinci sorumluluk) çöker. Bu durum Fragility (Kırılganlık) yaratır.4 Ayrıca, bir gün sistemde "Şifremi Unuttum" özelliği yapılması gerektiğinde ve sadece e-posta gönderme işlevi lazım olduğunda, bu kod parçası yerinden sökülüp tekrar kullanılamaz (Immobility).4 Sınıf, tek bir iş yapmamakta; adeta bir İsviçre çakısı gibi her görevi üstlenerek bakımını imkansız hale getirmektedir.

**İyi Senaryo: Sorumlulukların İzole Edilmesi ve Orkestrasyon** SRP'nin uygulandığı temiz bir mimaride, kod, hizmet ettiği işlevlere göre tamamen yalıtılmış ayrı sınıflara bölünmelidir. Biri sadece veritabanı işlemi yaparken, diğeri sadece iletişimden sorumlu olmalıdır.7

// İYİ SENARYO: Sorumlulukların Dağıtılması

// Sadece doğrulama iş kurallarından sorumlu sınıf

Sınıf KullaniciDogrulayici:

Fonksiyon GecerliMi(kullanici\_bilgileri):

Döndür (kullanici\_bilgileri.Email boş değil)

// Sadece veritabanı kayıt işleminden sorumlu sınıf

Sınıf KullaniciDeposu:

Fonksiyon VeritabaninaKaydet(kullanici\_bilgileri):

Veritabani.Baglan()

Veritabani.SQLCalistir("INSERT INTO...", kullanici\_bilgileri)

// Sadece dış dünyayla iletişimden sorumlu sınıf

Sınıf BildirimServisi:

Fonksiyon HosgeldinEpostasiGonder(email\_adresi):

EpostaServisi.Gonder(email\_adresi, "Yeni HTML Şablonlu Hoş Geldiniz Mesajı")

// Süreci yöneten üst katman (Orkestratör)

Sınıf KayitOrkestratoru:

Fonksiyon YeniKullaniciOlustur(kullanici\_bilgileri):

Eğer KullaniciDogrulayici.GecerliMi(kullanici\_bilgileri):

KullaniciDeposu.VeritabaninaKaydet(kullanici\_bilgileri)

BildirimServisi.HosgeldinEpostasiGonder(kullanici\_bilgileri.Email)

Bu modüler yapı sayesinde, e-posta servis sağlayıcısı değiştiğinde veya yeni bir pazarlama kampanyası eklendiğinde, veritabanı mantığının barındığı kod satırları zırhlı bir kasanın içindeymişçesine güvende kalır.7 Sınıfların adlandırılması bile kolaylaşmıştır ("Ve" bağlacı içeren karmaşık isimlendirmeler ortadan kalkar).2

### **2\. Open/Closed Principle (OCP) \- Açık/Kapalı Prensibi**

**Basit Tanım ve Amacı:** Açık/Kapalı prensibi, Bertrand Meyer tarafından yazılım dünyasına kazandırılmış, sonrasında Robert C. Martin tarafından polimorfizm (çok biçimlilik) bağlamında yeniden yorumlanmıştır. Prensip açıkça şunu söyler: Yazılım varlıkları (sınıflar, modüller, fonksiyonlar) gelişime açık (Open for extension), ancak değişime kapalı (Closed for modification) olmalıdır.2 Yani, iş dünyasından sisteme yeni bir özellik veya kural eklenmesi talep edildiğinde, mevcut ve tıkır tıkır çalışan eski kodların içeriğine dokunulmamalıdır; bunun yerine sisteme yeni kod parçacıkları dışarıdan "eklemlenmelidir".2

**Kötü Senaryo (Anti-Pattern): Bitmek Bilmeyen İf-Else ve Switch Blokları** Bir e-ticaret mağazasının sepet ve sipariş sistemi için indirimleri hesaplayan merkezi bir modül tasarlandığını ele alalım. Projenin ilk günlerinde sistem basittir: Sadece "Sezon İndirimi" ve "Müşteri Sadakat İndirimi" bulunmaktadır. Geliştirici, bu iki basit kuralı pratik bir switch veya if/else bloğu ile sisteme entegre eder.9

// KÖTÜ SENARYO (Anti-Pattern)

Sınıf IndirimHesaplayici:

Fonksiyon Hesapla(musteri\_tipi, tutar):

Eğer musteri\_tipi \== "Sezonluk":

Döndür tutar \* 0.90 // %10 indirim

Eğer musteri\_tipi \== "SadikMusteri":

Döndür tutar \* 0.85 // %15 indirim

Eğer musteri\_tipi \== "Normal":

Döndür tutar

// YENİ GEREKSİNİM: "Kara Cuma" veya "Öğrenci" indirimi geldiğinde burası açılacak.

*Eğer bunu uygulamasaydık ne olurdu?* Ticari bir yazılım asla ilk günkü haliyle kalmaz. Şirket büyüdükçe ve pazarlama agresifleştikçe, sisteme sürekli yeni kurallar yağmaya başlar: "Öğrenci İndirimi", "VIP İndirimi", "Kara Cuma İndirimi", "Anneler Günü İndirimi". Her yeni kural talebi geldiğinde, geliştirici IndirimHesaplayici sınıfını fiziksel olarak açmak, o devasa if-else zincirinin arasına yeni bir satır sıkıştırmak zorunda kalır.9 Her müdahale, kodun mevcut stabilitesini tehlikeye atar. Daha da kötüsü, Kalite Güvence (QA) ekipleri, yeni eklenen "Öğrenci İndirimi"nin kazara "Sadık Müşteri" indirimini bozup bozmadığından emin olmak için tüm sistemi baştan aşağı yeniden test etmek (Regression Testing) zorunda kalır.2 Bu döngü sürekli tekrarlandığında kod Rigidity (Esnemezlik) yaratır; yüzlerce satırlık if bloklarını okumak, yönetmek ve genişletmek imkansızlaşır.9

**İyi Senaryo: Soyutlama (Abstraction) ve Strateji Deseni ile Genişletme** Problemin çözümü, somut ifadelere bağımlı kalmak yerine, soyutlamalardan (Arayüzler veya Soyut Sınıflar) faydalanmaktır. Bir arayüz oluşturularak, her indirim türü kendi bağımsız sınıfına hapsedilir.9

// İYİ SENARYO: OCP Uygulaması

// Soyutlama (Sözleşme)

Arayüz IIndirimStratejisi:

Fonksiyon IndirimUygula(tutar)

// Mevcut Özellikler

Sınıf SezonlukIndirim uygular IIndirimStratejisi:

Fonksiyon IndirimUygula(tutar):

Döndür tutar \* 0.90

Sınıf SadikMusteriIndirimi uygular IIndirimStratejisi:

Fonksiyon IndirimUygula(tutar):

Döndür tutar \* 0.85

// Çekirdek Hesaplayıcı (Değişime tamamen kapalı\!)

Sınıf IndirimHesaplayici:

Fonksiyon Hesapla(IIndirimStratejisi strateji, tutar):

Döndür strateji.IndirimUygula(tutar)

Yarın pazarlama ekibi "Kara Cuma" indirimi talep ettiğinde, mevcut kodların (IndirimHesaplayici, SezonlukIndirim vb.) hiçbirine dokunulmaz. Sadece KaraCumaIndirimi adında, IIndirimStratejisi'ni uygulayan yepyeni bir sınıf oluşturulup sisteme dahil edilir.9 Çekirdek kod, yeni özelliklere ve stratejilere sonuna kadar *açık*, ancak mevcut kodun fiziksel olarak değiştirilmesine tamamen *kapalıdır*.2 Kalite ekipleri sadece yeni eklenen Kara Cuma sınıfını test eder; diğerlerinin bozulmadığından matematiksel olarak emin olunur.

### **3\. Liskov Substitution Principle (LSP) \- Liskov'un Yerine Geçme Prensibi**

**Basit Tanım ve Amacı:** Bilgisayar bilimcisi Barbara Liskov tarafından 1987 yılında "Veri Soyutlama" temalı bir konferans sunumunda tanımlanan bu prensip, nesne yönelimli programlamadaki kalıtım (inheritance) mekanizmasının nasıl doğru kullanılacağını dikte eder.2 Prensip der ki: Bir üst sınıfın (veya arayüzün) kullanıldığı her yerde, uygulamanın genel davranışını, tutarlılığını veya mantığını bozmadan onun alt sınıfları (türetilmiş sınıflar) da kullanılabiliyor olmalıdır.2 Alt sınıflar, ebeveynlerinin belirlediği "sözleşmeye" (Design by Contract) tam olarak sadık kalmalı, ebeveynin beklemediği zorlayıcı ön koşullar getirmemeli ve ebeveynin davranışını beklenmedik şekilde saptırmamalıdır.12

**Kötü Senaryo (Anti-Pattern): Beklenmeyen İstisnalar ve Matematiksel Paradokslar** Mentörlük seanslarında klasik olarak verilen örnek Kare-Dikdörtgen paradoksudur. Matematiksel gerçeklikte bir "Kare", özel bir "Dikdörtgen" türüdür (Is-A ilişkisi). Ancak bu kavramsal gerçeklik, koda "Kare, Dikdörtgenden türer" şeklinde aktarıldığında korkunç sonuçlar doğurur.13 Bir dikdörtgenin genişliğini değiştirdiğinizde yüksekliği sabit kalır; ancak bir karenin genişliğini değiştirdiğinizde kuralları gereği yüksekliği de otomatik değişmek zorundadır. Sistemi dikdörtgen beklerken kare ile beslediğinizde, alan hesaplamaları tamamen hatalı sonuç verir.13

Bunu iş dünyasında daha kritik bir senaryo olan E-ticaret Ödeme Sistemleri üzerinden incelemek, konunun vahametini daha net gösterir.14

// KÖTÜ SENARYO (Anti-Pattern)

Sınıf StandartOdemeYontemi:

Fonksiyon FaturaAdresiDogrula()

Fonksiyon KrediKartiNumarasiDogrula()

Fonksiyon OdemeyiCek(tutar)

Sınıf BankaKarti uygular StandartOdemeYontemi:

// Tüm metotlar sorunsuz çalışır, adres ve kart doğrulanır.

Sınıf KriptoCuzdan uygular StandartOdemeYontemi:

Fonksiyon FaturaAdresiDogrula():

HataFırlat("Desteklenmeyen İşlem: Kripto ağında fiziksel adres yoktur\!")

Fonksiyon KrediKartiNumarasiDogrula():  
    HataFırlat("Desteklenmeyen İşlem: Kripto cüzdanlarda kart numarası bulunmaz\!")  
      
Fonksiyon OdemeyiCek(tutar):  
    // Cüzdandan cüzdana transfer yap.

*Eğer bunu uygulamasaydık ne olurdu?* Ana ödeme işleyicisi (Orchestrator), sıradaki ödeme tipinin geleneksel mi yoksa modern mi olduğunu umursamadan polimorfizm (çok biçimlilik) yeteneği sayesinde StandartOdemeYontemi sınıfı üzerinden işlem yapmaya çalışacaktır. Döngü sırası KriptoCuzdan nesnesine geldiğinde, sistem "Adresi doğrula" metodunu çağıracak ve birden "Adres yok\!" diyerek sistemde ölümcül bir hata (Exception) fırlatıp tüm sipariş hattını çökertecektir.15 Kripto cüzdan, görünüşte bir ödeme yöntemi olsa da, koda döküldüğünde ebeveyni olan standart ödeme yönteminin davranışsal yerine tam olarak geçememiştir. Bu, klasik bir LSP ihlalidir ve yazılımı son derece kırılgan (Fragile) yapar.

**İyi Senaryo: Davranışsal Sözleşmelerin Doğru Tasarlanması** Çözüm, gerçek dünyadaki isim benzerliklerine aldanıp zorlama bir kalıtım hiyerarşisi kurmak yerine, yetenekleri ince düşünülmüş spesifik arayüzlere ayırmaktır.14 Kripto ödemesi ile geleneksel kredi kartı ödemesinin çalışma mekanizmalarının temelden farklı olduğu kabul edilmelidir.

// İYİ SENARYO: Doğru Soyutlama ve Sözleşmeler

// Her ödeme yönteminin ortak noktası sadece ödeme almaktır.

Arayüz IOdemeIslemcisi:

Fonksiyon OdemeyiCek(tutar)

// Sadece kart gerektiren işlemler için ek sözleşme

Arayüz IKrediKartiDestegi:

Fonksiyon KartVeAdresDogrula()

Sınıf KrediKartiIslemcisi uygular IOdemeIslemcisi, IKrediKartiDestegi:

Fonksiyon KartVeAdresDogrula():

// Banka API'sine gidip adres ve kart onaylanır

Fonksiyon OdemeyiCek(tutar):

// Karttan para çekilir

Sınıf KriptoIslemcisi uygular IOdemeIslemcisi:

Fonksiyon OdemeyiCek(tutar):

// Kripto ağında cüzdan transferini doğrudan gerçekleştir.

Bu tasarımda, üst seviye ödeme alma servisi sadece IOdemeIslemcisi arayüzü ile ilgilenir ve gereksiz yere "Adres doğrula" beklentisine girmez. Sistemi hangi alt sınıf devralırsa alsın, süreç beklendiği gibi işler ve çökmeler yaşanmaz.14

### **4\. Interface Segregation Principle (ISP) \- Arayüz Ayrımı Prensibi**

**Basit Tanım ve Amacı:** Arayüz Ayrımı Prensibi, Robert C. Martin tarafından Xerox firmasına danışmanlık yaptığı sırada, firmanın yazıcı sistemlerindeki kod karmaşasını çözerken formüle edilmiştir.17 Temel öğreti şudur: "İstemciler (sınıflar), kullanmadıkları ve asla ihtiyaç duymayacakları arayüz metotlarına bağımlı olmaya zorlanmamalıdır." 2 Eğer bir arayüz çok fazla metod içeriyorsa (Fat/Bulky Interface), bu durum arayüzün çok fazla sorumluluk üstlendiğinin göstergesidir. Monolitik büyük arayüzler yerine, işlevsel bazda bölünmüş küçük, yalın ve spesifik rollere sahip arayüzler tercih edilmelidir.19

**Kötü Senaryo (Anti-Pattern): Kullanılmayan Metotların Zorbalığı** Xerox örneğine benzer şekilde, modern bir ofis otomasyon sisteminde tüm ofis cihazlarını temsil etmesi planlanan devasa bir IAkilliMakine arayüzü tasarlandığını düşünelim.18 Veya lojistik ve teslimat yazılımlarındaki taşıtları ele alalım; her aracı kapsayacak genel bir IArac arayüzü oluşturulmuştur.20

// KÖTÜ SENARYO (Anti-Pattern)

Arayüz IAkilliMakine:

Fonksiyon CiktiYazdir()

Fonksiyon BelgeTara()

Fonksiyon FaksGonder()

Sınıf LazerYazici uygular IAkilliMakine:

// Gelişmiş bir makinedir. Yazdır, Tara ve FaksGonder işlemlerinin hepsini başarıyla uygular.

Sınıf BasitTermalFisYazici uygular IAkilliMakine:

Fonksiyon CiktiYazdir():

// Rulo kağıda basit fiş yazdır.

Fonksiyon BelgeTara():

HataFırlat("Desteklenmiyor: Benim tarayıcım yok\!")

Fonksiyon FaksGonder():

HataFırlat("Desteklenmiyor: Faks modemi bulunmuyor\!")

*Eğer bunu uygulamasaydık ne olurdu?* Sadece fiş yazdırmak için tasarlanmış basit bir cihaz olan BasitTermalFisYazici, sırf hiyerarşik sisteme dahil olabilmek için devasa arayüzün tüm şartlarını sağlamaya zorlanmıştır. Geliştirici, kodu derleyebilmek için içi boş veya hata fırlatan metotlar yazmak zorunda kalır (Buna endüstride "Dummy implementations" veya "Poisoned methods" denir).18 Bu durum, hem kod kirliliği yaratır hem de sistemdeki diğer modülleri yanlış yönlendirir. Daha vahim olanı; yarın öbür gün gelişmiş tarayıcılar için BelgeTara(cozunurluk\_seviyesi) şeklinde metoda yeni bir parametre eklenmesi gerektiğinde, tarama yeteneğiyle uzaktan yakından alakası olmayan BasitTermalFisYazici sınıfı da arayüz değiştiği için anlamsız yere güncellenmek, yeniden derlenmek ve test edilmek zorunda kalacaktır.18

**İyi Senaryo: Odaklanmış Mini Arayüzler ve Rol Ayrımı** Sistemdeki yetenekler, devasa bir çatı altında toplanmak yerine, "Roller" bazında küçük, esnek ve ayrık arayüzlere parçalanmalıdır.18

// İYİ SENARYO: Rollerin Ayrıştırılması

Arayüz IYazdirici:

Fonksiyon CiktiYazdir()

Arayüz ITarayici:

Fonksiyon BelgeTara()

Arayüz IFaksCihazi:

Fonksiyon FaksGonder()

Sınıf BasitTermalFisYazici uygular IYazdirici:

Fonksiyon CiktiYazdir():

// Sadece kendi bildiği ve donanımının yettiği işi yapar. Diğer rollerle ilgilenmez.

Sınıf GelismisOfisMakinesi uygular IYazdirici, ITarayici, IFaksCihazi:

// Tüm yeteneklere sahip cihaz, birden fazla arayüzü uygulayarak yeteneklerini belirtir.

Bu temiz tasarım sayesinde, sistemin hiçbir modülü kendisine ait olmayan bir sorumluluğun teknik yükünü çekmek zorunda kalmaz. Sistem modülerleşir, yeni özellikler eklemek sadece ilgili sınıfları etkiler.17

### **5\. Dependency Inversion Principle (DIP) \- Bağımlılıkların Tersine Çevrilmesi Prensibi**

**Basit Tanım ve Amacı:** Mimariyi en çok koruyan ve esneklik katan prensiplerden biridir. Geleneksel yapısal programlamada yüksek seviyeli modüller (iş kurallarını, algoritmaları, politikaları içeren çekirdek katmanlar), çalışabilmek için her zaman düşük seviyeli modüllere (veritabanı işlemleri, dosya okuma/yazma, API çağrıları gibi teknik detaylara) bağımlı olarak tasarlanırdı.22 DIP bu hiyerarşiyi tamamen reddeder ve bağımlılık yönünü "tersine" çevirir.2 İki temel kuralı vardır:

1. Üst seviye modüller, alt seviye modüllere doğrudan bağımlı olmamalıdır. Her ikisi de "Soyutlamalara" (Abstractions \- arayüzler) bağımlı olmalıdır.2  
2. Soyutlamalar, teknik detaylara bağımlı olmamalıdır. Tam tersine, teknik detaylar soyutlamalara bağımlı olmalıdır.22

**Kötü Senaryo (Anti-Pattern): Somut Sınıflara Doğrudan ve Sıkı Bağımlılık (Tight Coupling)** En çok karşılaşılan mimari katliamlardan biri, kıymetli iş mantığı katmanının (Domain/Business Logic), doğrudan veritabanı veya framework teknolojisi ile iç içe geçirilmesidir.24

// KÖTÜ SENARYO (Anti-Pattern)

// Düşük Seviyeli Teknik Modül

Sınıf MySQLVeritabani:

Fonksiyon SiparisKaydet(siparis\_bilgisi):

// Spesifik SQL INSERT sorguları çalıştırır.

// Yüksek Seviyeli İş Modülü

Sınıf SiparisYonetimi:

Fonksiyon SiparisOnayla(siparis\_bilgisi):

Eğer StokKontrolu.MevcutMu(siparis\_bilgisi):

// Sıkı Bağımlılık: Sınıf içinde doğrudan somut nesne yaratılıyor\!

MySQLVeritabani db \= YENİ MySQLVeritabani()

db.SiparisKaydet(siparis\_bilgisi)

*Eğer bunu uygulamasaydık ne olurdu?* Üst seviyeli, şirketin en değerli iş kurallarını barındıran SiparisYonetimi sınıfı, en alt seviyeli teknik bir altyapı detayına (MySQLVeritabani) sıkı sıkıya (tightly coupled) kelepçelenmiştir.24 Altı ay sonra şirket yönetimi artan veri trafiği sebebiyle ilişkisel bir veritabanı olan MySQL'den vazgeçip, döküman tabanlı NoSQL bir veritabanına (örneğin MongoDB) geçiş yapma kararı aldığında tam bir felaket yaşanır.24 MySQL'e göbekten bağlı olan tüm iş mantığı sınıflarının içi tek tek açılacak, veritabanı bağlantı kodları sökülecek ve yeniden yazılacaktır. Üstelik bu yapı, kodun izole bir şekilde test edilmesini (Unit Testing) de imkansız kılar. Çünkü veritabanı ayağa kaldırılmadan SiparisYonetimi sınıfını çalıştırmak mümkün değildir.25

**İyi Senaryo: Araya Bir Soyutlama (Sözleşme) Koymak (Repository Pattern ile Inversion)** Sistemin merkezine teknik detaylar (MySQL, Oracle, Mongo) değil, şirketin "İş İhtiyacı" konur. Veritabanı aracı, iş katmanının belirlediği kurallara uymak zorunda bırakılır.25 Bağımlılığın yönü değişir.

// İYİ SENARYO: Bağımlılığın Tersine Çevrilmesi

// SOYUTLAMA: Üst katmanın neye ihtiyacı olduğunu belirten sözleşme

Arayüz ISiparisDeposu:

Fonksiyon Kaydet(siparis\_bilgisi)

// Yüksek Seviyeli İş Modülü (Veritabanının ne olduğundan tamamen habersizdir)

Sınıf SiparisYonetimi:

// Bağımlılık artık dışarıdan enjekte ediliyor (Dependency Injection)

Değişken ISiparisDeposu \_depo

// Sınıf yaratılırken HANGİ deponun kullanılacağına dış dünyadaki yapıcı karar verir  
Fonksiyon SiparisYonetimi\_Olusturucu(ISiparisDeposu depo):  
    \_depo \= depo

Fonksiyon SiparisOnayla(siparis\_bilgisi):  
    Eğer StokKontrolu.MevcutMu(siparis\_bilgisi):  
        \_depo.Kaydet(siparis\_bilgisi) // Hangi DB olduğunu bilmez, sadece sözleşmeye güvenir.

// Düşük Seviyeli Teknik Modül (Üst katmanın kurallarına uymak zorundadır)

Sınıf MongoDBSiparisDeposu uygular ISiparisDeposu:

Fonksiyon Kaydet(siparis\_bilgisi):

// MongoDB'ye özgü JSON formatında kayıt kodları

Bu yapı (endüstride Hexagonal Architecture, Ports and Adapters veya Clean Architecture olarak da bilinir 26), SiparisYonetimi'nin dış dünyadan tamamen izole olmasını sağlar. İstenildiği an MongoDBSiparisDeposu yazılarak sisteme entegre edilebilir; bu sırada iş kurallarının tek bir satırına dahi dokunulmaz. Birim testleri yazılırken, bellekte çalışan (In-Memory) sahte bir ISiparisDeposu oluşturularak kod saniyeler içinde test edilebilir.25

## ---

**Diğer Temel Yazılım Felsefeleri: DRY, KISS ve YAGNI**

SOLID prensipleri mimarinin yapısal omurgasını oluştururken, aşağıdaki üç önemli prensip yazılımın "zihniyetini", ekiplerin verimliliğini ve geliştiricinin problem çözme yaklaşımını şekillendirir.27

### **DRY (Don't Repeat Yourself \- Kendini Tekrar Etme)**

**Mantığı ve Felsefesi:** Yazılım mühendisliğinin temel köşe taşlarından biridir. Andy Hunt ve Dave Thomas'ın kült kitabı *The Pragmatic Programmer* aracılığıyla popülerleşen bu prensip, "Bir sistemdeki her bilginin (knowledge), iş kuralının veya niyetin tek, kesin ve yetkili bir temsili olmalıdır" der.27

**Kritik Uyarı ve Yaygın Yanılgı:** Yeni başlayan (Junior) geliştiriciler bu prensibi çok yüzeysel bir şekilde okuyup, sadece "Aynı kod bloklarını kopyala-yapıştır yapmaktan kaçınmak" olarak algılarlar. Oysa DRY, kodun karakter dizilimiyle değil, **bilginin, iş kuralının ve niyetin** tekrarıyla ilgilidir.30 Örneğin; "Bir kullanıcının sisteme üye olabilmesi için 18 yaşından büyük olması gerekir" kuralı bir iş bilgisidir. Eğer bu 18 yaş kuralı veritabanı şemasında bir kontrol (constraint) olarak, arka uç (Backend) kodlarında bir API validasyonu olarak ve mobil uygulamadaki kullanıcı arayüzünde ayrı ayrı tanımlanmışsa, görünürde "kopyala-yapıştır" kodu olmasa bile devasa bir DRY ihlali yapılmış demektir.30 Sistemdeki her tekrar, tutarsızlığa davetiyedir. Yarın yaş sınırı 21'e çıkarıldığında, eğer bilgi üç farklı yere dağılmışsa ve biri güncellenmeyi unutulursa, sistem ölümcül hatalar üretir.32 Kod tekrarından kaçınmak sistemin bakım maliyetini düşürür ve kural değişikliklerinin tek bir merkezden, risksiz şekilde halledilmesini garanti eder.28

### **KISS (Keep It Simple, Stupid \- Basit Tut, Aptal\!)**

**Mantığı ve Felsefesi:** KISS prensibi, karmaşıklığın yazılımın ve sürdürülebilirliğin bir numaralı düşmanı olduğu gerçeğine dayanır.28 Çözümler, o anki problemi çözebilecek mümkün olan en basit, en anlaşılır ve en dolaysız haliyle tasarlanmalıdır.28

Geliştiricilerin, özellikle teknoloji trendlerini yakından takip edenlerin, genellikle basit bir iş için gereğinden fazla teknoloji kullanma eğilimi vardır. Eğer bir veri dönüşüm problemini iki satırlık düz, okunabilir bir algoritma çözüyorsa, o iş için araya kuyruk sistemleri (Message Brokers), beş farklı tasarım deseni (Design Pattern) veya karmaşık refleksif araçlar ekleyip sistemi hantallaştırmak ve okunmaz hale getirmek KISS prensibine ihanettir.2 Basit kodların okunabilirliği çok yüksektir, çok daha az hata (bug) barındırırlar ve ekibe yeni katılan bir geliştiricinin projenin işleyişini kavrayıp adapte olma süresini dramatik şekilde kısaltırlar.27 Kodun akıllılığı değil, netliği ve anlaşılabilirliği değerlidir.

### **YAGNI (You Aren't Gonna Need It \- Buna İhtiyacın Olmayacak)**

**Mantığı ve Felsefesi:** Agile (Çevik) yazılım geliştirme metodolojisinin bir dalı olan Extreme Programming (XP) kültüründen doğan bu prensip, sadece ve sadece *o anki mevcut iş gereksinimi* için kod yazmayı öğütler.2 Yaratıcılarından Ron Jeffries'in belirttiği gibi: "Her zaman işlevselliği gerçekten ihtiyacınız olduğunda inşa edin, ileride lazım olacağını öngördüğünüz (ama kesin olmayan) durumlar için asla şimdiden kod yazmayın.".2

Geliştiricilerin zihnindeki "Gelecekte kesin lazım olur, şimdiden altyapısını kurayım da sonradan uğraşmayayım" düşüncesi, masum görünse de projenin kaynaklarını emen bir zehirdir.2 Çünkü yazılım endüstrisinde öngörülen o "gelecek", hiçbir zaman tam olarak geliştiricinin hayal ettiği gibi gelmez. Müşterinin talepleri, pazarın yönü değişir. Talep edilmeden yazılan her gereksiz soyutlama, her ek parametre ve her kullanılmayan altyapı, kod tabanını gereksiz yere şişirir, test sürelerini uzatır ve gerçek, acil olan özelliklerin teslimatını geciktirir.34 YAGNI, spekülatif (varsayımsal) programlamayı reddeder; "En basit, en hızlı işe yarayan şeyi yapın" felsefesinin savunucusudur.28

## ---

**Mimari Zeka Testi: Çatışmalar ve Karşılaştırmalı Analiz**

Bir Junior geliştiriciyi, yılların deneyimine sahip bir "Senior" (Kıdemli) mimardan ayıran şey, bu prensiplerin teorik tanımlarını ezbere bilmesi değildir. Asıl ustalık, **prensiplerin birbiriyle çeliştiği durumlarda (Trade-off yönetimi) doğru dengeyi bulabilmesi**, ne zaman bir prensibi diğerine feda edeceğini öngörebilmesidir. Prensip dogmatizmi (kurallara körü körüne ve bağlamdan kopuk şekilde itaat etmek), genellikle çok kötü ve yönetilemez tasarımlarla sonuçlanır.32 Aşağıdaki gerçek dünya olayları, teorinin pratikte nasıl sınırlandırıldığını veya çatıştığını açıkça ortaya koymaktadır.

### **Çatışma 1: SRP ve DRY Arasındaki Ölümcül Yanılsama (Sahte Duplikasyon)**

Yazılım geliştirirken en sık düşülen tuzaklardan biri, DRY (Tekrar Etme) prensibine olan saplantının, SRP'yi (Tek Sorumluluk) ve kodun gelecekteki esnekliğini feci şekilde bozmasıdır. Buna endüstride "Sahte Duplikasyon" (False Duplication) veya rastlantısal kod tekrarı denir.29

**Senaryo: "Pişirme" İşlemi Yanılgısı** Bir restoran otomasyon sistemi yazdığınızı hayal edin. Sistemde "Yumurta Pişir" ve "Et Pişir" adında iki farklı modül bulunmaktadır. Şu anki mutfak prosedürlerine göre her iki işlem de koda şu şekilde yansımıştır: "Malzemeyi tavaya koy, sıcaklığı 150 dereceye ayarla, 5 dakika bekle, ocaktan al".32 İki farklı sınıfta tamamen aynı kod satırları bulunmaktadır. Genç bir geliştirici bu durumu fark eder. Kod tekrarını bir günah olarak (DRY ihlali) gördüğü için hemen müdahale eder. Yumurta ve Et modüllerindeki kodları siler ve sistemin ortasına ortak, merkezi bir MalzemePisir(malzeme\_tipi) fonksiyonu (Abstraction) oluşturur. Geliştirici kodu kısalttığı ve tekrarı önlediği için kendisiyle gurur duyar.

**Ne oldu? SRP Feda Edildi ve Kod Kırılganlaştı.** Yumurta pişirmek ve et pişirmek kod mimarisi (sözdizimi) olarak anlık bir tesadüf eseri birbirine tamamen aynı *görünse* bile, temsil ettikleri **iş bilgisi, etkilendikleri süreçler ve değişme nedenleri** birbirinden tamamen farklıdır.29 Bir ay sonra restoran şefi menüyü ve tarifleri günceller: "Yumurtalar çok kuruyor, bundan sonra yumurta 2 dakika yüksek ateşte pişirilsin. Et ise aynen kalmaya devam etsin.".32 Geliştirici, büyük bir çaresizlikle kendi oluşturduğu o muazzam merkezi MalzemePisir() fonksiyonunun içine girmek zorunda kalır. Şöyle "hack"ler yazmaya başlar: Eğer malzeme \== YUMURTA ise 2 dakika bekle, DEĞİLSE 5 dakika bekle. Birkaç ay sonra tavuk eklenir, vegan burger eklenir. Ortak diye yazılan fonksiyon, iç içe geçmiş if-else bloklarıyla dolu bir canavara, "Spagetti" koda dönüşür.

Sırf DRY kurallarına uymak ve 5 satır kodu tekrar etmemek adına uygulanan bu erken soyutlama (Premature Abstraction), SRP'yi ihlal etmiştir.29 Fonksiyon artık hem yumurta pişirme politikalarından hem et pişirme kurallarından sorumlu hale gelmiştir ve birden fazla değişme nedenine (Multiple reasons to change) sahiptir. Bir kural sırf görünüşte benziyor diye (DRY aşkına) SRP'yi bozmak, sistemi "Fragile" (Kırılgan) hale getirir. Bir üründeki değişiklik, diğer ürünün de bozulma riskini taşır.32

**Mimarinin Altın Kuralı (Rule of Three):** Yazılım mühendisi Martin Fowler'ın ortaya koyduğu "Üçler Kuralı" (Rule of Three) ve AHA (Avoid Hasty Abstractions \- Aceleci Soyutlamalardan Kaçın) prensibi burada dengeyi sağlar.29 Bir kodun tekrar edildiğini (duplikasyon) ikinci kez gördüğünüzde, onu birleştirmek için acele etmeyin; kopyalamaya izin verin.29 Çünkü tekrar eden kodun yönetimi, yanlış yapılmış bir soyutlamayı çözmekten çok daha ucuz ve kolaydır. Ancak aynı kuralın veya kodun üçüncü kez yazıldığına şahit oluyorsanız ve hepsinin aynı iş aktörüne (aynı değişim nedenine) hizmet ettiğinden eminseniz, o zaman ortak bir soyutlama (DRY) yapın.29 Yanlış bir soyutlama, kod tekrarından daha fazla teknik borç üretir.32

### **Çatışma 2: SOLID'in İhtişamına Karşı YAGNI ve KISS'in İsyanı (Aşırı Mühendislik \- Over-Engineering)**

SOLID prensipleri, doğası gereği projenin gelecekteki olası büyüme senaryolarına ve kural değişikliklerine karşı bir zırh sağlamayı vaat eder. Ancak "geleceği öngörerek sağlam mimari kurmak" ile "KISS ve YAGNI prensiplerini hunharca çiğneyerek karmaşıklık yaratmak" arasındaki çizgi inanılmaz derecede incedir. Çoğu zaman küçük ölçekli bir projeye %100 SOLID uygulamaya çalışmak, basit bir problemi içinden çıkılmaz bir "Mimari Astronotluk" (Architecture Astronaut) vakasına dönüştürür.2

**Senaryo: "Atılabilir" Bir Raporlama Script'i ve Mimari Astronotlar** Şirketin İnsan Kaynakları (İK) departmanı, IT ekibinden ufak bir rica da bulunur: "Veritabanımızdaki aktif kullanıcıların e-posta listesini bu cuma günkü etkinlik için çekip ekrana alt alta listeleyecek ufak bir araç yazabilir misiniz? Sadece bu cuma kullanacağız, sonra atabilirsiniz.".2 Bu görevi devralan teori tutkunu geliştirici, işi ciddiye alarak en mükemmel ve esnek mimariyi kurmaya (SOLID) karar verir:

1. İleride sistemin başka veritabanlarına da bağlanabileceğini düşünerek IUserRepository arayüzü ve dependency inversion (DIP) kurar.2  
2. Raporun belki ilerde PDF veya Excel çıktılarına da ihtiyaç duyabileceği varsayımıyla (YAGNI ihlali), devasa bir "Strategy Pattern" kurgular ve IReportGenerator, IOutputFormatter gibi arayüzler yazar (OCP ve ISP).2  
3. Bu devasa hiyerarşiyi birbirine bağlamak için projeye ağır bir "Dependency Injection Container" kütüphanesi ekler.

**Ne oldu? YAGNI ve KISS Yok Edildi.** Sadece 10 satırlık basit bir döngü ve basit bir konsol yazdırma işlemiyle çözülebilecek, 1 saat sürecek olan bu geçici sorun (KISS), sırf SOLID uğruna günlerce süren, onlarca sınıfa ve gereksiz soyutlamalara bölünmüş bir projeye dönüşmüştür.2 Müşteri henüz "Bunu PDF'e dönüştür" veya "Oracle veritabanına bağla" dememişken (YAGNI), geliştirici bunlara hazır devasa bir konfigürasyon canavarı kurmuştur.2

Bu eylem, ünlü yazılım düşünürü Joel Spolsky'nin tanımıyla tam bir "Mimari Astronot" (Architecture Astronaut) davranışıdır.2 Mimari astronotlar, kullanıcının gerçekte ihtiyaç duyduğu "basit mango meyvesini teslim etmekle" ilgilenmezler; onlar meyveyi taşıyacak olan kamyonun tekerlek mimarisini aşırı soyutlamalarla (örneğin "veri aktarım araçları platformu") tartışmayı tercih ederler ve oksijensiz yüksek irtifalarda (gerçeklikten uzak) gezinirler.2

Başka bir popüler analoji olan "Köprü Analojisi" ile durumu açıklayalım: Geliştiricinin yaptığı bu hamle, sadece bir metre genişliğinde ve yaz aylarında kuruyan küçük bir dereyi yaya olarak geçmek için çelik halatlı, devasa betonarme ayaklara sahip asma bir köprü inşa etmeye benzer.2 Köprünün inşaat mimarisi (SOLID) muazzamdır, depreme dayanıklıdır; ancak o anki iş ihtiyacı için (YAGNI) tamamen zaman, efor ve para israfıdır. O dere için birkaç tahta kalas (KISS) tamamen yeterlidir.2

**Mimarinin Altın Kuralı (Denge Noktası):** Eğer küçük, spesifik, bir defaya mahsus ("throwaway") bir uygulama yazılıyorsa veya projenin gereksinimleri henüz kristalleşmemiş, sürekli değişen bir girişim (startup) ortamındaysanız; birkaç satırlık basit, düz ve "çalışan" kod (KISS), devasa bir SOLID altyapısına kesinlikle tercih edilmelidir.2 Her şey baştan en son detaya kadar tasarlanmaya (Big Design Up Front) çalışılmamalıdır.2 Ancak proje organik olarak büyüdükçe, değişiklik talepleri artıp kod yönetimi acı vermeye başladığında ve yeni özellikler *gerçekten* talep edildiğinde, var olan basit kodlar SOLID prensipleri çerçevesinde yeniden yapılandırılmalıdır (Refactoring).2 YAGNI ve SOLID'in barış içinde bir arada yaşadığı bu tatlı nokta, yazılım sektöründe "Zamanında (Just-in-Time) Mimari" olarak adlandırılır.2

### **Karşılaştırmalı Karar Matrisi: Hangi Durumda Hangi Prensip Öne Çıkar?**

Gerçek dünya senaryolarında, mimarın projenin özelliklerine göre hangi felsefeyi merkeze alacağına karar vermesi gerekir. Bu kararları kolaylaştırmak için endüstri standartlarında kabul gören aşağıdaki matris referans alınabilir 2:

| Projenin Bağlamı ve Sorun | Odaklanılacak Öncelikli Prensip | Göz Ardı Edilebilecek İkincil Prensip | Mimari Kararın Arkasındaki Gerekçe |
| :---- | :---- | :---- | :---- |
| **Erken Aşama Startup / Hızlı Prototipleme (PoC)** | KISS, YAGNI | SOLID | Müşteri ihtiyaçları netleşmemiştir. Ürünün piyasaya çıkış hızı (Time-to-Market) kritik öneme sahiptir. Gereksiz arayüzler ve soyutlamalar vakit kaybıdır. İş kuralları netleşene kadar kod basit tutulur. |
| **Sık Değişen İş Kuralları ve Büyük Ekipler (Enterprise)** | OCP, SRP, DIP | KISS | Sistemin yıllarca yaşayacağı ve onlarca farklı modülün sürekli güncelleneceği kesinleşmiştir. Kodun açık-kapalı kuralına göre tasarlanması ve bağımlılıkların tersine çevrilmesi zorunludur. Aksi halde sistem kendi ağırlığı altında çöker. |
| **Rastlantısal Olarak Benzeyen Kod Blokları** | SRP | DRY | Aynı kod yapısı tamamen farklı departmanlara veya aktörlere hizmet ediyorsa (örneğin muhasebenin KDV hesaplaması ile arayüzdeki fiyat gösterimi tahmini), tek sorumluluğu (SRP) korumak ve bağımlılığı ayırmak adına kodun tekrar etmesine (Rule of Three) göz yumulur.29 |
| **Donanım ve Dış Servis Entegrasyonları** | ISP, LSP | DRY | Dış sistemlerin (Farklı model ödeme cihazları, yazıcılar) yetenekleri birbirinden farklıdır. Her donanım türü için spesifik, izole arayüzler yazılarak (ISP) alt sınıfların hata üretmesi engellenir. |

## ---

**Sonuç ve Genel Değerlendirme**

Nesne yönelimli programlama dünyasında hiçbir kural mutlak bir dogma veya kutsal bir metin değildir. Robert C. Martin'in yazılım dünyasına kazandırdığı SOLID prensipleri, büyüyen sistemleri Rigidity (Esnemezlik), Fragility (Kırılganlık) ve çürümeden kurtarmak için titizlikle formüle edilmiş kusursuz bir mimari rehberdir. Ancak bu rehberin, projenin bağlamından, ölçeğinden ve iş gerçeklerinden kopuk bir şekilde, sırf "kitaba uysun" diye körü körüne uygulanması, kod tabanını gereksiz soyutlama katmanlarıyla parçalayarak bilişsel karmaşıklığa yol açan farklı türde bir canavara dönüşebilir.

Yazılım geliştirme süreci statik bir inşaat projesi değil, değişen koşullara adapte olması gereken dinamik bir mühendislik eylemidir. Yetkin bir yazılım mimarının en önemli görevi, sadece kurallara uyan kod yazmak veya tasarım desenlerini sergilemek değildir. Gerçek ustalık; bir projenin ne zaman KISS'in sunduğu pragmatik basitliğe, ne zaman YAGNI'nin sağladığı geliştirme hızına, ne zaman DRY'ın merkezi kontrol yeteneğine ve nihayetinde ne zaman SOLID'in sarsılmaz zırhına ihtiyacı olduğuna karar verebilmekte gizlidir.

"Yanlış bir soyutlamanın bedeli, kod tekrarının maliyetinden her zaman daha yüksektir" gerçeği hiçbir zaman akıldan çıkarılmamalıdır. Sistemin o anki gerçek müşteri ihtiyaçları somutlaşmadan, gelecekteki varsayımsal problemler için devasa mimari kurgulara girişilmemelidir. Endüstri tecrübeleri açıkça göstermektedir ki; mutlak kusursuz ve her ilkeye uyan bir kod tabanı yoktur. Aksine, iş bağlamına, ayrılan zamana ve eldeki kaynaklara en uygun şekilde kurgulanmış, Trade-off (ödünleşim) yönetimi bilinçli yapılmış ve doğru noktalarda esnemeyi bilen sistemler vardır. Gerçek anlamda sürdürülebilir, dayanıklı ve değer üreten yazılımlar tam da bu denge noktasında filizlenir.

#### **Alıntılanan çalışmalar**

1. SOLID Principles in Object Oriented Design – BMC Software | Blogs, erişim tarihi Nisan 25, 2026, [https://www.bmc.com/blogs/solid-design-principles/](https://www.bmc.com/blogs/solid-design-principles/)  
2. SOLID principles vs YAGNI \- Software Engineering Stack Exchange, erişim tarihi Nisan 25, 2026, [https://softwareengineering.stackexchange.com/questions/32618/solid-principles-vs-yagni](https://softwareengineering.stackexchange.com/questions/32618/solid-principles-vs-yagni)  
3. S.O.L.I.D. Principles \- ProAndroidDev, erişim tarihi Nisan 25, 2026, [https://proandroiddev.com/s-o-l-i-d-principles-60e0f91afa6](https://proandroiddev.com/s-o-l-i-d-principles-60e0f91afa6)  
4. Is Your Software Breaking Down? Exploring Software Rot | by ..., erişim tarihi Nisan 25, 2026, [https://medium.com/kayvan-kaseb/is-your-software-breaking-down-exploring-software-rot-a1bfc35bb2e1](https://medium.com/kayvan-kaseb/is-your-software-breaking-down-exploring-software-rot-a1bfc35bb2e1)  
5. SOLID Design Principles Explained: Building Better Software Architecture \- DigitalOcean, erişim tarihi Nisan 25, 2026, [https://www.digitalocean.com/community/conceptual-articles/s-o-l-i-d-the-first-five-principles-of-object-oriented-design](https://www.digitalocean.com/community/conceptual-articles/s-o-l-i-d-the-first-five-principles-of-object-oriented-design)  
6. Does this class design violate the single responsibility principle?, erişim tarihi Nisan 25, 2026, [https://softwareengineering.stackexchange.com/questions/306801/does-this-class-design-violate-the-single-responsibility-principle](https://softwareengineering.stackexchange.com/questions/306801/does-this-class-design-violate-the-single-responsibility-principle)  
7. Understanding the Single Responsibility Principle in S.O.L.I.D \- DEV Community, erişim tarihi Nisan 25, 2026, [https://dev.to/rakibrahman/understanding-the-single-responsibility-principle-in-solid-57b8](https://dev.to/rakibrahman/understanding-the-single-responsibility-principle-in-solid-57b8)  
8. SOLID Deep Dive: Single Responsibility Principle Explained | by Ömer Okumuş \- Medium, erişim tarihi Nisan 25, 2026, [https://medium.com/@omerokumus3/solid-deep-dive-single-responsibility-principle-explained-a7dbddab18c2](https://medium.com/@omerokumus3/solid-deep-dive-single-responsibility-principle-explained-a7dbddab18c2)  
9. \#2 Open Close Principle \['O' in SOLID\] \- DEV Community, erişim tarihi Nisan 25, 2026, [https://dev.to/vinaykumar0339/2-open-close-principle-o-in-solid-2jj6](https://dev.to/vinaykumar0339/2-open-close-principle-o-in-solid-2jj6)  
10. Open-Closed principle: Enhancing code modularity \- Arnaud Langlade, erişim tarihi Nisan 25, 2026, [https://www.arnaudlanglade.com/solid-open-close-principle/](https://www.arnaudlanglade.com/solid-open-close-principle/)  
11. Mastering the Open/Closed Principle (OCD) with C\# with Examples | by Pankaj Mishra, erişim tarihi Nisan 25, 2026, [https://medium.com/@mishra.pankaj/mastering-the-open-closed-principle-with-c-with-examples-94f5e5fb4519](https://medium.com/@mishra.pankaj/mastering-the-open-closed-principle-with-c-with-examples-94f5e5fb4519)  
12. SOLID Design Principles Explained: The Liskov Substitution Principle with Code Examples, erişim tarihi Nisan 25, 2026, [https://stackify.com/solid-design-liskov-substitution-principle/](https://stackify.com/solid-design-liskov-substitution-principle/)  
13. What is an example of the Liskov Substitution Principle? \- Stack Overflow, erişim tarihi Nisan 25, 2026, [https://stackoverflow.com/questions/56860/what-is-an-example-of-the-liskov-substitution-principle](https://stackoverflow.com/questions/56860/what-is-an-example-of-the-liskov-substitution-principle)  
14. Implementing Payment Gateways with the Liskov Substitution Principle \- DEV Community, erişim tarihi Nisan 25, 2026, [https://dev.to/asifzcpe/empowering-your-laravel-application-mastering-payment-gateways-with-the-liskov-substitution-principle-30pg](https://dev.to/asifzcpe/empowering-your-laravel-application-mastering-payment-gateways-with-the-liskov-substitution-principle-30pg)  
15. Liskov Substitution Principle (LSP) In IOS: How To Write Trustworthy Code?, erişim tarihi Nisan 25, 2026, [https://swiftandmemes.com/liskov-substitution-principle-lsp-in-ios-how-to-write-trustworthy-code/](https://swiftandmemes.com/liskov-substitution-principle-lsp-in-ios-how-to-write-trustworthy-code/)  
16. The Liskov Substitution Principle Explained with Real-World Examples \- Medium, erişim tarihi Nisan 25, 2026, [https://medium.com/@marisama11239/the-liskov-substitution-principle-explained-with-real-world-examples-02f8158f9375](https://medium.com/@marisama11239/the-liskov-substitution-principle-explained-with-real-world-examples-02f8158f9375)  
17. SOLID Design Principles Explained: Interface Segregation with Code Examples \- Stackify, erişim tarihi Nisan 25, 2026, [https://stackify.com/interface-segregation-principle/](https://stackify.com/interface-segregation-principle/)  
18. Mastering the Interface Segregation Principle (ISP) in C\# with Examples | by Pankaj Mishra, erişim tarihi Nisan 25, 2026, [https://medium.com/@mishra.pankaj/mastering-the-interface-segregation-principle-isp-in-c-with-examples-b5d8d6e03e05](https://medium.com/@mishra.pankaj/mastering-the-interface-segregation-principle-isp-in-c-with-examples-b5d8d6e03e05)  
19. Interface Segregation Principle: A Real-World Example | by Sagarbhatt | Medium, erişim tarihi Nisan 25, 2026, [https://medium.com/@sagarbhatt85/interface-segregation-principle-a-real-world-example-5cff2242df18](https://medium.com/@sagarbhatt85/interface-segregation-principle-a-real-world-example-5cff2242df18)  
20. Interface Segregation Principle Explained \- ITU Online IT Training, erişim tarihi Nisan 25, 2026, [https://www.ituonline.com/tech-definitions/what-is-interface-segregation-principle-isp/](https://www.ituonline.com/tech-definitions/what-is-interface-segregation-principle-isp/)  
21. Interface Segregation Principle \- Getting Solid with SOLID \- Part 4 \- The Seeley Coder, erişim tarihi Nisan 25, 2026, [https://www.seeleycoder.com/blog/solid-part-4-interface-segregation-principle/](https://www.seeleycoder.com/blog/solid-part-4-interface-segregation-principle/)  
22. SOLID Design Principles Explained: Dependency Inversion \- Stackify, erişim tarihi Nisan 25, 2026, [https://stackify.com/dependency-inversion-principle/](https://stackify.com/dependency-inversion-principle/)  
23. Dependency inversion principle \- Stack Overflow, erişim tarihi Nisan 25, 2026, [https://stackoverflow.com/questions/79171237/dependency-inversion-principle](https://stackoverflow.com/questions/79171237/dependency-inversion-principle)  
24. SOLID — Dependency Inversion Principle (Part 5\) | by Matthias Schenk | Medium, erişim tarihi Nisan 25, 2026, [https://medium.com/@inzuael/solid-dependency-inversion-principle-part-5-f5bec43ab22e](https://medium.com/@inzuael/solid-dependency-inversion-principle-part-5-f5bec43ab22e)  
25. The Repository Pattern \- by Charlie Steele \- Klaviyo Engineering, erişim tarihi Nisan 25, 2026, [https://klaviyo.tech/the-repository-pattern-e321a9929f82](https://klaviyo.tech/the-repository-pattern-e321a9929f82)  
26. The importance of the dependency inversion principle \- Triple D, erişim tarihi Nisan 25, 2026, [https://www.tripled.io/07/05/2019/dependency-inversion-principle/](https://www.tripled.io/07/05/2019/dependency-inversion-principle/)  
27. Python Principles Playbook: SOLID to YAGNI Examples | Clean Code Guide \- Medium, erişim tarihi Nisan 25, 2026, [https://medium.com/@ramanbazhanau/python-principles-playbook-from-solid-to-yagni-on-examples-b98445e11c9c](https://medium.com/@ramanbazhanau/python-principles-playbook-from-solid-to-yagni-on-examples-b98445e11c9c)  
28. KISS, DRY, SOLID, YAGNI — A Simple Guide to Some Principles of Software Engineering and Clean Code | by HlfDev | Medium, erişim tarihi Nisan 25, 2026, [https://medium.com/@hlfdev/kiss-dry-solid-yagni-a-simple-guide-to-some-principles-of-software-engineering-and-clean-code-05e60233c79f](https://medium.com/@hlfdev/kiss-dry-solid-yagni-a-simple-guide-to-some-principles-of-software-engineering-and-clean-code-05e60233c79f)  
29. Applying DRY Correctly: Overcoming Misconceptions and ... \- Medium, erişim tarihi Nisan 25, 2026, [https://medium.com/@justamlguy/applying-dry-correctly-5b8b8f4d5068](https://medium.com/@justamlguy/applying-dry-correctly-5b8b8f4d5068)  
30. How the DRY Principle in Programming Prevents Duplications in AI-Generated Code, erişim tarihi Nisan 25, 2026, [https://www.faros.ai/blog/ai-generated-code-and-the-dry-principle](https://www.faros.ai/blog/ai-generated-code-and-the-dry-principle)  
31. "Yes, Please Repeat Yourself" and other Software Design Principles I Learned the Hard Way : r/programming \- Reddit, erişim tarihi Nisan 25, 2026, [https://www.reddit.com/r/programming/comments/1cckf07/yes\_please\_repeat\_yourself\_and\_other\_software/](https://www.reddit.com/r/programming/comments/1cckf07/yes_please_repeat_yourself_and_other_software/)  
32. The Dark Side of Don't Repeat Yourself \- DEV Community, erişim tarihi Nisan 25, 2026, [https://dev.to/sharma-tech/the-dark-side-of-dont-repeat-yourself-o4k](https://dev.to/sharma-tech/the-dark-side-of-dont-repeat-yourself-o4k)  
33. 3 software development principles I wish I knew earlier in my career, and the power of YAGNI, KISS, and DRY \- Reddit, erişim tarihi Nisan 25, 2026, [https://www.reddit.com/r/programming/comments/1bmicj0/3\_software\_development\_principles\_i\_wish\_i\_knew/](https://www.reddit.com/r/programming/comments/1bmicj0/3_software_development_principles_i_wish_i_knew/)  
34. Understanding the principle of software development with DRY, KISS, YAGNI, and the criticisms of SOLID | by 石井, erişim tarihi Nisan 25, 2026, [https://schimizu.com/understanding-the-principle-software-development-with-dry-kiss-yagni-and-the-criticisms-of-solid-036dbe28e649](https://schimizu.com/understanding-the-principle-software-development-with-dry-kiss-yagni-and-the-criticisms-of-solid-036dbe28e649)  
35. SOLID, Clean Code, DRY, KISS, YAGNI Principles \+ React \- Gerardo Perrucci, erişim tarihi Nisan 25, 2026, [https://www.gperrucci.com/blog/engineering/solid-clean-yagni-kiss](https://www.gperrucci.com/blog/engineering/solid-clean-yagni-kiss)
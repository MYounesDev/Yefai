# **Yazılım Mühendisliği Temelleri: Mimari Prensiplerin Teorik ve Pratik Analizi**

Yazılım mühendisliği disiplini, donanıma belirli talimatlar göndermek amacıyla kod yazma eyleminin çok ötesine geçen; sistemlerin zaman içindeki evrimini, karmaşıklığın yönetimini ve uzun vadeli sürdürülebilirliği inceleyen çok boyutlu bir bilim dalıdır. Modern bilgi işlem sistemlerinin en büyük zorluğu, bilgisayarların işlem kapasiteleri değil, bu sistemleri tasarlayan ve sürdüren insanların bilişsel kapasiteleridir. *Bilişsel Yük (Cognitive Load)*, bir yazılım geliştiricisinin belirli bir kodu okurken, anlarken ve değiştirirken çalışma belleğinde aktif olarak tutması ve işlemesi gereken toplam bilgi miktarıdır. Bir kod tabanı büyüdükçe, yapısal kurallar olmaksızın bilişsel yük eksponansiyel olarak artar ve sistem bir noktadan sonra anlaşılamaz, değiştirilemez bir yapıya dönüşür. Literatürde *Yazılım Çürümesi (Software Rot)* olarak tanımlanan bu fenomen, başlangıçta kusursuz çalışan bir yazılımın zaman içinde yapılan eklemeler ve değişiklikler sonucunda mimari bütünlüğünü kaybetmesi ve çökmeye mahkum hale gelmesi sürecini ifade eder.

Yazılım çürümesini engellemek ve bilişsel yükü optimize etmek amacıyla, bilgisayar bilimleri literatüründe evrensel tasarım prensipleri geliştirilmiştir. Geliştiriciler için kod yazarken netlik, öngörülebilirlik ve işbirliği odaklı olmak, yüksek kaliteli ve sürdürülebilir ürünler yaratmanın en temel şartıdır.1 Bu prensipler, belirli bir programlama dilinin sözdiziminden (syntax) tamamen bağımsız olup, algoritmaların ve veri yapılarının nasıl organize edilmesi gerektiğine dair soyut ve kavramsal bir çerçeve sunar. Bir yazılım mimarisinin kalitesi, sadece derlenip çalışmasıyla değil; değişime ne kadar açık olduğu, ne kadar az hata barındırdığı ve yeni mühendisler tarafından ne kadar hızlı anlaşılabildiği ile ölçülür.2

Bu araştırma raporu, yazılım mimarisinin en temel yapı taşları olarak kabul edilen DRY (Don't Repeat Yourself), KISS (Keep It Simple, Stupid) ve YAGNI (You Aren't Gonna Need It) prensiplerini akademik ve pratik boyutlarıyla derinlemesine incelemektedir. Bu kavramların içselleştirilmesi, sağlam, ölçeklenebilir ve teknik borçtan arındırılmış yazılım sistemleri inşa etmenin ön koşuludur. Rapor kapsamında her bir prensip; teorik temelleri, kavramsal analojileri, anti-örüntü (kusurlu tasarım) örnekleri, yapısal hata analizleri ve en iyi uygulama (best practice) yöntemleri bağlamında detaylandırılmıştır.

## ---

**DRY (Don't Repeat Yourself)**

### **Teorik Tanım**

DRY (Kendini Tekrar Etme) prensibi, bir yazılım sistemi içindeki iş mantığının, kavramsal bilginin veya kuralların mükerrer bir biçimde yazılmasını kesin olarak reddeden ve sistemin her bir parçasının tek bir merkezden yönetilmesini savunan temel bir mühendislik kuralıdır.4 Bu prensip, ilk kez 1999 yılında yazılım mühendisleri Andy Hunt ve Dave Thomas tarafından kaleme alınan *The Pragmatic Programmer* (Pragmatik Programcı) adlı başyapıtta formüle edilmiş ve literatüre kazandırılmıştır.2 İlgili eserde DRY prensibinin resmi ve akademik tanımı şu şekilde ifade edilmektedir: "Sistem içindeki her bir bilgi parçasının tek, belirsiz olmayan ve yetkili (otoriter) bir temsili olmalıdır".5

Bu tanımda geçen *Bilgi (Knowledge)* kavramının doğru anlaşılması, prensibin temel felsefesini kavramak açısından son derece kritiktir. Yazılım bağlamında bilgi, sadece birbirine benzeyen kod satırları anlamına gelmez; aynı zamanda uygulamanın iş etki alanındaki (business domain) belirli bir iş kuralını, bir sistem algoritmasını veya yapısal bir kararı temsil eder.5 DRY prensibinin temel amacı, *Tek Doğru Kaynağı (Single Source of Truth)* yaratmaktır.6 Tek Doğru Kaynağı, bir sistemde belirli bir verinin veya kurallar bütününün yalnızca tek bir otoriter merkezden tanımlanması ve diğer tüm sistem bileşenlerinin bu merkeze referans vermesi ilkesidir.

DRY prensibinin teorik çerçevesi, Bertrand Meyer tarafından Eiffel programlama dilinin tasarımı sırasında ortaya atılan *Tek Seçim Prensibi (Single Choice Principle)* ile de yakından ilişkilidir.9 Tek Seçim Prensibi, bir yazılım sisteminin bir dizi alternatifi desteklemesi gerektiğinde, bu alternatiflerin tam listesini sistemde yalnızca bir ve sadece bir modülün bilmesi gerektiğini belirtir.9 Tüm bu teorik yaklaşımların ortak paydası, sistemde yapılacak herhangi bir mantıksal değişikliğin yalnızca tek bir noktada gerçekleştirilmesini sağlayarak bakım maliyetlerini minimize etmektir. DRY ilkesi sadece kaynak koda indirgenemez; veri tabanı şemaları, test senaryoları, dokümantasyon ve derleme sistemleri de dahil olmak üzere sistemin tüm bilgi temsillerini kapsar.5

### **Kavramsal Analoji**

DRY prensibinin önemini kavramak için, bir ülkenin vatandaşlık ve kamu hizmetleri kayıt sistemindeki bürokratik işleyiş incelenebilir. Geleneksel ve merkezi olmayan bir bürokraside, bir vatandaşın ikametgah adresini değiştirmesi gerektiğinde; vergi dairesine, sağlık bakanlığına, ulaşım müdürlüğüne ve nüfus idaresine ayrı ayrı giderek aynı adresi dört farklı basılı forma yazması gerekir. Bu yaklaşım, bilginin gereksiz yere tekrarlandığı kusurlu bir sistemdir. Vatandaş, bir sonraki taşınmasında kurumlardan sadece birine haber vermeyi unutursa, devletin elindeki veriler birbirleriyle çelişmeye başlar ve sistemin bütünlüğü çöker.

Buna karşın, devletin modern ve merkezi bir "Merkezi Nüfus Veritabanı" kurduğunu varsayalım. Bu mimaride adres bilgisi sadece bu merkezde yetkili bir biçimde tutulur. Diğer tüm kamu kurumları (sağlık, vergi, ulaşım) vatandaşın adres bilgisini doğrudan bu merkezi sistemden referans alarak okur. Adres değiştiğinde, sadece merkezdeki tek bir otoriter kayıt güncellenir ve diğer tüm kurumlar anında güncel ve doğru bilgiye ulaşır. Yazılım mühendisliğindeki DRY prensibi, kod tabanında tam olarak bu merkezi ve otoriter yapıyı kurmayı hedefler.

### **Kusurlu Tasarım**

Aşağıdaki sözde kod (pseudocode), bir e-ticaret platformunda KDV (Katma Değer Vergisi) hesaplama ve sipariş işleme mantığının DRY prensibi ihlal edilerek sistemin çeşitli modüllerine nasıl kopyalandığını göstermektedir. Bu yaklaşım literatürde *WET (Write Everything Twice)* veya "Her Şeyi İki Kez Yaz" olarak bilinen anti-örüntüdür.2 Anti-örüntü (Anti-Pattern), ilk bakışta mantıklı görünen ancak uzun vadede sisteme kesin olarak zarar veren ve kaçınılması gereken yapısal tasarım hatalarıdır.

// Kusurlu Tasarım: WET (Write Everything Twice) Yaklaşımı ve Bilgi Tekrarı

Fonksiyon FaturaOlustur(urunFiyati):

// Vergi oranı %18 olarak bu fonksiyona sabitlenmiş (Hardcoded)

vergiMiktari \= urunFiyati \* 0.18

toplamTutar \= urunFiyati \+ vergiMiktari

VeritabaninaKaydet("Fatura Tutarı: " \+ toplamTutar)

Fonksiyon UrunIadeIslemiYap(urunFiyati):

// Aynı vergi hesaplama mantığı iade modülünde de tekrarlanmış

iadeVergisi \= urunFiyati \* 0.18

iadeTutari \= urunFiyati \+ iadeVergisi

VeritabaninaKaydet("İade Edilecek Tutar: " \+ iadeTutari)

Fonksiyon SepetOnizlemeGoster(urunFiyati):

// Kullanıcı arayüzüne gönderilecek veri için mantık üçüncü kez yazılmış

tahminiVergi \= urunFiyati \* 0.18

EkranaYazdir("Tahmini Vergi: " \+ tahminiVergi)

### **Hata Analizi**

Yukarıdaki tasarım, *Mantıksal Dağılma (Logical Dispersion)* adı verilen son derece tehlikeli bir mimari kusur içermektedir. Mantıksal Dağılma, aynı iş alanına ait olan ve beraber değişmesi gereken kuralların sistemin farklı, birbiriyle bağlantısız modüllerine saçılması durumudur. WET kodlama standardının tercih edilmesi, projeyi sürdürülemez bir çıkmaza sürükler. Bu kusurlu tasarımın doğuracağı sonuçlar aşağıda yapısal olarak incelenmiştir:

| Hata Türü / Risk | Analiz ve Sistemsel Sonuçları |
| :---- | :---- |
| **Yüksek Bakım Maliyeti** | İlgili vergi otoritesinin oranı %18'den %20'ye çıkardığı senaryoda, geliştiricinin FaturaOlustur, UrunIadeIslemiYap ve SepetOnizlemeGoster fonksiyonlarının hepsini sistemin devasa kod tabanı içinde tek tek bulup değiştirmesi gerekecektir.4 Bu durum efor israfına yol açar. |
| **Senkronizasyon Kaybı ve Çelişki** | İnsan hatası doğası gereği, geliştirici yüzlerce dosya arasında SepetOnizlemeGoster fonksiyonundaki güncellemeyi gözden kaçırabilir.1 Bu durumda, kullanıcıya gösterilen vergi %18 iken, faturaya yansıyan vergi %20 olacak; sistem hukuki ve finansal olarak çökecektir. |
| **Test Edilebilirlik Zorluğu** | Aynı mantık üç farklı yerde bulunduğu için, yazılım test uzmanlarının (veya otomatik test araçlarının) bu mantığın doğruluğunu üç farklı senaryo için ayrı ayrı test etmesi gerekir.5 DRY prensibi ihlali, test yükünü katlayarak artırır. |
| **Kavramsal Otorite Eksikliği** | Vergi oranının hangi değere sahip olduğu konusunda sistemde bir otorite (Tek Doğru Kaynağı) yoktur. Veri, fonksiyonların içine gömülmüş gizli bir detay haline gelmiştir.12 |

DRY prensibinin ihlali, yazılım ekibinin güvenini zedeler. Geliştiriciler, kod tabanının bir yerinde yaptıkları değişikliğin, sistemin bilinmeyen başka bir köşesinde sistemi bozup bozmayacağından sürekli şüphe duyarlar ve bu durum geliştirme hızını felç eder.

### **Doğru Tasarım**

DRY prensibinin doğru bir şekilde uygulanabilmesi için geliştiricilerin *Soyutlama (Abstraction)* ve *Kapsülleme (Encapsulation)* tekniklerini ustalıkla kullanması gerekir.10 Soyutlama, bir sistemdeki karmaşık ayrıntıların gizlenerek sadece ilgili işlevin dışarıya sunulmasıdır. Kapsülleme ise, verinin ve o veriyi işleyen mantığın belirli bir modül içine hapsedilerek dış müdahalelerden korunmasıdır. Aşağıdaki ideal tasarımda, tekrarlanan "bilgi", tek bir otoriter merkeze toplanmıştır.4

// Doğru Tasarım: DRY Yaklaşımı ve Tek Doğru Kaynağı (Single Source of Truth)

// Sistemin genel yapılandırmasında otoriter bir sabit belirleniyor

Sabit Deger VERGI\_ORANI \= 0.18

// Soyutlanmış, merkezi ve tek hesaplama modülü

Fonksiyon VergiHesapla(fiyat):

Döndür fiyat \* VERGI\_ORANI

// Diğer tüm fonksiyonlar hesaplama yapmak yerine bu merkezi modülü çağırıyor

Fonksiyon FaturaOlustur(urunFiyati):

toplamTutar \= urunFiyati \+ VergiHesapla(urunFiyati)

VeritabaninaKaydet("Fatura Tutarı: " \+ toplamTutar)

Fonksiyon UrunIadeIslemiYap(urunFiyati):

iadeTutari \= urunFiyati \+ VergiHesapla(urunFiyati)

VeritabaninaKaydet("İade Edilecek Tutar: " \+ iadeTutari)

Fonksiyon SepetOnizlemeGoster(urunFiyati):

EkranaYazdir("Tahmini Vergi: " \+ VergiHesapla(urunFiyati))

Bu yapılandırma ile, kod tabanı değişime karşı esnek ve modüler bir hale getirilmiştir.4 Yeni vergi kuralları geldiğinde veya oran değiştiğinde, sadece VergiHesapla fonksiyonuna veya VERGI\_ORANI sabitine müdahale etmek tüm sistemin anında ve hatasız bir biçimde güncellenmesini sağlar.1

Ancak literatür, DRY prensibinin körü körüne uygulanmasına karşı da kesin uyarılar barındırır. Yazılım uzmanı Sandi Metz'in "Yanlış soyutlama, kopyalamadan (duplikasyon) çok daha maliyetlidir" şeklindeki ünlü tespiti, bu konudaki en önemli akademik sınırlamalardan biridir.5 Eğer iki farklı modüldeki kod satırları sadece tesadüfen birbirine benziyorsa (sözdizimsel benzerlik), ancak tamamen farklı iş kurallarını (farklı bilgileri) temsil ediyorsa, bunları zorla tek bir fonksiyonda birleştirmek *Yanlış Soyutlama (Wrong Abstraction)* yaratır.5 Bu gibi durumlarda, *Üç Kuralı (Rule of Three)* metodolojisi önerilmektedir.2 Üç Kuralı, bir kod deseninin iki kez yazılmasına tahammül edilebileceğini, ancak aynı desen üçüncü kez ortaya çıktığında mutlaka soyutlanarak yeniden düzenlenmesi gerektiğini savunan pratik bir rehberdir.2

## ---

**KISS (Keep It Simple, Stupid)**

### **Teorik Tanım**

KISS prensibi, orijinal açılımı "Keep It Simple, Stupid" (Basit Tut, Aptal) olan ve literatürde sıklıkla "Keep It Short and Simple" (Kısa ve Basit Tut) veya "Keep It Super Simple" (Süper Basit Tut) olarak da anılan, mühendislik ve tasarım süreçlerinde sadeliği en üst düzey ideal olarak konumlandıran evrensel bir ilkedir.3 Bu ilkenin temel felsefesi, sistemlerin karmaşıklaştıkça değil, basit tutuldukça daha iyi, daha güvenilir ve daha verimli çalıştığını savunmasıdır.3 Yazılım geliştirme bağlamında KISS prensibi; bir çözümün fonksiyonel gereksinimleri eksiksiz karşılarken, aynı zamanda okunabilirliğinin, anlaşılabilirliğinin ve bakımının yapısal karmaşıklığa kurban edilmemesini şart koşar.3

Bu prensibin kökenleri 1960'lı yıllara, Amerika Birleşik Devletleri Donanması'na ve Lockheed şirketinin efsanevi baş mühendisi Kelly Johnson'a dayanmaktadır.14 Johnson, mühendis ekibine tasarladıkları yüksek teknolojili savaş uçaklarının (örneğin SR-71 Blackbird), savaş alanındaki aşırı stres koşulları altında sıradan bir tamirci tarafından sadece temel el aletleri kullanılarak onarılabilecek kadar basit olması gerektiğini vurgulamıştır.14 İfade içindeki "aptal" (stupid) kelimesi, mühendislerin zekasına yönelik bir hakaret değil; sistemlerin nasıl bozulduğu ile onları onarmak için gereken uzmanlık seviyesi arasındaki ilişkiye dikkat çeken askeri bir jargondur.14 Yazılımda da durum tamamen aynıdır; bir sistem gece yarısı kritik bir üretim hatası (production bug) verdiğinde, geliştiricinin o stres altında karmaşık hiyerarşileri çözmek yerine doğrudan hatanın kaynağına ulaşabilmesi gerekir.

KISS prensibi, yazılım sistemlerinin yaşamsal özelliklerinden olan *Sürdürülebilirlik (Maintainability)* ve *Ölçeklenebilirlik (Scalability)* hedeflerine ulaşmak için vazgeçilmezdir.3 Basit tasarımlar, yeni özelliklerin mevcut yapıyı bozmadan eklenebilmesine olanak tanır ve hesaplama performansını artırır.3 Ancak basitlik, "eksiklik" veya "ilkel olmak" anlamına gelmez. Gerçek mühendislik dehası, karmaşık sorunları, son derece zarif ve anlaşılır mimarilerle çözebilme yeteneğinde yatar.3

### **Kavramsal Analoji**

KISS prensibinin uygulanmadığı bir senaryoyu kavramak için, bir muharebe sahasında arızalanan iki farklı zırhlı aracı düşünebiliriz. Birinci araç, devasa bir mühendislik harikasıdır; motoru yönetmek için onlarca mikroçip, hidrolik basınç algılayıcıları ve bilgisayar kontrollü sıvı soğutma sistemlerine sahiptir. Savaşın ortasında, bu karmaşık ağdaki tek bir sensör tozlandığında veya kablo koptuğunda, araç tamamen durur. Askeri teknisyenin bu sistemi onarabilmesi için temiz bir laboratuvar ortamına, teşhis bilgisayarlarına ve saatlerce zamana ihtiyacı vardır.

İkinci araç ise tamamen mekanik esaslara göre, KISS prensibi gözetilerek tasarlanmıştır. Ateşleme sistemi doğrudan kablolarla motora bağlıdır, bilgisayar çipleri veya hassas sensörleri yoktur. Araç sahada arızalandığında, teknisyen sorunun nereden kaynaklandığını motorun kapağını açtığı an görebilir ve standart bir İngiliz anahtarı ile dakikalar içinde tamir edip aracı savaşa döndürebilir. Yazılım sistemleri de savaş alanındaki bu araçlara benzer. Gece saat 03:00'te sistem çöktüğünde, arızayı gidermeye çalışan geliştiricinin ihtiyacı olan şey, onlarca katman ve soyutlama arkasına gizlenmiş "mükemmel" tasarımlar değil, hatanın nerede olduğunu anında gösteren şeffaf ve "basit" bir kod yapısıdır.

### **Kusurlu Tasarım**

Aşağıdaki sözde kod, bir yazılım sisteminde kullanıcının yaşının 18'den büyük olup olmadığını kontrol eden son derece temel bir mantıksal doğrulamanın, *Aşırı Mühendislik (Over-Engineering)* hastalığına yakalanarak nasıl devasa bir mimari soruna dönüştürüldüğünü sergilemektedir.3 Aşırı Mühendislik, bir problemi çözmek için gereğinden fazla esnek, aşırı soyutlanmış ve mevcut gereksinimlerin çok ötesinde karmaşık yapılar inşa etme eğilimidir.3

// Kusurlu Tasarım: Aşırı Mühendislik (Over-Engineering) ve KISS İhlali

// Tek bir işlem için gereksiz arayüz (Interface) tanımlaması

Arayüz IValidationRule:

Fonksiyon Validate(veri)

// Basit bir if/else bloğu yerine bütün bir sınıf (Class) yaratılması

Sinif AgeValidationRule Uygular IValidationRule:

Fonksiyon Validate(veri):

Eğer veri.yas \>= 18 ise

Döndür Doğru

Yoksa

Döndür Yanlış

// Doğrulayıcı sınıfı oluşturmak için bir Üretici Fabrika (Factory) kullanılması

Sinif ValidationManagerFactory:

Fonksiyon GetAgeValidator():

Döndür Yeni AgeValidationRule()

// Uygulamanın asıl iş mantığının karmaşıklığa boğulması

Fonksiyon KullaniciGirisiniKontrolEt(kullanici):

fabrika \= Yeni ValidationManagerFactory()

dogrulayici \= fabrika.GetAgeValidator()

Eğer dogrulayici.Validate(kullanici) \== Doğru ise:  
    EkranaYazdir("Sisteme Giriş Başarılı")  
Yoksa:  
    EkranaYazdir("Yaş Sınırı İhlali")

### **Hata Analizi**

Yukarıdaki kusurlu örnek, teknik olarak beklendiği gibi çalışır ve doğru sonucu verir. Ancak mimari perspektiften değerlendirildiğinde, ortaya çıkan yapı literatürde *Lasagna Kodu (Lasagna Code)* olarak adlandırılan, katmanların birbiri üzerine gereksiz yere bindirildiği ve anlaşılırlığın tamamen yok edildiği bir çöküş örneğidir.6 Bu yapının barındırdığı mühendislik hataları ve yol açacağı uzun vadeli problemler şu şekilde analiz edilebilir 3:

| Over-Engineering (Aşırı Mühendislik) Sorunu | Sisteme Yönelik Yıkıcı Etkileri |
| :---- | :---- |
| **Gereksiz Katmanlaşma** | Basit bir yas \>= 18 operatör kontrolü için fabrikalar ve arayüzler yaratılmıştır. Bu durum, problemi çözmekten ziyade, geliştiricinin tasarım örüntülerini (Design Patterns) zorla kullanma çabasından kaynaklanır. 3 |
| **Artan Bilişsel Yük** | Kod tabanına yeni katılan (onboarding) bir mühendis, sadece bir yaş kuralının nerede hesaplandığını bulmak için üç farklı dosya, sınıf ve arayüz arasında gezinmek zorunda bırakılır. |
| **Hata Ayıklama (Debugging) Kördüğümü** | Sistem çalışma anında bir hata verdiğinde, hatanın izini sürmek (stack trace) felakete dönüşür. Hata mesajı, asıl mantığın bulunduğu satırı işaret etmek yerine, arayüzler ve fabrikalar arasında kaybolur.3 |
| **Performans ve Bellek İsrafı** | Sadece basit bir kontrol için bellekte (RAM) fabrika sınıfları örneklenir (instantiation), arayüz referansları tutulur ve işlemci gereksiz nesne yönelimli yüklerin altına sokulur.3 |

Bazı geliştiriciler, yazılım prensiplerini ve mimari kalıpları (örneğin Fabrika Kalıbı) yanlış yorumlayarak, ne kadar çok katman kurarlarsa kodlarının o kadar "kaliteli" görüneceği yanılgısına düşerler.3 Oysa profesyonel yazılım mühendisliğinde kodun kalitesi karmaşıklığıyla değil, okunabilirliğiyle ölçülür.

### **Doğru Tasarım**

Aynı gereksinimin, KISS prensibinin sunduğu sadelik ve doğrudanlık ile hiçbir soyutlama karmaşasına girmeden çözülmüş ideal versiyonu aşağıdadır. KISS prensibini uygulamak için; temel hedeflerin belirlenmesi, esaslara odaklanılması ve karmaşık tasarımların kasıtlı olarak ortadan kaldırılması gerekir.3

// Doğru Tasarım: KISS (Keep It Simple, Stupid) Yaklaşımı ve Sadelik

// Yaş kontrolü için tek ve doğrudan görev yapan açık bir fonksiyon

Fonksiyon ResitMi(yas):

Döndür yas \>= 18

// Sistemin kullanımı: Fabrikalar veya arayüzler yok, sadece saf iş mantığı

Fonksiyon KullaniciGirisiniKontrolEt(kullanici):

Eğer ResitMi(kullanici.yas) ise:

EkranaYazdir("Sisteme Giriş Başarılı")

Yoksa:

EkranaYazdir("Yaş Sınırı İhlali")

Bu doğru tasarım, isminin ve içerdiği mantığın öngördüğü şeyi tamamen şeffaf bir şekilde yerine getirir.17 Karmaşıklıktan arındırılmış bu kod, herhangi bir geliştirici tarafından saniyeler içinde okunabilir, çok daha hızlı derlenip çalışır ve bir hata oluştuğunda sorunun tam olarak nerede (satır Döndür yas \>= 18\) olduğu anında tespit edilebilir.3 KISS prensibi, "en iyi kod, hiç yazılmayan koddur" felsefesini destekleyerek mühendisleri gereksiz kod üretiminden alıkoyar.3

## ---

**YAGNI (You Aren't Gonna Need It)**

### **Teorik Tanım**

YAGNI, Türkçeye "Buna İhtiyacın Olmayacak" olarak çevrilebilen ve yazılım geliştirme süreçlerinde gelecekteki potansiyel ihtiyaçlara göre "varsayımsal" kod yazılmasını kesin bir dille reddeden köklü bir tasarım prensibidir.10 Bu ilke, 1990'lı yılların sonlarında yazılım dünyasını geleneksel şelale (waterfall) modellerinden kurtaran *Çevik (Agile)* metodolojilerin ve spesifik olarak *Ekstrem Programlama (Extreme Programming \- XP)* pratiğinin kalbinde yer alır.10 Ekstrem programlamanın kurucuları Kent Beck, Ron Jeffries ve Chet Hendrickson tarafından "C3 Projesi" (Chrysler Comprehensive Compensation System) sırasında literatüre kazandırılmış olan YAGNI, geliştirme ekiplerinin "yalnızca mevcut iterasyonda mutabık kalınan kapsamı zamanında teslim etmeye" odaklanmasını zorunlu kılar.10

Yazılım projelerinde mühendislerin en sık düştüğü hatalardan biri, gelecekteki gereksinimleri tahmin etmeye çalışmaktır. "İleride farklı veri tabanlarına geçiş yapabiliriz", "Müşteri henüz istemedi ama gelecekte XML yerine JSON desteği de bekleyebilir", "Altı ay sonra bu modülü başka bir şirkete de satarız" gibi düşünceler, literatürde *Spekülatif Genellik (Speculative Generality)* olarak bilinen bir soruna yol açar.17 Spekülatif Genellik, o an için hiçbir işe yaramayan ancak gelecekte "kullanılabileceği umuduyla" sisteme entegre edilen soyutlamalar ve özelliklerdir. YAGNI prensibi bu duruma tamamen karşı çıkarak şu kuralı koyar: "Her zaman işleri sadece gerçekten ihtiyacınız olduğunda uygulayın, sadece ihtiyacınız olacağını öngördüğünüzde asla uygulamayın".17 Bir özelliğe gelecekte kesin olarak ihtiyaç duyulacağından tamamen emin olunsa dahi, o özellik hemen o an inşa edilmemelidir.17

Bu prensip, sistemin esnek ve genişlemeye açık olmamasını savunmaz.17 Tam tersine, gereksiz ve yanlış varsayımlarla doldurulmamış, yalın bir sistemin gelecekteki gerçek değişimlere çok daha hızlı ve kolay adapte olabileceğini iddia eder.17

### **Kavramsal Analoji**

YAGNI prensibini içselleştirmek için, dağlık bir bölgeye yürüyüş (trekking) yapmak üzere çantasını hazırlayan bir gezgini düşünebiliriz. Gezginin o anki somut ihtiyacı su, harita, pusula ve temel ilk yardım malzemeleridir. Ancak gezgin çantasını hazırlarken şu spekülasyonları yapmaya başlar: "Ya yolumu kaybedip bir hafta ormanda kalırsam? Yanıma fazladan on kutu konserve almalıyım. Ya karşıma bir ayı çıkarsa? Ağır bir çelik kafes de taşıyayım. Ya yürüyüş sırasında aniden bir göle rastlar ve balık tutmak istersem? Balıkçılık takımını da sırtıma yükleyeyim."

Sonuç olarak gezgin, henüz hiçbir somut tehlike veya ihtiyaç oluşmadan, sadece "ihtimal dahilinde" diye taşıması imkansız olan, yüz kiloluk bir çantayla yola çıkar. Bu ağır yük onun yürüyüşünü yavaşlatır, enerjisini tüketir ve dağın eteklerine varmadan tükenmesine neden olur. Daha da kötüsü, ne bir ayı ile karşılaşır ne de balık tutacak bir göl bulur; taşıdığı onca ağırlık tamamen israf olur. Yazılım mühendisliğinde YAGNI'nin ihlal edilmesi tam olarak budur: Henüz talep edilmemiş özelliklerin ve varsayımsal mimarilerin ağır yükünü, yazılımın kod tabanına (sırt çantasına) doldurmak ve tüm projenin geliştirme hızını yavaşlatmaktır.

### **Kusurlu Tasarım**

Sektörün otorite kabul edilen isimlerinden Martin Fowler'ın *Yagni* üzerine kaleme aldığı makalede verdiği örneğe dayanarak 18; bir yazılım ekibinin nakliye şirketleri için bir sigorta fiyatlandırma sistemi geliştirdiğini varsayalım. Müşterinin ekibe ilettiği "mevcut iterasyon gereksinimi" yalnızca gemilerin fırtınaya yakalanma riskinin (Storm Risk) hesaplanmasıdır. Ancak mühendis, 6 ay sonra şirketin "Korsan Saldırısı" (Piracy Risk) veya daha fantastik riskleri de (Meteor Çarpması) isteyebileceğini öngörerek (spekülasyon yaparak) sistemi aşağıdaki gibi tasarlar:

// Kusurlu Tasarım: Spekülatif Genellik ve YAGNI İhlali

Arayüz IRiskHesaplayici:

Fonksiyon FiyatHesapla()

// İstenilen Gerçek İhtiyaç

Sinif FirtinaRiski Uygular IRiskHesaplayici:

Fonksiyon FiyatHesapla():

Döndür 1500

// Spekülasyon 1: "İleride müşteri kesin korsan saldırısı sigortası da isteyecek"

Sinif KorsanSaldirisiRiski Uygular IRiskHesaplayici:

Fonksiyon FiyatHesapla():

// Bu kod şu an hiçbir yerde kullanılmıyor, tamamen ölü kod (Dead Code).

// Müşterinin korsan riskini nasıl hesaplamak isteyeceği henüz bilinmiyor.

Döndür 8000

// Spekülasyon 2: "Sistemi tam esnek yapalım, meteor ihtimalini bile ekleyelim"

Sinif MeteorCarpmasiRiski Uygular IRiskHesaplayici:

Fonksiyon FiyatHesapla():

// Sistemin kalitesini ve hızını düşüren yığınlar.

Döndür 50000

// Sigorta modülünün ana şalteri

Fonksiyon SigortaFiyatiBelirle(riskTipi):

Eğer riskTipi \== "Firtina" ise Döndür Yeni FirtinaRiski().FiyatHesapla()

Eğer riskTipi \== "Korsan" ise Döndür Yeni KorsanSaldirisiRiski().FiyatHesapla()

Eğer riskTipi \== "Meteor" ise Döndür Yeni MeteorCarpmasiRiski().FiyatHesapla()

### **Hata Analizi**

Yukarıdaki kod, mühendisin gözüne oldukça "esnek ve geleceğe hazır" görünebilir. Ancak YAGNI prensibine göre bu yaklaşım, yazılımın yaşam döngüsüne vurulmuş büyük bir darbedir.17 Varsayımlara dayalı özellikler geliştirmek sistemleri yönetilmesi zor bir duruma sokar.19 Bu spekülatif geliştirmenin zararları aşağıdaki tabloda detaylandırılmıştır:

| YAGNI İhlali Sonuçları | Mühendislik ve İşletme Analizi |
| :---- | :---- |
| **Fırsat Maliyeti (Opportunity Cost)** | Geliştiricinin korsan ve meteor risklerini kurgulamak, yazmak, derlemek ve test etmek için harcadığı zaman, müşterinin *şu an* acilen beklediği satış modülünün gecikmesine sebep olmuştur.18 Müşteriye anında değer üretmek (Time Savings) yerine, hayali özelliklere zaman harcanmıştır.1 |
| **Ölü Kod (Dead Code) Yığılması** | Sisteme eklenen spekülatif kodların çoğu hiçbir zaman gerçeğe dönüşmez.10 Hiç çalıştırılmayan ancak sistemde yer kaplayan, okunması ve bakımının yapılması gereken kodlar *Ölü Kod* olarak kod tabanını kirletir.3 |
| **Yanlış Tahminlerin Maliyeti** | Altı ay sonra müşteri gerçekten korsan saldırısı riski modülünü istediğinde, büyük ihtimalle hesaplamanın sadece Döndür 8000 kadar basit olmayacağını, mürettebat sayısına ve rotaya göre değişen karmaşık bir algoritma beklediğini söyleyecektir.17 Mühendisin önceden yazdığı kod çöpe gidecek, baştan yazmak zorunda kalacaktır.6 |
| **Teknik Borç (Technical Debt)** | Sistemdeki her satır kod, bakım gerektiren bir yüktür. Kullanılmayan karmaşıklıklar, ileride yapılacak gerçek değişiklikleri zorlaştırarak teknik borç oluşturur.3 |

YAGNI ilkesinin terk edilmesi, yazılım ekibini "müşterinin ne istediğini ondan daha iyi bildiği" yanılgısına sürükler. Oysa yazılımda müşterinin gerçek ihtiyaçları, projenin canlıya çıkmasıyla ve zamanla netleşir.

### **Doğru Tasarım**

YAGNI prensibini benimsemiş profesyonel bir yazılım mimarı, aynı sistemi varsayımlardan tamamen arındırarak, yalnızca eldeki doğrulanmış gereksinimlere (sadece Fırtına Riski) sadık kalarak inşa eder:

// Doğru Tasarım: YAGNI (You Aren't Gonna Need It) Odaklı Yalın Yaklaşım

// Yalnızca mevcut iterasyonda istenen somut gereksinim uygulanır.

// Arayüzler, fabrikalar veya kullanılmayan risk türleri sisteme dahil edilmez.

Fonksiyon FirtinaSigortasiHesapla():

Döndür 1500

// Doğrudan sistem kullanımı

Fonksiyon SigortaFiyatiBelirle():

Döndür FirtinaSigortasiHesapla()

Bu son derece yalın ve odaklanmış tasarım; geliştirme hızını maksimize eder, projenin müşteriye anında teslim edilmesini sağlar ve geliştiriciyi "yanlış tahminlerin" bedelini ödemekten kurtarır.1 Eğer aylar sonra müşteri gerçekten Korsan Saldırısı riskinin eklenmesini talep ederse, sistem *Fırsatçı Yeniden Düzenleme (Opportunistic Refactoring)* yöntemiyle güvenli bir şekilde dönüştürülür.13 *Yeniden Düzenleme (Refactoring)*, yazılımın dışarıdan gözlemlenebilen işlevselliğini değiştirmeden, iç mimarisinin daha modüler ve temiz hale getirilmesi sürecidir.16 İhtiyaç anı geldiğinde kod, doğal bir evrimle bir arayüz (Interface) yapısına taşınabilir. YAGNI ilkesinin özeti şudur: Problemi problem olduğu gün çöz; henüz var olmayan problemleri tasarlayarak zaman kaybetme.20

---

Yazılım geliştirme serüveninin temel yapıtaşlarını oluşturan bu ilk bölümde; DRY (Bilgiyi tek bir otoriter kaynakta topla), KISS (Tasarımda sadeliği ve okunabilirliği en üst ideal olarak koru) ve YAGNI (Sadece elindeki somut gereksinime odaklan, geleceği speküle etme) prensipleri yapısal ve teorik düzeyde incelenmiştir. Bu üç kavram, kod yazma eylemini salt bir zanaat olmaktan çıkarıp, onu öngörülebilir, sürdürülebilir ve yönetilebilir bir mühendislik disiplinine dönüştüren ilkeler bütünüdür. Bir sistemin niteliği, içindeki kod satırlarının veya soyutlamaların çokluğuyla değil; değişime uyum sağlama hızı ve insan bilişine sunduğu şeffaflıkla ölçülür. Eğitim sürecinin bir sonraki modülü, nesne yönelimli paradigmanın (Object-Oriented Programming) omurgasını oluşturan SOLID prensipleri ve spesifik Tasarım Örüntüleri (Design Patterns) üzerine kurgulanacaktır.

#### **Alıntılanan çalışmalar**

1. KISS, DRY, SOLID, YAGNI — A Simple Guide to Some Principles of Software Engineering and Clean Code | by HlfDev | Medium, erişim tarihi Nisan 25, 2026, [https://medium.com/@hlfdev/kiss-dry-solid-yagni-a-simple-guide-to-some-principles-of-software-engineering-and-clean-code-05e60233c79f](https://medium.com/@hlfdev/kiss-dry-solid-yagni-a-simple-guide-to-some-principles-of-software-engineering-and-clean-code-05e60233c79f)  
2. DRY principles: How to write efficient SQL \- dbt Labs, erişim tarihi Nisan 25, 2026, [https://www.getdbt.com/blog/dry-principles](https://www.getdbt.com/blog/dry-principles)  
3. KISS Principle in Software Development \- GeeksforGeeks, erişim tarihi Nisan 25, 2026, [https://www.geeksforgeeks.org/software-engineering/kiss-principle-in-software-development/](https://www.geeksforgeeks.org/software-engineering/kiss-principle-in-software-development/)  
4. DRY Principle in Software Development \- GeeksforGeeks, erişim tarihi Nisan 25, 2026, [https://www.geeksforgeeks.org/software-engineering/dont-repeat-yourselfdry-in-software-development/](https://www.geeksforgeeks.org/software-engineering/dont-repeat-yourselfdry-in-software-development/)  
5. The DRY Principle: Benefits and Costs with Examples, erişim tarihi Nisan 25, 2026, [https://thevaluable.dev/dry-principle-cost-benefit-example/](https://thevaluable.dev/dry-principle-cost-benefit-example/)  
6. 3 software development principles I wish I knew earlier in my career, and the power of YAGNI, KISS, and DRY \- Reddit, erişim tarihi Nisan 25, 2026, [https://www.reddit.com/r/programming/comments/1bmicj0/3\_software\_development\_principles\_i\_wish\_i\_knew/](https://www.reddit.com/r/programming/comments/1bmicj0/3_software_development_principles_i_wish_i_knew/)  
7. The DRY Principle, erişim tarihi Nisan 25, 2026, [https://radek.io/posts/dry-principle/](https://radek.io/posts/dry-principle/)  
8. Prime doesn't understand the DRY principle : r/theprimeagen \- Reddit, erişim tarihi Nisan 25, 2026, [https://www.reddit.com/r/theprimeagen/comments/1dl262w/prime\_doesnt\_understand\_the\_dry\_principle/](https://www.reddit.com/r/theprimeagen/comments/1dl262w/prime_doesnt_understand_the_dry_principle/)  
9. Don't repeat yourself \- Wikipedia, erişim tarihi Nisan 25, 2026, [https://en.wikipedia.org/wiki/Don%27t\_repeat\_yourself](https://en.wikipedia.org/wiki/Don%27t_repeat_yourself)  
10. DRY, KISS & YAGNI Principles: Guide & Benefits \- Boldare, erişim tarihi Nisan 25, 2026, [https://www.boldare.com/blog/kiss-yagni-dry-principles/](https://www.boldare.com/blog/kiss-yagni-dry-principles/)  
11. The Pragmatic Programmer, erişim tarihi Nisan 25, 2026, [https://media.pragprog.com/titles/tpp20/dry.pdf](https://media.pragprog.com/titles/tpp20/dry.pdf)  
12. DRY (Don't Repeat Yourself) Principle in Python: A Practical Guide | by Vitaly Sem \- Medium, erişim tarihi Nisan 25, 2026, [https://medium.com/@virtualik/dry-dont-repeat-yourself-principle-in-python-a-practical-guide-06290ebda0cf](https://medium.com/@virtualik/dry-dont-repeat-yourself-principle-in-python-a-practical-guide-06290ebda0cf)  
13. How the DRY Principle in Programming Prevents Duplications in AI-Generated Code, erişim tarihi Nisan 25, 2026, [https://www.faros.ai/blog/ai-generated-code-and-the-dry-principle](https://www.faros.ai/blog/ai-generated-code-and-the-dry-principle)  
14. KISS principle \- Wikipedia, erişim tarihi Nisan 25, 2026, [https://en.wikipedia.org/wiki/KISS\_principle](https://en.wikipedia.org/wiki/KISS_principle)  
15. A detailed example of the KISS principle in C \- David Omid, erişim tarihi Nisan 25, 2026, [https://www.davidomid.com/a-detailed-example-of-the-kiss-principle-in-csharp](https://www.davidomid.com/a-detailed-example-of-the-kiss-principle-in-csharp)  
16. You aren't gonna need it \- Wikipedia, erişim tarihi Nisan 25, 2026, [https://en.wikipedia.org/wiki/You\_aren%27t\_gonna\_need\_it](https://en.wikipedia.org/wiki/You_aren%27t_gonna_need_it)  
17. Software Design Principles (Basics) | DRY, YAGNI, KISS, etc \- work@tech, erişim tarihi Nisan 25, 2026, [https://workat.tech/machine-coding/tutorial/software-design-principles-dry-yagni-eytrxfhz1fla](https://workat.tech/machine-coding/tutorial/software-design-principles-dry-yagni-eytrxfhz1fla)  
18. Yagni \- Martin Fowler, erişim tarihi Nisan 25, 2026, [https://martinfowler.com/bliki/Yagni.html](https://martinfowler.com/bliki/Yagni.html)  
19. YAGNI Principle in Software Development \- GeeksforGeeks, erişim tarihi Nisan 25, 2026, [https://www.geeksforgeeks.org/software-engineering/what-is-yagni-principle-you-arent-gonna-need-it/](https://www.geeksforgeeks.org/software-engineering/what-is-yagni-principle-you-arent-gonna-need-it/)  
20. YAGNI (“You Aren't Gonna Need It,”): helps software engineers build with clarity, not clutter | by Saurabh Gupta | Medium, erişim tarihi Nisan 25, 2026, [https://medium.com/@saurabh.engg.it/yagni-you-arent-gonna-need-it-helps-software-engineers-build-with-clarity-not-clutter-02464d0b7a63](https://medium.com/@saurabh.engg.it/yagni-you-arent-gonna-need-it-helps-software-engineers-build-with-clarity-not-clutter-02464d0b7a63)
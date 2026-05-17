# Yefai IEEE Raporu

Bu klasör Yefai projesi için IEEEtran conference formatında hazırlanmış LaTeX rapor çıktısını içerir.

## Dosyalar

- `yefai_ieee_report.tex` — ana rapor dosyası
- `references.bib` — BibTeX kaynakları
- `README.md` — derleme notları

## Derleme

Bu klasörde çalıştır:

```bash
pdflatex yefai_ieee_report.tex
bibtex yefai_ieee_report
pdflatex yefai_ieee_report.tex
pdflatex yefai_ieee_report.tex
```

Alternatif:

```bash
latexmk -pdf yefai_ieee_report.tex
```

## Teslim Öncesi Güncellenecek Yerler

1. Yazar adı, bölüm, kurum, şehir ve e-posta/öğrenci numarası.
2. Şekil yer tutucuları gerçek ekran görüntüleri veya diyagramlarla değiştirilecekse `figure` bloklarındaki açıklamalar.
3. Ders/kurum teşekkür notu gerekiyorsa `Teşekkür` bölümü.
4. Eğer rapor İngilizce istenirse metin çevrilmeli ve `babel` dili güncellenmelidir.

## Notlar

- Rapor gövdesinde kaynak kod, dosya yolu veya uygulama içi tanımlayıcı kullanılmaması hedeflendi.
- Şekiller bilinçli olarak yer tutucu bırakıldı; skill kuralı gereği gerçek görsel üretilmedi veya gömülmedi.
- Gereksinim kapsamı `.planning` belgeleri ve mevcut arka uç davranışlarıyla hizalandı.

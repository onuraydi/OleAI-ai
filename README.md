# OleAI Engine
OleAI Engine, akıllı yemek tarifleri ve kiler (pantry) yönetimi için geliştirilmiş yapay zeka (AI) tabanlı bir öneri sistemidir. Doğal Dil İşleme (NLP) yetenekleriyle kullanıcıların zevklerini analiz ederken, yapısal (structured) malzeme takibi ile kullanıcının elindeki ürünlere en uygun tarifleri filtreler ve puanlar.
## 🚀 Teknolojiler
- **FastAPI**: Yüksek performanslı ve asenkron REST API altyapısı.
- **Scikit-Learn (TF-IDF & Cosine Similarity)**: Yemek tariflerinin içerikleri, başlıkları ve kategorileri üzerinden NLP destekli metin analizi ve benzerlik skorlaması.
- **Pydantic**: Güçlü ve güvenli veri doğrulama (validation) süreçleri.
- **Pytest**: Gelişmiş test ve yüksek kod kapsamı (coverage) güvencesi.
## 🧠 Nasıl Çalışır? (Hibrit Öneri Modeli)
Model, en ideal yemek tarifini bulmak için sadece eldeki malzemeleri saymaz; aynı zamanda zevklere, alışkanlıklara ve pratikliğe göre çok yönlü bir algoritma (Hybrid Evaluation) çalıştırır:
1. **Malzeme Eşleştirme (Structured Fulfillment):** Kullanıcının kilerinde bulunan malzemeler, gramajına ve sıvı/katı birim ölçülerine (kg, g, l, ml, vb.) göre dönüştürülüp hesaplanarak tarifteki gereksinimlerle eşleştirilir.
2. **NLP ile Tat Benzerliği (Taste Similarity):** Kullanıcının geçmişteki etkileşimleri (kaydetme, beğenme, geçme) "zamana bağlı zayıflama (time decay)" algoritmasıyla incelenir. Etkileşimler NLP vektörlerine yansıtılarak Cosine Similarity (Kosinüs Benzerliği) metodu ile en uygun lezzet profili çıkarılır.
3. **Dinamik Modlar:** Kullanıcının anlık ihtiyacına göre öneri algoritmasının ağırlıkları değiştirilir.
### 🎯 Öneri Modları (Recommendation Modes)
Sistem farklı kullanıcı senaryolarına anında adapte olabilen farklı öneri modlarına sahiptir:
- **`DEFAULT`**: Kilerdeki malzeme uyumluluğu (%50) ile kullanıcının lezzet tercihini (%50) eşit ağırlıkta tutar.
- **`STRICT`**: Katı mod. Tarifteki malzemelerin en az %90'ı kullanıcının kilerinde olmalıdır. Eksik malzeme kabul etmez, tamamen evdeki imkanlara odaklanır.
- **`FOR_YOU`**: Kişiselleştirme odaklı. Evde malzeme eksik olsa bile, kullanıcının daha önceki favorilerine en çok benzeyen (%80 NLP ağırlığı) lezzetleri öne çıkarır.
- **`QUICK`**: Hızlı ve pratik. Hazırlık ve pişirme süresi toplam 45 dakikayı geçen tüm tarifleri otomatik olarak eler.
- **`EXPLORE`**: Keşfet modu. Klasikleşmiş yüksek popüler tarifler yerine, kullanıcının daha önce çok karşılaşmadığı farklı tarifleri öne çıkarır.
- **`MINIMAL`**: Az malzeme ile çok iş. Kilerdeki eşleşme oranı en az %60 olmalıdır.
- **`ULTIMATE`**: Gurme deneyimi. Mükemmele en yakın, hem lezzet skoru yüksek hem de malzemenin %70'ten fazlasının bulunduğu elit tarif önerileri sunar.
### ♻️ Ekstra Puanlamalar
- **Zero Waste (Sıfır Atık) Boost:** Kilerdeki tarihi geçmek üzere olan (son 3 gün) malzemeleri içeren tarifler ekstra bonus puanı (+%20) kazanır ve en üst sıraya yerleşir.
- **New Recipe Boost:** Sisteme son 7 gün içerisinde eklenmiş yeni tarifler desteklenerek daha sık gösterilir.
## 📡 API Uç Noktaları (Endpoints)
Tüm isteklerde `X-API-Key` başlığı (header) ile yetkilendirme yapılmalıdır.
- `GET /health` : Sistemin ve modelin durumunu (sağlıklı olup olmadığını, en son ne zaman güncellendiğini ve modeldeki tarif sayısını) döner.
- `POST /api/v1/recommendations` : Kullanıcının kiler bilgisini (`pantryItems`), arama metnini, etkileşimlerini ve uygulanacak modu alır; en ideal `top_k` tarifi sırasıyla ve skoruyla birlikte döndürür.
- `POST /api/v1/recipes/sync` : Sisteme yeni bir tarif eklendiğinde, AI modeline bunu anlık olarak öğretir ve vektörleri günceller. (Gerçek zamanlı öğrenme)
## 🛠️ Kurulum ve Çalıştırma
**Gereksinimler:**
- Python 3.10+
**Bağımlılıkların Yüklenmesi:**
```bash
pip install -r requirements.txt
```
**Uygulamanın Başlatılması:**
```bash
uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload
```
**Testlerin Çalıştırılması:**
```bash
# Sadece testleri çalıştırmak için
pytest
# Testleri çalıştırıp kod kapsamı (coverage) raporu almak için
pytest --cov=src --cov-report=term-missing
```
OleAI Engine, sürekli güncellenen ve gerçek zamanlı öğrenme destekleyen altyapısıyla kullanıcılarına en akıllı yemek deneyimini sunmak üzere tasarlanmıştır.

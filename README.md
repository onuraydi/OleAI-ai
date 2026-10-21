<div align="center">

# OleAI Engine 🧠🍲

**🌐 Language / Dil:** &nbsp; [🇬🇧 English](#en) &nbsp;|&nbsp; [🇹🇷 Türkçe](#tr)

</div>

---

<a id="en"></a>

> 🇹🇷 Türkçe okumak için: **[Türkçe sürüme git ↓](#tr)**

OleAI Engine is an artificial intelligence (AI) based recommendation system developed for smart recipes and pantry management. It analyzes users' taste preferences with Natural Language Processing (NLP) methods, and filters and scores recipes that match the ingredients the user has on hand through structured ingredient tracking.

The system is designed to deliver personalized recommendations by evaluating user interactions and recipe data.

## Tech Stack

- **Framework:** Python 3.10+, FastAPI
- **AI and data processing:** Scikit-learn (TF-IDF and Cosine Similarity), Pandas
- **Data validation:** Pydantic
- **Security:** `X-API-Key` based API access control
- **DevOps and code quality:** Docker, GitHub Actions (CI/CD), SonarQube
- **Testing:** Pytest

## How Does It Work? — Hybrid Recommendation Model

OleAI Engine does not rank recipes solely by the number of available ingredients. It uses a hybrid scoring approach that evaluates ingredient compatibility, user preferences, and the practicality of the recipe together.

### 1. Ingredient matching (Structured Fulfillment)

The ingredients in the user's pantry are compared against recipe requirements using the supported weight and volume units (e.g., kg, g, l, ml). This helps calculate how much of a recipe's ingredients are available.

> Unit conversions and quantity comparisons are limited to the units and data model supported by the application.

### 2. Taste similarity with NLP (Taste Similarity)

A preference profile is built by evaluating the user's past interactions, such as saving, liking, or skipping. A time decay approach allows more recent interactions to contribute more to the preference profile.

Recipe texts are vectorized with TF-IDF, and their similarity to the user's preferences is calculated using Cosine Similarity.

### 3. Dynamic recommendation modes

Different filters and scoring weights are applied depending on the user's needs.

## Recommendation Modes

- **`DEFAULT`:** Pantry ingredient compatibility and taste preference are weighted equally (50% / 50%).
- **`STRICT`:** Requires at least 90% of the recipe's ingredients to be present in the user's pantry. Tolerance for missing ingredients depends on the application's relevant filtering rules.
- **`FOR_YOU`:** Prioritizes personalization. Taste similarity is weighted at 80%; missing pantry ingredients alone may not exclude a recipe.
- **`QUICK`:** Eliminates recipes whose combined preparation and cooking time exceeds 45 minutes.
- **`EXPLORE`:** Aims to surface recipes the user has not encountered frequently before.
- **`MINIMAL`:** Focuses on recipes that match at least 60% with the ingredients in the pantry.
- **`ULTIMATE` (Gourmet):** Highlights recipes with a high taste score and more than 70% of their ingredients available.

## Additional Scoring (Boosts)

- **Zero Waste Boost:** Recipes that use pantry ingredients with three days or less until expiration may receive extra points. In the specified configuration, this bonus is defined as `20%`.
- **New Recipe Boost:** Provides additional visibility to recipes added to the system within the last seven days, helping new recipes appear in recommendations.

> The effect of the bonuses on the final ranking depends on the scoring and ranking rules in the application.

## API Endpoints

The `X-API-Key` header must be used in requests for API access.

| Method | Endpoint | Description |
| --- | --- | --- |
| `GET` | `/health` | Reports the service's health status, the model's last update time, and the number of recipes in the model. |
| `POST` | `/api/v1/recommendations` | Takes the pantry ingredients (`pantryItems`), search text, user interactions, and recommendation mode; returns the best `top_k` recipes along with their scores. |
| `POST` | `/api/v1/recipes/sync` | Feeds new or updated recipe data into the recommendation model and updates the relevant vectors. |

## Project Structure

```text
OleAI-ai/
├── .github/
│   └── workflows/              # CI/CD workflows (ai-cd.yml, ci.yml)
├── src/
│   ├── api/                     # API endpoints and schemas (schemas.py)
│   ├── core/                    # Configuration and security (config.py, exceptions.py)
│   ├── models/                  # Recommendation models (recommender.py)
│   ├── services/                # Business logic and data preparation
│   │   ├── data_preprocessor.py
│   │   └── recipe_sync_service.py
│   └── main.py                  # Entry point of the FastAPI application
├── tests/                       # Pytest tests
├── Dockerfile                   # Container image definition
├── requirements.txt             # Python dependencies
├── sonar-project.properties     # SonarQube configuration
├── README.md
└── CONTRIBUTING.md
```

## Setup and Running

### Requirements

- Python 3.10 or higher
- Git
- Docker (only for running via Docker)

### 1. Clone the repository

```bash
git clone https://github.com/onuraydi/OleAI-ai.git
cd OleAI-ai
```

### 2. Create a virtual environment

**Windows (PowerShell):**

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

**Linux / macOS:**

```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install dependencies

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### 4. Configure environment variables

Create a `.env` file in the project root directory:

```ini
API_KEY=guclu_ve_tahmin_edilemez_bir_api_anahtari
SONAR_TOKEN=sonarqube_token_degeri
```

- Replace the `API_KEY` value with a strong, hard-to-guess value.
- `SONAR_TOKEN` is only required if a SonarQube analysis will be run.
- Do not add real secret keys to the Git repository. Make sure the `.env` file is listed in `.gitignore`.
- Review the configuration code to verify the names of the environment variables the application uses.

### 5. Start the application locally

```bash
uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload
```

You can access the API documentation at the following addresses:

- Swagger UI: <http://localhost:8000/docs>
- OpenAPI schema: <http://localhost:8000/openapi.json>

`--reload` is for development; use a suitable server configuration in production.

### 6. Run with Docker

Build the Docker image in the project root directory:

```bash
docker build -t oleai-engine .
```

Then start the container:

```bash
docker run -d \
  --name oleai-engine \
  -p 8000:8000 \
  --env-file .env \
  oleai-engine
```

To view the container logs:

```bash
docker logs -f oleai-engine
```

## Tests and Code Coverage

To run the tests:

```bash
pytest
```

To get a code coverage report in the terminal, the `pytest-cov` dependency must be installed:

```bash
pytest --cov=src --cov-report=term-missing
```

To generate an HTML report:

```bash
pytest --cov=src --cov-report=html
```

The HTML report is written to the `htmlcov/` directory.

## Security Notes

- Do not add API keys to source code, test output, or commits.
- Use HTTPS, secure secret management, and appropriate access controls in production.
- Do not treat the `X-API-Key` check alone as a comprehensive user authentication system.
- Do not expose secret configuration values or sensitive information in error responses.

## Contributing

If you would like to report a bug, make a suggestion, or contribute code, please read the development and Pull Request guidelines in [`CONTRIBUTING.md`](CONTRIBUTING.md).

<div align="right">

[⬆ Back to top](#) &nbsp;|&nbsp; [🇹🇷 Türkçe sürüme git](#tr)

</div>

---
---

<a id="tr"></a>

> 🇬🇧 To read in English: **[Go to the English version ↑](#en)**

OleAI Engine, akıllı yemek tarifleri ve kiler (pantry) yönetimi için geliştirilmiş yapay zekâ (AI) tabanlı bir öneri sistemidir. Doğal Dil İşleme (NLP) yöntemleriyle kullanıcıların lezzet tercihlerini analiz eder; yapısal malzeme takibiyle kullanıcının elindeki ürünlere uygun tarifleri filtreler ve puanlar.

Sistem, kullanıcı etkileşimlerini ve tarif verilerini değerlendirerek kişiselleştirilmiş öneriler sunmak üzere tasarlanmıştır.

## Teknoloji Yığını (Tech Stack)

- **Framework:** Python 3.10+, FastAPI
- **AI ve veri işleme:** Scikit-learn (TF-IDF ve Cosine Similarity), Pandas
- **Veri doğrulama:** Pydantic
- **Güvenlik:** `X-API-Key` tabanlı API erişim kontrolü
- **DevOps ve kod kalitesi:** Docker, GitHub Actions (CI/CD), SonarQube
- **Test:** Pytest

## Nasıl Çalışır? — Hibrit Öneri Modeli

OleAI Engine, tarifleri yalnızca mevcut malzemelerin sayısına göre sıralamaz. Malzeme uyumluluğunu, kullanıcı tercihlerini ve tarifin pratikliğini birlikte değerlendiren bir hibrit puanlama yaklaşımı kullanır.

### 1. Malzeme eşleştirme (Structured Fulfillment)

Kullanıcının kilerindeki malzemeler, desteklenen ağırlık ve hacim birimleri (ör. kg, g, l, ml) üzerinden tarif gereksinimleriyle karşılaştırılır. Bu işlem, tarifteki malzemelerin ne kadarının mevcut olduğunu hesaplamaya yardımcı olur.

> Birim dönüşümleri ve miktar karşılaştırmaları, uygulamanın desteklediği birimler ve veri modeliyle sınırlıdır.

### 2. NLP ile lezzet benzerliği (Taste Similarity)

Kullanıcının geçmiş etkileşimleri — kaydetme, beğenme veya geçme gibi — değerlendirilerek tercih profili oluşturulur. Zamana bağlı zayıflama (time decay) yaklaşımı, daha yeni etkileşimlerin tercih profiline daha fazla katkı sağlamasını mümkün kılar.

Tarif metinleri TF-IDF ile vektörleştirilir ve Cosine Similarity (kosinüs benzerliği) kullanılarak kullanıcı tercihleriyle benzerlikleri hesaplanır.

### 3. Dinamik öneri modları

Kullanıcının ihtiyacına göre farklı filtreler ve puanlama ağırlıkları uygulanır.

## Öneri Modları (Recommendation Modes)

- **`DEFAULT`:** Kilerdeki malzeme uyumluluğu ve lezzet tercihi eşit ağırlıkla değerlendirilir (%50 / %50).
- **`STRICT` (Katı):** Tarif malzemelerinin en az %90'ının kullanıcının kilerinde bulunmasını gerektirir. Eksik malzeme toleransı uygulamanın ilgili filtreleme kurallarına bağlıdır.
- **`FOR_YOU` (Sizin İçin):** Kişiselleştirmeye öncelik verir. Lezzet benzerliği %80 ağırlıkla değerlendirilir; kilerde eksik malzeme bulunması tek başına tarifi dışlamayabilir.
- **`QUICK` (Hızlı):** Hazırlık ve pişirme sürelerinin toplamı 45 dakikayı aşan tarifleri eler.
- **`EXPLORE` (Keşfet):** Kullanıcının daha önce sık karşılaşmadığı tarifleri öne çıkarmayı hedefler.
- **`MINIMAL` (Minimalist):** Kilerdeki malzemelerle en az %60 eşleşme sağlayan tariflere odaklanır.
- **`ULTIMATE` (Gurme):** Lezzet skoru yüksek ve malzemelerinin %70'inden fazlası mevcut olan tarifleri öne çıkarır.

## Ek Puanlamalar (Boosts)

- **Zero Waste (Sıfır Atık) Boost:** Son kullanma tarihine üç gün veya daha az kalan kiler malzemelerini kullanan tariflere ek puan verilebilir. Belirtilen yapılandırmada bu bonus `%20` olarak tanımlanmıştır.
- **New Recipe Boost:** Son yedi gün içinde sisteme eklenen tariflere ek görünürlük sağlayarak yeni tariflerin önerilerde yer almasını destekler.

> Bonusların nihai sıralamaya etkisi, uygulamadaki puanlama ve sıralama kurallarına bağlıdır.

## API Uç Noktaları (Endpoints)

API erişimi için isteklerde `X-API-Key` başlığı kullanılmalıdır.

| Method | Endpoint | Açıklama |
| --- | --- | --- |
| `GET` | `/health` | Servisin sağlık durumunu, modelin son güncellenme zamanını ve modeldeki tarif sayısını bildirir. |
| `POST` | `/api/v1/recommendations` | Kiler malzemelerini (`pantryItems`), arama metnini, kullanıcı etkileşimlerini ve öneri modunu alır; en uygun `top_k` tarifi skorlarıyla birlikte döndürür. |
| `POST` | `/api/v1/recipes/sync` | Yeni veya güncellenmiş tarif verilerini öneri modeline aktarır ve ilgili vektörleri günceller. |

## Proje Yapısı

```text
OleAI-ai/
├── .github/
│   └── workflows/              # CI/CD iş akışları (ai-cd.yml, ci.yml)
├── src/
│   ├── api/                     # API uç noktaları ve şemalar (schemas.py)
│   ├── core/                    # Konfigürasyon ve güvenlik (config.py, exceptions.py)
│   ├── models/                  # Öneri modelleri (recommender.py)
│   ├── services/                # İş mantığı ve veri hazırlama
│   │   ├── data_preprocessor.py
│   │   └── recipe_sync_service.py
│   └── main.py                  # FastAPI uygulamasının başlangıç noktası
├── tests/                       # Pytest testleri
├── Dockerfile                   # Konteyner imajı tanımı
├── requirements.txt             # Python bağımlılıkları
├── sonar-project.properties     # SonarQube yapılandırması
├── README.md
└── CONTRIBUTING.md
```

## Kurulum ve Çalıştırma

### Gereksinimler

- Python 3.10 veya üzeri
- Git
- Docker (yalnızca Docker üzerinden çalıştırmak için)

### 1. Repoyu klonlama

```bash
git clone https://github.com/onuraydi/OleAI-ai.git
cd OleAI-ai
```

### 2. Sanal ortam oluşturma

**Windows (PowerShell):**

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

**Linux / macOS:**

```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Bağımlılıkları yükleme

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### 4. Ortam değişkenlerini yapılandırma

Proje kök dizininde `.env` dosyası oluşturun:

```ini
API_KEY=guclu_ve_tahmin_edilemez_bir_api_anahtari
SONAR_TOKEN=sonarqube_token_degeri
```

- `API_KEY` değerini güçlü ve tahmin edilmesi zor bir değerle değiştirin.
- `SONAR_TOKEN` yalnızca SonarQube analizi çalıştırılacaksa gereklidir.
- Gerçek gizli anahtarları Git deposuna eklemeyin. `.env` dosyasının `.gitignore` içinde olduğundan emin olun.
- Uygulamanın kullandığı ortam değişkenlerinin isimlerini doğrulamak için yapılandırma kodunu inceleyin.

### 5. Uygulamayı yerel ortamda başlatma

```bash
uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload
```

API dokümantasyonuna şu adresten ulaşabilirsiniz:

- Swagger UI: <http://localhost:8000/docs>
- OpenAPI şeması: <http://localhost:8000/openapi.json>

`--reload` geliştirme ortamı içindir; üretim ortamında uygun bir sunucu yapılandırması kullanın.

### 6. Docker ile çalıştırma

Proje kök dizininde Docker imajını oluşturun:

```bash
docker build -t oleai-engine .
```

Ardından konteyneri başlatın:

```bash
docker run -d \
  --name oleai-engine \
  -p 8000:8000 \
  --env-file .env \
  oleai-engine
```

Konteyner günlüklerini görüntülemek için:

```bash
docker logs -f oleai-engine
```

## Testler ve Kod Kapsamı (Coverage)

Testleri çalıştırmak için:

```bash
pytest
```

Terminalde kod kapsamı raporu almak için `pytest-cov` bağımlılığının kurulu olması gerekir:

```bash
pytest --cov=src --cov-report=term-missing
```

HTML raporu oluşturmak için:

```bash
pytest --cov=src --cov-report=html
```

HTML raporu `htmlcov/` dizinine yazılır.

## Güvenlik Notları

- API anahtarlarını kaynak koda, test çıktısına veya commit'lere eklemeyin.
- Üretim ortamında HTTPS, güvenli sır yönetimi ve uygun erişim kontrolleri kullanın.
- `X-API-Key` kontrolünü tek başına kapsamlı bir kullanıcı kimlik doğrulama sistemi olarak değerlendirmeyin.
- Hata yanıtlarında gizli yapılandırma değerlerini veya hassas bilgileri açığa çıkarmayın.

## Katkıda Bulunma

Hata bildirimi, öneri veya kod katkısı yapmak istiyorsanız [`CONTRIBUTING.md`](CONTRIBUTING.md) dosyasındaki geliştirme ve Pull Request yönergelerini inceleyin.

<div align="right">

[⬆ Başa dön](#) &nbsp;|&nbsp; [🇬🇧 İngilizce sürüme git](#en)

</div>

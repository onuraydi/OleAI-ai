<div align="center">

**🌐 Language / Dil:** &nbsp; [🇬🇧 English](#en) &nbsp;|&nbsp; [🇹🇷 Türkçe](#tr)

</div>

---

<a id="en"></a>

> 🇹🇷 Türkçe okumak için: **[Türkçe sürüme git ↓](#tr)**

# OleAI Engine — Contributing Guide

Thank you for your interest in contributing to the OleAI Engine project. This guide describes the recommended steps for keeping the development process consistent, testable, and reviewable.

## Development Workflow

### 1. Fork the repository

Fork the project to your own account on GitHub.

### 2. Clone the fork

```bash
git clone https://github.com/onuraydi/OleAI-ai.git
cd OleAI-ai
```

Before development, create a virtual environment and install the dependencies. See the setup steps in [`README.md`](README.md) for details.

### 3. Create a new branch

Do not work directly on the `main` or `master` branch. Use branch names that describe the purpose of the change:

```bash
# New feature
git checkout -b feature/new-recommendation-mode

# Bug fix
git checkout -b bugfix/sync-error

# Documentation
git checkout -b docs/readme-update

# Test
git checkout -b test/zero-waste-boost
```

Write branch names in lowercase and separate words with hyphens.

## Coding Standards

### Architecture and responsibilities

Preserve the responsibilities of the layers in the existing project structure:

- `src/api/`: API endpoints and request/response schemas
- `src/core/`: Configuration, security, and shared infrastructure components
- `src/models/`: Recommendation model and scoring logic
- `src/services/`: Data preparation, synchronization, and application business logic
- `tests/`: Automated tests

Add new code to the module that matches its responsibility. Do not create unnecessary layers or overlapping responsibilities.

### Python code quality

- Follow the project's existing coding style and naming approach.
- Choose clear, purpose-appropriate names for variables, functions, and classes.
- Use type hints and descriptive docstrings where needed.
- Handle errors appropriately instead of swallowing them silently.
- Preserve the existing Pydantic schemas and validation rules in API requests and responses.
- Do not include secret keys, passwords, or personal data in source code or logs.

### Test-driven development

Add appropriate automated tests for every new feature or bug fix.

- Place tests in the `tests/` directory.
- Write tests so they can be run with Pytest.
- Test edge cases and invalid inputs in addition to successful scenarios.
- If you changed the recommendation algorithm, verify the expected behavior of the relevant modes, scores, and ranking.
- Run the existing tests and make sure your change does not break other behavior.
- When needed, check the code coverage report with the command `pytest --cov=src --cov-report=term-missing`.

### Static code analysis

If possible, run a code analysis with SonarQube or SonarLint before opening a Pull Request. The repository contains a `sonar-project.properties` configuration. Make sure the quality checks required by the CI/CD workflow pass.

## Commit Messages — Conventional Commits

Use the Conventional Commits format in commit messages:

```text
<type>: <short and descriptive message>
```

Examples:

- `feat: add MINIMAL recommendation mode`
- `fix: resolve dimension error in TF-IDF vector matrix`
- `docs: update recommendation modes section in README`
- `test: add tests for zero waste scoring`
- `refactor: tidy model service calls`
- `ci: add coverage report to test workflow`

Common types:

| Type | Usage |
| --- | --- |
| `feat` | New feature |
| `fix` | Bug fix |
| `docs` | Documentation change |
| `test` | Adding or editing tests |
| `refactor` | Code improvement that does not change behavior |
| `ci` | CI/CD configuration |
| `build` | Dependency or build system change |
| `chore` | Other maintenance tasks |

Write commit messages that are short, clear, and describe the change made.

## Pull Request (PR) Process

### 1. Verify your changes

Run the tests before creating a Pull Request:

```bash
pytest
```

If you want a coverage report:

```bash
pytest --cov=src --cov-report=term-missing
```

Review your changes and verify that you have not accidentally added secret files, local configuration, or unrelated files.

### 2. Commit and push your changes

```bash
git add .
git commit -m "feat: improve time decay algorithm"
git push origin feature/time-decay-opt
```

Replace the branch name with the branch you created.

### 3. Open a Pull Request

On GitHub, open a Pull Request from the branch in your fork to the target branch in the main repository.

Include the following information in the PR description:

- **Purpose:** Why is the change needed?
- **Changes:** What was added, fixed, or removed?
- **Affected areas:** Which API endpoints, recommendation modes, or services are affected?
- **Tests:** Which tests were run and what were the results?
- **API compatibility:** Is there a change that affects backward compatibility in request/response schemas or behavior?

### 4. CI checks and code review

- Check the results of the CI workflows run by GitHub Actions.
- Fix any failing tests or quality checks.
- Evaluate feedback from the code review and make the necessary adjustments.
- Changes are merged into the target branch after review and approval by the project maintainers.

## Pre-Contribution Checklist

Before opening a Pull Request, check the following:

- [ ] I created an appropriate branch for the change.
- [ ] The code follows the existing project structure and standards.
- [ ] I added or updated the relevant tests.
- [ ] I ran the `pytest` tests.
- [ ] I did not commit secret keys or local configuration files.
- [ ] I wrote the commit messages in Conventional Commits format.
- [ ] I described the change and the test results in the Pull Request description.

Thank you for your contribution!

<div align="right">

[⬆ Back to top](#) &nbsp;|&nbsp; [🇹🇷 Türkçe sürüme git](#tr)

</div>

---
---

<a id="tr"></a>

> 🇬🇧 To read in English: **[Go to the English version ↑](#en)**

# OleAI Engine — Katkıda Bulunma Rehberi

OleAI Engine projesine katkıda bulunmak istediğiniz için teşekkür ederiz. Bu rehber; geliştirme sürecini tutarlı, test edilebilir ve gözden geçirilebilir tutmak için izlenmesi önerilen adımları açıklar.

## Geliştirme İş Akışı

### 1. Repoyu fork'lama

GitHub üzerinden projeyi kendi hesabınıza fork'layın.

### 2. Fork'u klonlama

```bash
git clone https://github.com/onuraydi/OleAI-ai.git
cd OleAI-ai
```

Geliştirme öncesinde sanal ortam oluşturup bağımlılıkları yükleyin. Ayrıntılar için [`README.md`](README.md) dosyasındaki kurulum adımlarına bakın.

### 3. Yeni bir branch oluşturma

Doğrudan `main` veya `master` branch'i üzerinde çalışmayın. Değişikliğin amacını anlatan branch isimleri kullanın:

```bash
# Yeni özellik
git checkout -b feature/yeni-oneri-modu

# Hata düzeltmesi
git checkout -b bugfix/sync-hatasi

# Dokümantasyon
git checkout -b docs/readme-guncellemesi

# Test
git checkout -b test/zero-waste-boost
```

Branch isimlerini küçük harfle ve kelimeleri tireyle ayırarak yazın.

## Kod Yazım Standartları

### Mimari ve sorumluluklar

Mevcut proje yapısındaki katmanların sorumluluklarını koruyun:

- `src/api/`: API uç noktaları ve istek/yanıt şemaları
- `src/core/`: Konfigürasyon, güvenlik ve ortak altyapı bileşenleri
- `src/models/`: Öneri modeli ve puanlama mantığı
- `src/services/`: Veri hazırlama, senkronizasyon ve uygulama iş mantığı
- `tests/`: Otomatik testler

Yeni kodu, sorumluluğuna uygun modüle ekleyin. Gereksiz katmanlar veya birbiriyle örtüşen sorumluluklar oluşturmayın.

### Python kod kalitesi

- Projenin mevcut kodlama biçimini ve isimlendirme yaklaşımını izleyin.
- Değişken, fonksiyon ve sınıf adlarını açık ve amaca uygun seçin.
- Gerekli yerlerde tür ipuçları (type hints) ve açıklayıcı docstring'ler kullanın.
- Hataları sessizce yutmak yerine uygun şekilde ele alın.
- API istek ve yanıtlarında mevcut Pydantic şemalarını ve doğrulama kurallarını koruyun.
- Gizli anahtarları, parolaları veya kişisel verileri kaynak koda ve günlük kayıtlarına eklemeyin.

### Test odaklı geliştirme

Her yeni özellik veya hata düzeltmesi için uygun otomatik testler ekleyin.

- Testleri `tests/` dizinine yerleştirin.
- Testleri Pytest ile çalıştırılabilir şekilde yazın.
- Başarılı durumların yanında sınır durumlarını ve geçersiz girdileri de test edin.
- Öneri algoritmasında değişiklik yaptıysanız ilgili modların, puanların ve sıralamanın beklenen davranışını doğrulayın.
- Mevcut testleri çalıştırın ve değişikliğinizin başka davranışları bozmadığından emin olun.
- Kod kapsamı raporunu gerektiğinde `pytest --cov=src --cov-report=term-missing` komutuyla kontrol edin.

### Statik kod analizi

Pull Request açmadan önce mümkünse SonarQube veya SonarLint ile kod analizi çalıştırın. Depoda `sonar-project.properties` yapılandırması bulunmaktadır. CI/CD iş akışının gerektirdiği kalite kontrollerinin başarılı olduğundan emin olun.

## Commit Mesajları — Conventional Commits

Commit mesajlarında Conventional Commits biçimini kullanın:

```text
<type>: <kısa ve açıklayıcı mesaj>
```

Örnekler:

- `feat: MINIMAL öneri modu eklendi`
- `fix: TF-IDF vektör matrisindeki boyut hatası giderildi`
- `docs: README öneri modları bölümü güncellendi`
- `test: sıfır atık puanlaması için testler eklendi`
- `refactor: model servis çağrıları düzenlendi`
- `ci: test iş akışına coverage raporu eklendi`

Yaygın türler:

| Tür | Kullanım |
| --- | --- |
| `feat` | Yeni özellik |
| `fix` | Hata düzeltmesi |
| `docs` | Dokümantasyon değişikliği |
| `test` | Test ekleme veya düzenleme |
| `refactor` | Davranışı değiştirmeyen kod iyileştirmesi |
| `ci` | CI/CD yapılandırması |
| `build` | Bağımlılık veya derleme sistemi değişikliği |
| `chore` | Diğer bakım işleri |

Commit mesajını kısa, açık ve yapılan değişikliği anlatacak şekilde yazın.

## Pull Request (PR) Süreci

### 1. Değişiklikleri doğrulama

Pull Request oluşturmadan önce testleri çalıştırın:

```bash
pytest
```

Coverage raporu almak istiyorsanız:

```bash
pytest --cov=src --cov-report=term-missing
```

Değişikliklerinizi gözden geçirin ve yanlışlıkla gizli dosya, yerel yapılandırma veya ilgisiz dosya eklemediğinizi doğrulayın.

### 2. Değişiklikleri commit'leme ve push etme

```bash
git add .
git commit -m "feat: time decay algoritması iyileştirildi"
git push origin feature/time-decay-opt
```

Branch adını kendi oluşturduğunuz branch ile değiştirin.

### 3. Pull Request açma

GitHub üzerinden fork'unuzdaki branch'ten ana depodaki hedef branch'e Pull Request açın.

PR açıklamasında şu bilgileri belirtin:

- **Amaç:** Değişiklik neden gerekli?
- **Değişiklikler:** Neler eklendi, düzeltildi veya kaldırıldı?
- **Etkilenen alanlar:** Hangi API uç noktaları, öneri modları veya servisler etkilendi?
- **Testler:** Hangi testler çalıştırıldı ve sonuçları ne oldu?
- **API uyumluluğu:** İstek/yanıt şemalarında veya davranışta geriye dönük uyumluluğu etkileyen bir değişiklik var mı?

### 4. CI kontrolleri ve kod incelemesi

- GitHub Actions tarafından çalıştırılan CI iş akışlarının sonucunu kontrol edin.
- Başarısız testler veya kalite kontrolleri varsa düzeltin.
- Kod incelemesinden gelen geri bildirimleri değerlendirin ve gerekli düzenlemeleri yapın.
- Değişiklikler, proje bakımcılarının incelemesi ve onayından sonra hedef branch'e alınır.

## Katkı Öncesi Kontrol Listesi

Pull Request açmadan önce aşağıdakileri kontrol edin:

- [ ] Değişiklik için uygun bir branch oluşturdum.
- [ ] Kod mevcut proje yapısına ve standartlarına uyuyor.
- [ ] İlgili testleri ekledim veya güncelledim.
- [ ] `pytest` testlerini çalıştırdım.
- [ ] Gizli anahtarları veya yerel yapılandırma dosyalarını commit'lemedim.
- [ ] Commit mesajlarını Conventional Commits biçiminde yazdım.
- [ ] Pull Request açıklamasında değişikliği ve test sonuçlarını belirttim.

Katkınız için teşekkürler!

<div align="right">

[⬆ Başa dön](#) &nbsp;|&nbsp; [🇬🇧 İngilizce sürüme git](#en)

</div>

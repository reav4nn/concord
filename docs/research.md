# Research və qərarlar

## Hakaton: NeuroBridge.SI (Bakı, 9-10 okt 2026)
- Təşkilatçı Starnest Academy-dir. Partnyor Azercell, qaliblər OMNI AI Summit-də elan olunur.
- Komandalar 1-5 nəfərdən ibarətdir, biz 2 nəfərik.
- Track-lər: AI Gaming və AI Enterprise Solutions. Biz Enterprise track-dəyik.
- Kart: dəyər 25, prototip/AI 30, test 20, feasibility 15, orijinallıq 10.
- Birinci turu GPT və Claude oxuyur. Final turunda insan jüri eyni kartla yenidən qiymət verir.
- Bərabərlik olanda əvvəl prototip balına, sonra test balına baxılır.
- Qaydalar:
  - Əvvəlcədən research etmək olar.
  - Məhsul hakaton başlayandan sonra qurulmalıdır.
  - Kitabxanalar disclosure ilə istifadə oluna bilər.
- Mənbə: neurobridge.si/rules, neurobridge.si/tracks
- Qeyd: qaydalarda finalçı sayı həm 30, həm 10 yazılıb.

## İdeya seçimi (judge-with-debate)
10 ideyanı 3 müstəqil "hakim" qiymətləndirdi: birinci turu oxuyan LLM, Azercell-dən jüri üzvü və skeptik ML mühəndisi.

| İdeya | J1 | J2 | J3 |
|---|---|---|---|
| **Freight sənəd cross-check (seçildi)** | 80 | 81 | 79 |
| Tender compliance | 77 | 77 | 71 |
| AI playtest agent | 74 | 76 | 70 |
| Telecom support | 72 | 73 | 68 |
| Qaimə | 70 | 71 | 68 |

Hakimlərin üçü də eyni əsas tələni göstərdi: dairəvi sintetik test, yəni datanı da, cavabları da özün yaradıb özün yoxlayırsan. Bunun çarəsi:
- blind injection
- güclü baseline
- uğursuzluqları göstərmək
- ən azı bir real istifadəçidən rəqəm almaq

## Müsahibə: Air Cargo Azerbaijan
**Kim:** Əsəd Piriyev. **Nə vaxt:** 9 okt 2026, telefonla.

1. **Hansı sənədlər yoxlanılır?** Invoice, packing list, mənşə sertifikatı. Hava ilə gələndə AWB da.
2. **Yoxlama nə qədər çəkir?** Sənədlər hamısı əldə olanda 5-10 dəqiqə, bəzən 20 dəqiqə.
3. **Ən çox hansı səhvlər olur?** Hər yerdə ola bilər. Ən çox alıcı tərəfi səhv yazırlar, hesablamada da səhv olur, məsələn 5 dollarlıq fərq.
4. **Səhv gecikməyə səbəb olurmu?** Çox vaxt gecikməyə düşmür.

**Nəticə:** dəyəri "yoxlama vaxtı və səhvin əvvəlcədən tutulması" üzərində qururuq, "gecikmənin qarşısını alırıq" demirik.

## Zəng siyahısı
| Şirkət | Telefon | Status |
|---|---|---|
| ISO BROKER | +994 50 550 34 28 | açmadı |
| Azerbaijan Logistics Services | +994 99 908 08 88 | açmadı |
| Global Logistics Services | +994 50 215 58 28 | açmadı |
| Freight Azerbaijan | +994 70 847 81 68 | açmadı |
| Global Freight Forwarding | +994 50 224 58 08 | açmadı |
| Air Cargo Azerbaijan | +994 12 488 65 17 | **cavab verdi** (yuxarıda) |
| AG Global Logistic | +994 10 327 09 56 | WhatsApp-dan yazmağı dedilər, mesaj göndərildi |

## Ölkə konteksti
- Azərbaycanın 2025-2028 Sİ strategiyası Azərbaycan dilində AI həllərini prioritet sayır.
- 2026-2028 rəqəmsal inkişaf planında "suveren AI" mövzusu var.
- Orta Dəhliz yükləri artır. Bu, layihənin üçdilli (az/en/ru) sənəd emalını əsaslandırır.

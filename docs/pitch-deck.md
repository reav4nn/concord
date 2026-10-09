# Pitch deck (8 slayd, kartın ardıcıllığı ilə)

Birinci turu LLM oxuyur. Hər slaydın başlığı kart kriteriyasını açıq desin, rəqəmlər mətnlə yazılsın (yalnız şəkildə olmasın).

1. **Concord.**
   - Tagline: "Freight documents that agree before customs".
   - Loqo, komanda (2 nəfər), track.
2. **Problem (Value for the user).**
   - Kim: Bakıdakı deklarant.
   - 4 sənəd, fərqli tərəflər doldurur.
   - Sitat: "5-20 dəqiqə; ən çox alıcı tərəfi və məbləğ səhv olur" (Air Cargo Azerbaijan, Əsəd Piriyev).
3. **Demo (Prototype).**
   - Nəticə ekranının skrinşotu: 2 xəta, 1 uyğun ad variantı, dəlil cədvəli.
   - Akış: yüklə → oxu → tutuşdur → məktub.
4. **AI nə edir, kod nə edir.**
   - CLAUDE.md-dəki cədvəl.
   - Alıcı adının 3 yazılışı nümunəsi: baseline səhv salır, Concord salmır.
5. **Quality testing.**
   - Test setinin necə qurulduğu: blind injection, holdout seed.
   - Precision/recall cədvəli: Concord və baseline.
   - 2-3 uğursuzluq skrinşotla.
6. **Feasibility.**
   - Yük başına xərc (API).
   - Lazım olan data: anonimləşdirilmiş real sənədlər.
   - Növbəti addım: 2 həftəlik pilot ekspeditorla.
7. **Originality.**
   - Adi OCR və ya chatbot deyil.
   - Sənədlərarası yoxlama, üçdilli ad uyğunlaşdırması, hər qərarda mənbə.
8. **Next step və disclosure.**
   - Pilot, skan test seti, e-gömrük inteqrasiyası.
   - İstifadə olunan model, data və komponentlər.

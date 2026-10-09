"""UI and finding texts in Azerbaijani, English and Russian.

Findings store a `type` and `params`; texts are rendered here at display time, so switching
language never needs another model call.
"""

LANGS = {"az": "AZ", "en": "EN", "ru": "RU"}

UI = {
    "tagline": {"az": "Yük sənədlərinin avtomatik tutuşdurulması", "en": "Automatic cross-check of shipment documents", "ru": "Автоматическая сверка документов на груз"},
    "tab_upload": {"az": "Yüklə", "en": "Upload", "ru": "Загрузка"},
    "tab_result": {"az": "Nəticə", "en": "Result", "ru": "Результат"},
    "upload_title": {"az": "Yükün sənədlərini əlavə edin", "en": "Add the shipment's documents", "ru": "Добавьте документы на груз"},
    "upload_hint": {"az": "PDF, skan və ya telefon şəkli. Ən azı 2 sənəd lazımdır.", "en": "PDF, scan or phone photo. At least 2 documents.", "ru": "PDF, скан или фото с телефона. Минимум 2 документа."},
    "check": {"az": "Yoxla", "en": "Check", "ru": "Проверить"},
    "sample": {"az": "Nümunə yükü aç", "en": "Open sample", "ru": "Открыть пример"},
    "reading": {"az": "Sənədlər oxunur...", "en": "Reading documents...", "ru": "Чтение документов..."},
    "reading_one": {"az": "{doc} oxunur", "en": "Reading {doc}", "ru": "Читаем: {doc}"},
    "comparing": {"az": "Tutuşdurulur...", "en": "Cross-checking...", "ru": "Сверка..."},
    "done": {"az": "Hazırdır", "en": "Done", "ru": "Готово"},
    "done_go": {"az": "Hazırdır. 'Nəticə' tab-ına keçin.", "en": "Done. Open the 'Result' tab.", "ru": "Готово. Откройте вкладку «Результат»."},
    "sample_go": {"az": "Nümunə yük yükləndi. 'Nəticə' tab-ına keçin.", "en": "Sample loaded. Open the 'Result' tab.", "ru": "Пример загружен. Откройте вкладку «Результат»."},
    "failed": {"az": "Yoxlama alınmadı: {e}. Sənədi yenidən yükləyin və ya nümunə yükü açın.", "en": "Check failed: {e}. Upload again or open the sample.", "ru": "Проверка не удалась: {e}. Загрузите снова или откройте пример."},
    "empty": {"az": "Hələ nəticə yoxdur. Sənəd yükləyin və ya nümunə yükü açın.", "en": "No result yet. Upload documents or open the sample.", "ru": "Результата пока нет. Загрузите документы или откройте пример."},
    "n_error": {"az": "xəta", "en": "errors", "ru": "ошибок"},
    "n_warn": {"az": "yoxlanmalı", "en": "to review", "ru": "проверить"},
    "n_ok": {"az": "uyğun", "en": "match", "ru": "совпадает"},
    "tab_findings": {"az": "Uyğunsuzluqlar", "en": "Discrepancies", "ru": "Расхождения"},
    "tab_letter": {"az": "Düzəliş məktubu", "en": "Correction email", "ru": "Письмо об исправлении"},
    "tab_data": {"az": "Çıxarılan data", "en": "Extracted data", "ru": "Извлечённые данные"},
    "col_doc": {"az": "Sənəd", "en": "Document", "ru": "Документ"},
    "col_value": {"az": "Dəyər", "en": "Value", "ru": "Значение"},
    "col_where": {"az": "Harada", "en": "Where", "ru": "Где"},
    "who": {"az": "Kim aşkarladı", "en": "Found by", "ru": "Кто обнаружил"},
    "fix": {"az": "Təklif olunan düzəliş", "en": "Suggested fix", "ru": "Предлагаемое исправление"},
    "passed": {"az": "Uyğun gələn yoxlamalar:", "en": "Checks that match:", "ru": "Совпадающие проверки:"},
    "no_letter": {"az": "Xəta yoxdur, məktub lazım deyil.", "en": "No errors, no email needed.", "ru": "Ошибок нет, письмо не нужно."},
    "letter_note": {"az": "Yalnız xəta statuslu bəndlər daxil edilir. Yoxlanmalı bəndlər brokerin təsdiqini gözləyir.", "en": "Only confirmed errors are included. Items to review wait for the broker.", "ru": "Включены только подтверждённые ошибки. Пункты «проверить» ждут брокера."},
}

SEV = {
    "error": {"az": "Xəta", "en": "Error", "ru": "Ошибка"},
    "warn": {"az": "Yoxlanmalı", "en": "Review", "ru": "Проверить"},
    "ok": {"az": "Uyğun", "en": "Match", "ru": "Совпадает"},
}

DOC = {
    "invoice": {"az": "Invoice", "en": "Invoice", "ru": "Инвойс"},
    "packing_list": {"az": "Packing list", "en": "Packing list", "ru": "Упаковочный лист"},
    "certificate_of_origin": {"az": "Mənşə sertifikatı", "en": "Certificate of origin", "ru": "Сертификат происхождения"},
    "awb": {"az": "AWB", "en": "AWB", "ru": "AWB"},
    "invoice_lines": {"az": "Invoice, sətirlər", "en": "Invoice, line items", "ru": "Инвойс, строки"},
    "invoice_total": {"az": "Invoice, TOTAL", "en": "Invoice, TOTAL", "ru": "Инвойс, ИТОГО"},
}

CHECK = {  # passed-check labels
    "weight": {"az": "Brutto çəki", "en": "Gross weight", "ru": "Вес брутто"},
    "packages": {"az": "Yer sayı", "en": "Pieces", "ru": "Кол-во мест"},
    "tax_id": {"az": "Alıcı VÖEN", "en": "Consignee tax ID", "ru": "ИНН получателя"},
    "total": {"az": "Invoice cəmi", "en": "Invoice total", "ru": "Сумма инвойса"},
    "hs": {"az": "HS kodları", "en": "HS codes", "ru": "Коды ТН ВЭД"},
    "consignee": {"az": "Alıcı adı", "en": "Consignee name", "ru": "Наименование получателя"},
}

CHECKER = {
    "code_numbers": {"az": "Kod: rəqəm müqayisəsi", "en": "Code: number comparison", "ru": "Код: сравнение чисел"},
    "code_exact": {"az": "Kod: dəqiq uyğunluq", "en": "Code: exact match", "ru": "Код: точное совпадение"},
    "code_math": {"az": "Kod: hesab yoxlaması", "en": "Code: arithmetic check", "ru": "Код: арифметическая проверка"},
    "code_codes": {"az": "Kod: kod müqayisəsi", "en": "Code: code comparison", "ru": "Код: сравнение кодов"},
    "ai_names": {"az": "AI: ad və translit uyğunlaşdırması", "en": "AI: name and transliteration matching", "ru": "ИИ: сопоставление названий и транслитерации"},
}

# per finding type: field, title, summary, fix, checker. {placeholders} come from finding["params"]
FINDING = {
    "weight_mismatch": dict(
        checker="code_numbers",
        field={"az": "Brutto çəki", "en": "Gross weight", "ru": "Вес брутто"},
        title={"az": "Ümumi çəki uyğun gəlmir", "en": "Gross weight does not match", "ru": "Вес брутто не совпадает"},
        summary={"az": "Sənədlərdə brutto çəki fərqlidir (tolerans 0,5%).", "en": "Gross weight differs between documents (tolerance 0.5%).", "ru": "Вес брутто в документах различается (допуск 0,5%)."},
        fix={"az": "Bütün sənədlərdə çəkini {value} kq etmək.", "en": "Set gross weight to {value} kg on every document.", "ru": "Указать вес {value} кг во всех документах."}),
    "package_mismatch": dict(
        checker="code_exact",
        field={"az": "Yer sayı", "en": "Pieces", "ru": "Кол-во мест"},
        title={"az": "Yer sayı uyğun gəlmir", "en": "Number of pieces does not match", "ru": "Количество мест не совпадает"},
        summary={"az": "Sənədlərdə qutu/yer sayı fərqlidir.", "en": "The number of cartons / pieces differs between documents.", "ru": "Количество мест в документах различается."},
        fix={"az": "Yer sayını {value} kimi düzəltmək.", "en": "Correct the piece count to {value}.", "ru": "Исправить количество мест на {value}."}),
    "tax_id_mismatch": dict(
        checker="code_exact",
        field={"az": "Alıcı VÖEN", "en": "Consignee tax ID", "ru": "ИНН получателя"},
        title={"az": "Alıcının VÖEN-i fərqlidir", "en": "Consignee tax ID differs", "ru": "ИНН получателя различается"},
        summary={"az": "VÖEN bütün sənədlərdə eyni olmalıdır.", "en": "The tax ID (VÖEN) must be identical on every document.", "ru": "ИНН (VÖEN) должен совпадать во всех документах."},
        fix={"az": "Səhv sənədi {value} VÖEN-i ilə yeniləmək.", "en": "Reissue the wrong document with tax ID {value}.", "ru": "Переоформить документ с ИНН {value}."}),
    "total_mismatch": dict(
        checker="code_math",
        field={"az": "Məbləğ", "en": "Amount", "ru": "Сумма"},
        title={"az": "Invoice-un cəmi sətirlərlə tutmur", "en": "Invoice total does not add up", "ru": "Итог инвойса не сходится со строками"},
        summary={"az": "{n} sətrin cəmi {sum} {cur}, TOTAL isə {total} {cur}. Fərq {diff} {cur}.", "en": "{n} line items add up to {sum} {cur}, the TOTAL says {total} {cur}. Difference {diff} {cur}.", "ru": "Сумма {n} строк: {sum} {cur}, ИТОГО: {total} {cur}. Разница {diff} {cur}."},
        fix={"az": "TOTAL sətrini düzəltmək.", "en": "Correct the TOTAL line.", "ru": "Исправить строку ИТОГО."}),
    "hs_mismatch": dict(
        checker="code_codes",
        field={"az": "HS kodu", "en": "HS code", "ru": "Код ТН ВЭД"},
        title={"az": "HS kodları sənədlər arasında fərqlidir", "en": "HS codes differ between documents", "ru": "Коды ТН ВЭД в документах различаются"},
        summary={"az": "Invoice və mənşə sertifikatında fərqli HS kodları var.", "en": "The invoice and the certificate of origin list different HS codes.", "ru": "В инвойсе и сертификате происхождения разные коды ТН ВЭД."},
        fix={"az": "Brokerlə düzgün kodu təsdiqləyib bir sənədi yeniləmək.", "en": "Confirm the right code with the broker and update one document.", "ru": "Согласовать код с брокером и исправить документ."}),
    "consignee_mismatch": dict(
        checker="ai_names",
        field={"az": "Alıcı adı", "en": "Consignee name", "ru": "Наименование получателя"},
        title={"az": "Alıcı fərqli şirkət kimi görünür", "en": "Consignee looks like a different company", "ru": "Получатель похож на другую компанию"},
        summary=None,
        fix={"az": "Düzgün alıcı adı ilə sənədi yeniləmək.", "en": "Reissue the document with the correct consignee.", "ru": "Переоформить документ с верным получателем."}),
    "consignee_unsure": dict(
        checker="ai_names",
        field={"az": "Alıcı adı", "en": "Consignee name", "ru": "Наименование получателя"},
        title={"az": "Alıcı adı yoxlanmalıdır", "en": "Consignee name needs review", "ru": "Получателя нужно проверить"},
        summary=None,
        fix={"az": "Brokerin təsdiqi lazımdır.", "en": "Needs the broker's confirmation.", "ru": "Нужно подтверждение брокера."}),
    "consignee_variants": dict(
        checker="ai_names",
        field={"az": "Alıcı adı", "en": "Consignee name", "ru": "Наименование получателя"},
        title={"az": "Alıcı adı {n} cür yazılıb, eyni şirkətdir", "en": "Consignee written {n} ways, same company", "ru": "Получатель написан {n} способами, это одна компания"},
        summary=None,
        fix={"az": "Düzəliş lazım deyil.", "en": "No fix needed.", "ru": "Исправление не требуется."}),
}


def t(key, lang, **kw):
    s = UI[key].get(lang) or UI[key]["az"]
    return s.format(**kw) if kw else s


def doc_label(key, lang):
    return DOC.get(key, {}).get(lang, key)


def finding_text(f, lang):
    """Return field/title/summary/fix/checker for a finding in `lang`."""
    spec = FINDING.get(f["type"])
    if not spec:
        return {k: f.get(k, "") for k in ("field", "title", "summary", "fix", "checker")}
    p = f.get("params", {})
    reasons = p.get("reason", {})
    summary = (spec["summary"][lang].format(**p) if spec["summary"]
               else reasons.get(lang) or reasons.get("en") or f.get("summary", ""))
    return {
        "field": spec["field"][lang],
        "title": spec["title"][lang].format(**p),
        "summary": summary,
        "fix": spec["fix"][lang].format(**p),
        "checker": CHECKER[spec["checker"]][lang],
    }

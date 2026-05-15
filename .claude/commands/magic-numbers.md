Analyze $ARGUMENTS for magic numbers and magic strings. Suggest named constants.

## Шалгах зүйлс

1. **Magic numbers** — кодон дотор шууд бичсэн тоо (0, 1, True, None биш бусад)
   - Жишээ: `200`, `950`, `10000`, `0.85`
2. **Magic strings** — давтагддаг текст утга
   - Status, role, type нэрс: `"pending"`, `"admin"`, `"super_user"`
   - Error message-ууд олон газар нэг ижил
3. **HTTP status code** — `200`, `400`, `404` гэх мэт

## Хариултын формат

Magic value бүрд:

```
## <утга> олдсон газрууд

- <файл:мөр> — context
- <файл:мөр> — context

Санал болгох константын нэр: `<UPPER_SNAKE_CASE>`
Байршил: `app/config/constants.py` эсвэл `app/models/<related>.py`

# Тодорхойлох
<NAME> = <value>

# Ашиглах
if x == <NAME>:
    ...
```

## Дүрэм

- 0, 1, True, False, None, "", [] ЭДГЭЭР НЬ magic биш — алгасах
- HTTP status code-ыг Flask `http.HTTPStatus` Enum-ээс авч болно
- Status/role гэх мэт олонлогийг class дотор бүлэглэх: `class LoanStatus: PENDING = "pending"`
- Константын нэр `UPPER_SNAKE_CASE`, утгыг тайлбарласан байх
- Хэрэв magic value олдоогүй бол ✅ "Энэ файлд magic value алга" гэж бичих

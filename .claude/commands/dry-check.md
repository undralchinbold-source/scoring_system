Analyze $ARGUMENTS (file OR folder) for duplicated code blocks. Apply DRY principle.

## Шалгах зүйлс

1. 3+ мөртэй адил эсвэл бараг адил код блок
2. Адил validation/error handling олон газар давтагдаж байгаа эсэх
3. Адил database query хэв маяг (get_or_404, filter_by + first)
4. Адил response формат (jsonify(...), 200)
5. Адил magic string / status code

## Хариултын формат

Давтагдсан хэв маяг бүрд:

```
## Давтагдсан #N: <товч тайлбар>

Олдсон газрууд:
- <файл:мөр>
- <файл:мөр>

Давтагдсан код:
<example>

Шийдвэр: Helper function `<name>(<params>)` хэлбэрээр гаргах
Байрлуулах файл: `app/<utils|validators|services>/<name>.py`

Refactored:
# helper:
def <name>(...):
    ...
# usage:
<name>(...)
```

## Дүрэм

- 2 удаа давтагдсан → анхаар (магадгүй helper)
- 3+ удаа давтагдсан → заавал helper
- Helper-уудыг зөв байршуулах: validation → `validators/`, business logic → `services/`, generic → `utils/`
- Хэрэв давтагдсан код олдоогүй бол ✅ "Энэ файлд DRY зөрчил алга" гэж бичих

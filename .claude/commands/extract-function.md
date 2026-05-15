Analyze $ARGUMENTS and find functions that are too long (>20 lines).
Suggest concrete Extract Function refactorings.

## Шалгах зүйлс

1. 20+ мөртэй функц байгаа эсэх
2. Функц дотор тодорхой үүрэгтэй хэсгүүд (block-уудыг) ялгах:
   - Input validation (ValueError, шалгалт)
   - Data transformation (feature engineering, mapping)
   - External call (DB, API, model)
   - Output formatting (jsonify, dict build)
3. Хэсэг бүхэн тусдаа функц болж болох эсэх

## Хариултын формат

Функц бүрд:

```
## <function_name> (<N> lines) - <файл:мөр>

Хэсгүүд:
- Lines X-Y:  <зорилго> → шинэ функц: `_<name>(...)` -> <return>
- Lines X-Y:  <зорилго> → шинэ функц: `_<name>(...)` -> <return>

Refactored version (skeleton):
def <function_name>(...):
    _validate_...(...)
    result = _build_...(...)
    return _format_...(result)
```

## Дүрэм

- Шинэ функцийн нэр snake_case, үйл үг-нэр үг (calculate_score, validate_input)
- Private helper-ыг `_` underscore-ээр эхлүүлэх
- Логик өөрчилж болохгүй — зөвхөн бүтэц
- Хэрэв бүх функц 20 мөрөөс богино бол ✅ "Энэ файлд extract function шаардлагагүй" гэж бичих

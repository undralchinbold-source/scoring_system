Analyze $ARGUMENTS for Single Responsibility Principle violations.

## Шалгах зүйлс

1. Функц 2+ үүрэг гүйцэтгэж байгаа эсэх. Үүрэг гэдэг нь:
   - **HTTP layer**: request унших, response буцаах
   - **Validation**: input шалгах, ValueError
   - **Business logic**: бодит тооцоо, шийдвэр
   - **Database**: query, INSERT, UPDATE, DELETE
   - **External call**: API call, file IO, ML inference
   - **Logging / Audit**: log, audit log
2. Route функц route + service-ийн ажлыг хослуулсан эсэх
3. Service функц олон төрлийн entity-тэй ажиллаж байгаа эсэх

## Хариултын формат

Олдсон зөрчил бүрд:

```
## <function_name> - <файл:мөр>

Үүрэг тоо: N
Хийж байгаа ажил:
1. <үүрэг 1> (lines X-Y)
2. <үүрэг 2> (lines X-Y)

Санал болгох хуваалт:
- Route: `app/routes/<file>.py` — зөвхөн HTTP
- Validator: `app/validators/<file>.py` — input шалгалт
- Service: `app/services/<file>.py` — бизнес логик

Refactored skeleton:
# Route
def <name>():
    data = request.get_json()
    <validator>.validate(data)
    result = <service>.<action>(data)
    return jsonify(result), 200
```

## Дүрэм

- scoring_system архитектур: route → validator → service → model
- Route дотор шууд `db.session.commit()` байх нь SRP зөрчил
- Route дотор feature engineering / model inference SRP зөрчил
- 1 функц 3+ үүрэгтэй бол MAJOR, 4+ үүрэгтэй бол BLOCKER
- Хэрэв SRP зөрчил алга бол ✅ "Энэ файл SRP-д нийцсэн" гэж бичих

Analyze $ARGUMENTS for nested if statements (pyramid of doom) and suggest Guard Clause refactoring.

## Шалгах зүйлс

1. 3 эсвэл түүнээс олон давхар nested `if` олох
2. `else: return error` хэлбэрийн хэв маяг олох (Guard Clause-аар сольж болно)
3. Функцийн үндсэн логик нэлээд дотогшоо орсон эсэх

## Хариултын формат

Олдсон pyramid бүрд:

```
## <function_name> - <файл:мөр>

Nesting depth: N давхар

### Өмнө
<original code>

### Дараа (Guard Clause)
<refactored code with early returns>

Учир нь: ...
```

## Дүрэм

- Алдааны нөхцлүүдийг **эхэнд** шалгана, шууд буцаана
- HTTP status code зөв байх: 404 (not found), 409 (conflict), 400 (bad input), 403 (forbidden)
- Үндсэн "happy path" логик функцийн **доор, indent багатай** байна
- Бүх Guard Clause-ийн алдааны мэдээ user-friendly байх
- Хэрэв 3 давхар nested if олдоогүй бол ✅ "Guard Clause шаардлагагүй" гэж бичих

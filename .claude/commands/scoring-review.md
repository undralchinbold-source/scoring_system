Review the ML predict pipeline of this scoring system. Focus: $ARGUMENTS

## Шалгах хэсгүүд

### 🤖 Model Loading
- [ ] Singleton pattern зөв хэрэгжсэн үү (нэг л удаа ачаалдаг уу)
- [ ] Model файл байхгүй бол зөв алдаа буцаадаг уу
- [ ] joblib.load warnings дарагдсан уу

### 📊 Feature Engineering
- [ ] feature_cols дараалал зөв баригдсан уу
- [ ] amount_to_income_ratio, annual_dti, log_income, log_amount зөв тооцоологдсон уу
- [ ] employment_type label encoding зөв уу
- [ ] Тэг эсвэл сөрөг орлогод log() алдаа гарахгүй уу (division by zero)

### 🔄 Preprocessing
- [ ] Scaler зөв дарааллаар ажиллаж байна уу
- [ ] DataFrame-ээр дамжуулж байна уу (numpy array биш — feature name warning)
- [ ] Scaler output-г дахин DataFrame болгосон уу

### 📤 Output
- [ ] predict_proba зөв class index ашиглаж байна уу
- [ ] "approved" class-ын index зөв олдож байна уу
- [ ] decision label decode зөв хийгдэж байна уу

### 🗄️ Database
- [ ] ScoreHistory зөв хадгалагдаж байна уу
- [ ] application_id байхгүй үед null биш алдаа гарахгүй уу
- [ ] created_by user_id зөв дамжигдаж байна уу

### ✅ Validation
- [ ] employment_type EMPLOYMENT_TYPES жагсаалтад байна уу
- [ ] monthly_income, employment_years, requested_amount > 0 уу
- [ ] Алдааны мессеж Монголоор ойлгомжтой уу

## Хариу

Асуудал бүрт:
- ❌ **Файл:мөр** — тайлбар + засах арга

Асуудалгүй бол:
- ✅ Pipeline зөв ажиллаж байна — товч тайлбар

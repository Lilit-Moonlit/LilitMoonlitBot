# Налаштування Meta API для крос-постингу (Instagram & Facebook)

Ця інструкція допоможе вам отримати необхідні ID та токени для вашого бота.

## Крок 1: Створення застосунку в Meta
1. Перейдіть на [Meta for Developers](https://developers.facebook.com/).
2. Натисніть **My Apps** -> **Create App**.
3. Оберіть тип застосунку **Business** (або "Other" -> "Business").
4. Дайте назву (наприклад, `BeautyBot CrossPosting`) та вкажіть вашу пошту.

## Крок 2: Додавання продуктів
У панелі керування застосунком додайте:
- **Instagram Graph API**
- **Facebook Login for Business**

## Крок 3: Отримання токенів через Graph API Explorer
Найшвидший спосіб отримати токен:
1. Перейдіть у [Graph API Explorer](https://developers.facebook.com/tools/explorer/).
2. У полі **Meta App** оберіть ваш створений застосунок.
3. У полі **User or Page** оберіть **Get Page Access Token**. Вам запропонують увійти через Facebook.
4. **ВАЖЛИВО:** Оберіть сторінку Facebook та пов'язаний акаунт Instagram, куди ви хочете постити.
5. Надайте дозволи (Permissions):
   - `instagram_basic`
   - `instagram_content_publish`
   - `pages_read_engagement`
   - `pages_manage_posts`
   - `public_profile`
6. Натисніть **Generate Access Token**.

## Крок 4: Отримання ID
Після отримання токена, натисніть кнопку **(i)** або виконайте запит `GET /me/accounts`, щоб дізнатися:
- `FB_PAGE_ID` (ID вашої сторінки).
- `IG_BUSINESS_ACCOUNT_ID` (ID бізнес-акаунта Instagram). Його можна знайти, зробивши запит `GET /{page-id}?fields=instagram_business_account`.

## Крок 5: Безкінечний (Long-lived) токен
Токен з Explorer діє лише 1-2 години. Щоб отримати токен на 60 днів або "безкінечний":
1. Скористайтеся [Access Token Tool](https://developers.facebook.com/tools/accesstoken/).
2. Або ми використаємо спеціальний URL запит пізніше, щоб оновити ваш токен.

## Крок 6: Додавання в .env
Коли отримаєте дані, впишіть їх у файл `.env` у корені проекту:
```env
META_ACCESS_TOKEN=ваш_токен_тут
FB_PAGE_ID=ваш_id_сторінки
IG_BUSINESS_ACCOUNT_ID=ваш_id_інстаграма
```

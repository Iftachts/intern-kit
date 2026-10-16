# קיט ההתמחות בפסיכולוגיה חינוכית

אתר קריאה למתמחים, בנוי לפי שנות ההתמחות: שנה א' (מתאבנים), שנים ב'-ג' (מנה עיקרית), שנה ד' (קינוח), ולצדן מתווי העבודה, מילון מושגים ומקורות.

## מבנה

| נתיב | תוכן |
|---|---|
| `index.html` | האתר כולו בקובץ אחד (כולל כל התוכן) |
| `files/` | 36 קבצי המקור ב-PDF, שהאתר פותח בקורא המובנה |
| `source/summaries/` | הסיכום המובנה של כל פריט (Markdown) |
| `source/content/` | סקירות התחומים, ארגז הכלים והמילון (Markdown) |
| `source/meta.py` | מפת הפריטים: שנה, תחום, מראה מקום, קישור |
| `source/template.html` | העיצוב והקוד של האתר |
| `source/files_manifest.json`, `source/url_labels.json` | רשימת קבצי ה-PDF ותוויות הקישורים, שהבנייה קוראת |
| `source/build.py` | בניית `index.html` מהתוכן |

## הרצה

פותחים את `index.html` דרך שרת אינטרנט (לא ישירות מהדיסק, כדי שקורא ה-PDF יוכל לטעון את הקבצים), למשל:

```
python3 -m http.server
```

אפשר גם לפרסם את המאגר ב-GitHub Pages (Settings → Pages → Deploy from branch → `main` / root). שימו לב: GitHub Pages של מאגר פרטי זמין רק בחלק מהתוכניות, ואתר Pages הוא ציבורי.

מחוץ ל-Claude, ההתקדמות האישית נשמרת בדפדפן (localStorage).

## עדכון התוכן

עורכים את קובצי ה-Markdown או את `source/meta.py`, ומריצים:

```
pip install "markdown==3.7"
python3 source/build.py
```

הסקריפט בודק שאין הפניות שבורות או רשימות שבורות, ובונה מחדש את `index.html`.

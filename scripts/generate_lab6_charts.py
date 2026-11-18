#!/usr/bin/env python3
"""
Generate analytical calculations, statistical summary, and publication-quality
300 DPI charts for Lab 6: Usability Testing & Prototype Quality Evaluation.
Course: Human-Computer Interaction (ПЧМИ), BSU FPMI, 2026.
Project: Litera - Online Bookstore (Web & Mobile)
"""

import os
import math
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches

# Ensure output directory exists
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "..", "docs", "images")
os.makedirs(OUTPUT_DIR, exist_ok=True)
STATS_PATH = os.path.join(OUTPUT_DIR, "lab6_stats.txt")

plt.rcParams["font.sans-serif"] = ["DejaVu Sans", "Arial", "Helvetica"]
plt.rcParams["axes.unicode_minus"] = False

# Consistent Litera Design System Palette
NAVY = "#0F172A"
ROYAL = "#1E3A8A"
AMBER = "#D97706"
GOLD = "#F59E0B"
TEAL = "#0D9488"
EMERALD = "#10B981"
RED = "#EF4444"
SLATE = "#64748B"
LIGHT_BG = "#F8FAFC"
BORDER = "#CBD5E1"


def adjusted_wald_ci(successes: int, n: int, z: float = 1.96):
    """Adjusted Wald 95% confidence interval for binary task success (Sauro / Lewis)."""
    p_adj = (successes + (z ** 2) / 2.0) / (n + z ** 2)
    se = math.sqrt((p_adj * (1.0 - p_adj)) / (n + z ** 2))
    lo = max(0.0, p_adj - z * se)
    hi = min(1.0, p_adj + z * se)
    return p_adj * 100.0, lo * 100.0, hi * 100.0


# =============================================================================
# 1. USABILITY PERFORMANCE METRICS & LEARNABILITY (N = 8, Tasks T1-T5)
# =============================================================================
tasks_meta = [
    {"id": "T1", "name": "Авторизация и профиль Litera ID", "target_web": 40.0, "target_mob": 45.0, "opt_steps_web": 5, "opt_steps_mob": 5},
    {"id": "T2", "name": "Фасетный поиск + самовывоз <=60 BYN", "target_web": 60.0, "target_mob": 75.0, "opt_steps_web": 6, "opt_steps_mob": 7},
    {"id": "T3", "name": "Карточка, ридер фрагмента, в корзину", "target_web": 75.0, "target_mob": 85.0, "opt_steps_web": 5, "opt_steps_mob": 5},
    {"id": "T4", "name": "Поиск и предзаказ при активном фильтре", "target_web": 90.0, "target_mob": 100.0, "opt_steps_web": 5, "opt_steps_mob": 6},
    {"id": "T5", "name": "Корзина (2 экз.) и полный чекаут", "target_web": 120.0, "target_mob": 130.0, "opt_steps_web": 9, "opt_steps_mob": 9},
]

# Raw test observations per participant R1..R8 (6 students, 1 professor, 1 manager)
# Web data: [T1..T5]
web_binary = np.array([
    [1, 1, 1, 1, 1],  # R1 (Student)
    [1, 1, 1, 1, 1],  # R2 (Student)
    [1, 1, 1, 0, 1],  # R3 (Student - hit #filterPickup + #filterPreorder conflict in T4)
    [1, 1, 1, 1, 1],  # R4 (Student)
    [1, 1, 1, 0, 1],  # R5 (Student - hit T4 conflict)
    [1, 1, 1, 1, 1],  # R6 (Student)
    [1, 0, 1, 0, 1],  # R7 (Professor - missed price slider / filter reset)
    [1, 1, 1, 1, 1],  # R8 (Manager)
], dtype=float)

web_graded = np.array([
    [1.0, 1.0, 1.0, 1.0, 1.0],
    [1.0, 1.0, 1.0, 0.5, 1.0],
    [1.0, 1.0, 1.0, 0.0, 1.0],
    [1.0, 0.5, 1.0, 1.0, 1.0],
    [1.0, 1.0, 1.0, 0.0, 0.5],
    [1.0, 1.0, 1.0, 0.5, 1.0],
    [1.0, 0.5, 1.0, 0.0, 1.0],
    [1.0, 1.0, 1.0, 1.0, 1.0],
], dtype=float)

web_time = np.array([
    [22.0, 36.0, 48.0, 62.0, 68.0],  # R1
    [25.0, 41.0, 52.0, 84.0, 76.0],  # R2
    [24.0, 39.0, 55.0, 118.0, 74.0], # R3 (failed T4 after long struggle)
    [28.0, 58.0, 49.0, 68.0, 71.0],  # R4
    [26.0, 44.0, 58.0, 124.0, 96.0], # R5
    [21.0, 35.0, 46.0, 79.0, 65.0],  # R6
    [37.0, 74.0, 71.0, 132.0, 112.0],# R7
    [23.0, 38.0, 50.0, 66.0, 69.0],  # R8
], dtype=float)

web_errors = np.array([
    [0, 0, 0, 0, 0],
    [0, 0, 0, 1, 0],
    [0, 0, 0, 3, 0],
    [0, 1, 0, 1, 0],
    [0, 0, 0, 3, 1],
    [0, 0, 0, 1, 0],
    [0, 2, 0, 3, 1],
    [0, 0, 0, 0, 0],
], dtype=int)

web_steps_fact = np.array([
    [5, 6, 5, 6, 9],
    [5, 7, 5, 8, 9],
    [5, 6, 5, 11, 10],
    [5, 8, 5, 7, 9],
    [5, 7, 6, 12, 11],
    [5, 6, 5, 8, 9],
    [6, 10, 6, 13, 12],
    [5, 6, 5, 6, 9],
], dtype=float)

# ASQ (After-Scenario Questionnaire, 3 items 1..5 averaged per respondent per task)
web_asq = np.array([
    [4.9, 4.7, 5.0, 3.8, 4.8],
    [4.8, 4.5, 4.9, 3.2, 4.6],
    [4.7, 4.6, 4.8, 2.3, 4.7],
    [4.6, 4.1, 4.9, 3.6, 4.5],
    [4.7, 4.4, 4.7, 2.2, 4.1],
    [5.0, 4.8, 5.0, 3.4, 4.9],
    [4.2, 3.7, 4.5, 2.0, 4.0],
    [4.9, 4.7, 4.9, 3.9, 4.8],
], dtype=float)

# Mobile data: [T1..T5]
mob_binary = np.array([
    [1, 1, 1, 1, 1],  # R1
    [1, 1, 1, 0, 1],  # R2
    [1, 1, 1, 0, 1],  # R3
    [1, 1, 1, 1, 1],  # R4
    [1, 0, 1, 0, 1],  # R5 (didn't expand mobile filter accordion in time)
    [1, 1, 1, 1, 1],  # R6
    [1, 1, 1, 0, 0],  # R7 (failed T4 filter conflict and missed courier address)
    [1, 1, 1, 1, 1],  # R8
], dtype=float)

mob_graded = np.array([
    [1.0, 1.0, 1.0, 1.0, 1.0],
    [1.0, 1.0, 1.0, 0.0, 1.0],
    [1.0, 0.5, 1.0, 0.0, 1.0],
    [1.0, 1.0, 1.0, 0.5, 1.0],
    [1.0, 0.0, 1.0, 0.0, 0.5],
    [1.0, 1.0, 1.0, 1.0, 1.0],
    [1.0, 0.5, 0.5, 0.0, 0.0],
    [1.0, 1.0, 1.0, 0.5, 1.0],
], dtype=float)

mob_time = np.array([
    [26.0, 48.0, 56.0, 74.0, 82.0],
    [29.0, 54.0, 61.0, 115.0, 89.0],
    [28.0, 68.0, 64.0, 126.0, 91.0],
    [32.0, 57.0, 59.0, 92.0, 86.0],
    [31.0, 94.0, 67.0, 134.0, 118.0],
    [25.0, 46.0, 54.0, 83.0, 78.0],
    [43.0, 84.0, 92.0, 146.0, 148.0],
    [27.0, 51.0, 58.0, 88.0, 84.0],
], dtype=float)

mob_errors = np.array([
    [0, 0, 0, 1, 0],
    [0, 0, 0, 2, 0],
    [0, 1, 0, 3, 0],
    [0, 0, 0, 1, 0],
    [0, 2, 0, 3, 1],
    [0, 0, 0, 0, 0],
    [0, 2, 1, 4, 2],
    [0, 0, 0, 1, 0],
], dtype=int)

mob_steps_fact = np.array([
    [5, 7, 5, 8, 9],
    [5, 8, 5, 11, 10],
    [5, 10, 6, 13, 10],
    [5, 8, 5, 9, 9],
    [6, 12, 6, 14, 12],
    [5, 7, 5, 7, 9],
    [7, 11, 8, 15, 14],
    [5, 8, 5, 9, 9],
], dtype=float)

mob_asq = np.array([
    [4.7, 4.4, 4.8, 3.3, 4.5],
    [4.6, 4.2, 4.6, 2.4, 4.4],
    [4.5, 3.8, 4.5, 2.1, 4.3],
    [4.4, 4.3, 4.7, 3.1, 4.4],
    [4.4, 2.8, 4.4, 2.0, 3.8],
    [4.8, 4.6, 4.9, 3.5, 4.6],
    [3.9, 3.2, 3.8, 1.8, 2.9],
    [4.7, 4.4, 4.7, 3.2, 4.5],
], dtype=float)

# Learnability across 5 training scenarios (Control task T5 time & errors, N=8)
learn_iters = np.array([1, 2, 3, 4, 5])
learn_web_time = np.array([124.5, 98.2, 84.0, 74.6, 68.4])
learn_mob_time = np.array([138.0, 112.4, 96.5, 86.2, 79.1])
learn_web_err = np.array([1.75, 1.00, 0.50, 0.25, 0.13])
learn_mob_err = np.array([2.25, 1.38, 0.75, 0.38, 0.25])
learn_web_pass_pct = np.array([50.0, 75.0, 87.5, 100.0, 100.0])   # within 120s target
learn_mob_pass_pct = np.array([37.5, 62.5, 75.0, 87.5, 100.0])   # within 130s target

# =============================================================================
# 2. OFFLINE REVERSE CARD SORTING (N = 8, Screen Testing Method 3 + Menu Tree)
# =============================================================================
ors_tasks = [
    "ORS-1: Каталог жанров (IT / Романы)",
    "ORS-2: Фильтр цены и наличия",
    "ORS-3: Предзаказы новинок",
    "ORS-4: Ознакомительный фрагмент",
    "ORS-5: Избранное / Закладки",
    "ORS-6: Филиалы и пункты самовывоза",
]
# Exact 1st-attempt hits out of 8 respondents (from numbered UI zones)
ors_web_hits = [8, 7, 6, 7, 7, 6]      # 100%, 87.5%, 75.0%, 87.5%, 87.5%, 75.0%
ors_mob_hits = [8, 5, 5, 4, 5, 6]      # 100%, 62.5%, 62.5%, 50.0% (book icon confusion), 62.5% (bookmark), 75.0%
ors_web_pct = [h / 8.0 * 100.0 for h in ors_web_hits]
ors_mob_pct = [h / 8.0 * 100.0 for h in ors_mob_hits]

# =============================================================================
# 3. TREEJACK INFORMATION ARCHITECTURE TESTING (N = 10, 6 Tasks)
# =============================================================================
tj_tasks = [
    {"id": "TJ-1", "name": "Найти IT-новинку по предзаказу"},
    {"id": "TJ-2", "name": "Проверить самовывоз в ТЦ «Галерея»"},
    {"id": "TJ-3", "name": "Открыть ознакомительный фрагмент"},
    {"id": "TJ-4", "name": "Выбрать курьерскую доставку заказа"},
    {"id": "TJ-5", "name": "Проверить трекинг статуса заказа"},
    {"id": "TJ-6", "name": "Найти телефон и режим филиала"},
]
# Counts out of 10 respondents: (Direct Success, Indirect Success, Direct Fail, Indirect Fail, FirstClick%, MedianTime_s)
tj_web_raw = [
    (6, 2, 1, 1, 70.0, 14.2),   # TJ-1: 80% success, 60% direct
    (8, 1, 1, 0, 90.0, 11.5),   # TJ-2: 90% success, 80% direct
    (8, 1, 0, 1, 90.0, 9.8),    # TJ-3: 90% success, 80% direct
    (9, 1, 0, 0, 100.0, 8.4),   # TJ-4: 100% success, 90% direct
    (7, 2, 0, 1, 80.0, 12.1),   # TJ-5: 90% success, 70% direct
    (5, 3, 1, 1, 60.0, 16.8),   # TJ-6: 80% success, 50% direct (split between О нас / Доставка)
]
tj_mob_raw = [
    (5, 2, 2, 1, 60.0, 17.5),   # TJ-1: 70% success
    (6, 2, 1, 1, 70.0, 14.8),   # TJ-2: 80% success
    (5, 2, 2, 1, 50.0, 15.6),   # TJ-3: 70% success (unlabeled book icon confusion)
    (8, 2, 0, 0, 90.0, 10.2),   # TJ-4: 100% success
    (6, 2, 1, 1, 70.0, 14.0),   # TJ-5: 80% success
    (6, 2, 1, 1, 70.0, 15.1),   # TJ-6: 80% success (mobile About Us / Branches screen is clearer)
]

# =============================================================================
# 4. EXPECTATION TESTING (N = 8) & CHECKLISTS (72 Web / 50 Mobile)
# =============================================================================
exp_web_elements = [
    ("Кнопка «В корзину»", 8),
    ("Кнопка «Читать фрагмент»", 8),
    ("Бейдж «Войти» / профиль (Litera ID)", 7),
    ("Чекбокс «В наличии на складе»", 6),
    ("Чекбокс «Твердый переплет» (disabled)", 2),
    ("Пункт «Продавцы [Увед.]» в шапке", 3),
    ("Кнопка «На сингальский» (карточка)", 2),
    ("Опция «Курьер (+8.00 BYN)»", 3),
]
exp_mob_elements = [
    ("Таб-бар «[Корзина] (N)»", 8),
    ("Таб-бар «[Профиль] Войти»", 8),
    ("Таб-бар «[Поиск]»", 7),
    ("Степпер «- / +» в корзине", 7),
    ("Аккордеон «Фильтры каталога»", 6),
    ("Таб-бар иконка [Колокольчик] (без подп.)", 5),
    ("Таб-бар иконка [Закладка] (без подп.)", 5),
    ("Таб-бар иконка [Книга] (без подп.)", 3),
]

# Checklists: (Category, Total, Yes=1, Partial=0.5, No=0)
web_checklist_cats = [
    ("1. Архитектура и навигация", 13, 10, 2, 1),
    ("2. Планировка и дизайн", 9, 8, 1, 0),
    ("3. Содержание и тексты", 9, 7, 1, 1),
    ("4. Формы и взаимодействие", 8, 5, 2, 1),
    ("5. Графика и мультимедиа", 6, 4, 2, 0),
    ("6. Цвета и типографика", 10, 9, 1, 0),
    ("7. Устойчивость к ошибкам", 9, 5, 2, 2),
    ("8. Платформа и доступность", 8, 6, 2, 0),
]
mob_checklist_cats = [
    ("1. Мобильная ИА и навигация", 8, 5, 2, 1),
    ("2. Сенсорная эргономика (Thumb)", 8, 7, 1, 0),
    ("3. Адаптивность и Safe Area", 7, 6, 1, 0),
    ("4. Формы и мобильный ввод", 7, 4, 2, 1),
    ("5. Контент и читаемость", 7, 6, 1, 0),
    ("6. Устойчивость к прерываниям", 7, 4, 2, 1),
    ("7. Производительность и WCAG", 6, 5, 1, 0),
]

# =============================================================================
# 5. GOMS / KLM FOR WEB (12 MODELS: 3 Forms x 2 Variants x 2 Methods)
# =============================================================================
# Constants from manual p. 11 & p. 14:
K_VAL = 0.20  # Keystroke or mouse click after P (per p. 14 Example 2: P M K -> P K)
P_VAL = 1.10  # Pointing with mouse
H_VAL = 0.40  # Homing hand between keyboard and mouse
M_VAL = 1.35  # Mental pause

# Every model: (code, form_id, variant, method, n_H, n_P, n_K, n_M, formula_str)
goms_models = [
    # Form 1: Authorization (Email 10 chars, Password 8 chars, Remember checkbox, Submit)
    ("G1.1", "Форма 1: Авторизация", "Вариант 1А (Базовый)", "Мышь + ввод",
     5, 4, 22, 6, "5H + 4P + 22K + 6M"),
    ("G1.2", "Форма 1: Авторизация", "Вариант 1А (Базовый)", "Клавиатура (Tab)",
     2, 1, 23, 6, "2H + 1P + 23K + 6M"),
    ("G1.3", "Форма 1: Авторизация", "Вариант 1Б (Оптим.)", "Мышь + ввод",
     3, 2, 20, 4, "3H + 2P + 20K + 4M"),
    ("G1.4", "Форма 1: Авторизация", "Вариант 1Б (Оптим.)", "Клавиатура (Tab)",
     0, 0, 20, 4, "0H + 0P + 20K + 4M"),

    # Form 2: Search & Faceted Filters ("Мартин" 6 chars, IT, Pickup, MaxPrice 60)
    ("G2.1", "Форма 2: Поиск и фильтры", "Вариант 2А (Классич.)", "Мышь + ввод",
     5, 6, 14, 8, "5H + 6P + 14K + 8M"),
    ("G2.2", "Форма 2: Поиск и фильтры", "Вариант 2А (Классич.)", "Клавиатура (Tab)",
     2, 1, 17, 7, "2H + 1P + 17K + 7M"),
    ("G2.3", "Форма 2: Поиск и фильтры", "Вариант 2Б (Live UI)", "Мышь + ввод",
     1, 3, 9, 4, "1H + 3P + 9K + 4M"),
    ("G2.4", "Форма 2: Поиск и фильтры", "Вариант 2Б (Live UI)", "Клавиатура (Tab)",
     0, 0, 12, 5, "0H + 0P + 12K + 5M"),

    # Form 3: Checkout (Delivery, Name "Кирилл" 6, Phone 9, Promo "FPMI" 4, Payment, Submit)
    ("G3.1", "Форма 3: Чекаут заказа", "Вариант 3А (Гость)", "Мышь + ввод",
     7, 7, 26, 10, "7H + 7P + 26K + 10M"),
    ("G3.2", "Форма 3: Чекаут заказа", "Вариант 3А (Гость)", "Клавиатура (Tab)",
     2, 1, 28, 9, "2H + 1P + 28K + 9M"),
    ("G3.3", "Форма 3: Чекаут заказа", "Вариант 3Б (Litera ID)", "Мышь + ввод",
     3, 3, 7, 4, "3H + 3P + 7K + 4M"),
    ("G3.4", "Форма 3: Чекаут заказа", "Вариант 3Б (Litera ID)", "Клавиатура (Tab)",
     0, 0, 5, 2, "0H + 0P + 5K + 2M"),
]

goms_computed = []
for code, form, var, meth, nH, nP, nK, nM, fstr in goms_models:
    tH = nH * H_VAL
    tP = nP * P_VAL
    tK = nK * K_VAL
    tM = nM * M_VAL
    tot = tH + tP + tK + tM
    goms_computed.append({
        "code": code, "form": form, "var": var, "meth": meth,
        "nH": nH, "nP": nP, "nK": nK, "nM": nM, "formula": fstr,
        "tH": tH, "tP": tP, "tK": tK, "tM": tM, "total": tot
    })

# =============================================================================
# 6. TLM / FLM FOR MOBILE (3 Forms x 2 Variants = 6 Models)
# =============================================================================
# Touchscreen operators:
T_VAL = 0.28   # Tapping / virtual key tap
PT_VAL = 0.65  # Finger pointing to new target zone
F_VAL = 0.42   # Flicking / quick swipe
D_VAL = 0.85   # Dragging slider / scroll
GB_VAL = 0.80  # Biometric Face ID / OS autofill confirmation
# M_VAL = 1.35

# (code, form, variant, n_T, n_PT, n_F, n_D, n_GB, n_M, emp_time_s)
tlm_models = [
    ("TLM-1А", "Моб. форма 1: Вход (SMS)", "Вариант А (Ручной QWERTY)", 15, 2, 0, 0, 0, 3, 9.8),
    ("TLM-1Б", "Моб. форма 1: Вход (SMS)", "Вариант Б (Autofill + Face ID)", 3, 2, 0, 0, 1, 2, 5.8),
    ("TLM-2А", "Моб. форма 2: Поиск/Фильтр", "Вариант А (Слайдер + Аккордеон)", 10, 4, 1, 1, 0, 5, 13.7),
    ("TLM-2Б", "Моб. форма 2: Поиск/Фильтр", "Вариант Б (Bottom Sheet + Чипы)", 9, 3, 1, 0, 0, 3, 9.3),
    ("TLM-3А", "Моб. форма 3: Моб. чекаут", "Вариант А (Скролл + Ручной ввод)", 14, 5, 0, 2, 0, 6, 17.6),
    ("TLM-3Б", "Моб. форма 3: Моб. чекаут", "Вариант Б (Apple/Белкарт Pay)", 3, 2, 0, 0, 1, 2, 5.9),
]

tlm_computed = []
for code, form, var, nT, nPT, nF, nD, nGB, nM, emp in tlm_models:
    tT = nT * T_VAL
    tPT = nPT * PT_VAL
    tF = nF * F_VAL
    tD = nD * D_VAL
    tGB = nGB * GB_VAL
    tM = nM * M_VAL
    tot = tT + tPT + tF + tD + tGB + tM
    tlm_computed.append({
        "code": code, "form": form, "var": var,
        "nT": nT, "nPT": nPT, "nF": nF, "nD": nD, "nGB": nGB, "nM": nM,
        "tT": tT, "tPT": tPT, "tF": tF, "tD": tD, "tGB": tGB, "tM": tM,
        "total": tot, "emp": emp
    })

# =============================================================================
# 7. SUS (SYSTEM USABILITY SCALE) & COMBINED METRICS (N = 8, Web & Mobile)
# =============================================================================
# 10 items (1..5): odd = positive (score-1), even = negative (5-score)
sus_web_raw = np.array([
    [5, 1, 5, 1, 4, 2, 5, 1, 5, 2],  # R1 -> 87.5
    [5, 2, 4, 1, 5, 2, 4, 1, 5, 2],  # R2 -> 82.5
    [4, 2, 5, 2, 4, 2, 5, 2, 4, 2],  # R3 -> 75.0
    [5, 1, 5, 1, 5, 1, 5, 2, 4, 1],  # R4 -> 92.5
    [4, 2, 4, 2, 4, 2, 5, 2, 4, 2],  # R5 -> 72.5
    [5, 1, 5, 1, 5, 1, 5, 1, 5, 1],  # R6 -> 100.0
    [4, 2, 4, 2, 4, 2, 4, 2, 4, 3],  # R7 -> 72.5
    [5, 1, 5, 1, 5, 1, 5, 1, 5, 2],  # R8 -> 97.5
])
sus_mob_raw = np.array([
    [5, 2, 4, 1, 5, 2, 4, 1, 5, 2],  # R1 -> 82.5
    [4, 2, 4, 2, 4, 2, 5, 2, 4, 2],  # R2 -> 72.5
    [4, 2, 4, 2, 4, 2, 4, 2, 4, 2],  # R3 -> 70.0
    [5, 1, 4, 1, 5, 2, 5, 2, 4, 1],  # R4 -> 87.5
    [4, 3, 4, 2, 4, 2, 4, 2, 4, 2],  # R5 -> 67.5
    [5, 1, 5, 1, 5, 1, 5, 1, 4, 1],  # R6 -> 97.5
    [3, 2, 4, 3, 4, 2, 4, 2, 4, 3],  # R7 -> 62.5
    [5, 1, 5, 2, 5, 1, 5, 1, 4, 2],  # R8 -> 92.5
])


def calc_sus_scores(matrix):
    scores = []
    for row in matrix:
        odd_sum = sum(row[i] - 1 for i in [0, 2, 4, 6, 8])
        even_sum = sum(5 - row[i] for i in [1, 3, 5, 7, 9])
        scores.append(2.5 * (odd_sum + even_sum))
    return np.array(scores, dtype=float)


sus_web_scores = calc_sus_scores(sus_web_raw)
sus_mob_scores = calc_sus_scores(sus_mob_raw)

# Combined Metric 1: Goal-based (Completion >= 80% [>=4/5], Mean Time <= 75s Web / <= 85s Mob, SUS >= 75)
web_user_comp = web_binary.mean(axis=1) * 100.0
web_user_time = web_time.mean(axis=1)
web_goal_met = ((web_user_comp >= 80.0) & (web_user_time <= 75.0) & (sus_web_scores >= 75.0)).astype(int)

mob_user_comp = mob_binary.mean(axis=1) * 100.0
mob_user_time = mob_time.mean(axis=1)
mob_goal_met = ((mob_user_comp >= 80.0) & (mob_user_time <= 85.0) & (sus_mob_scores >= 75.0)).astype(int)


# Combined Metric 2: Percentage normalization (Manual p. 23 Rules 1-4)
def combined_percent_metrics(binary_mat, time_mat, err_mat, sus_vec):
    comp_p = binary_mat.mean(axis=1) * 100.0  # Rule 2: A/Max * 100 (Max=5 tasks -> mean*100)
    sus_p = sus_vec                           # Rule 1: 0..100 -> P = A%
    user_err = err_mat.sum(axis=1).astype(float)
    err_max = np.max(user_err)
    err_p = (1.0 - user_err / err_max) * 100.0 if err_max > 0 else np.full_like(user_err, 100.0)  # Rule 3
    user_time = time_mat.mean(axis=1)
    time_min = np.min(user_time)
    time_p = (time_min / user_time) * 100.0   # Rule 4
    unweighted = (comp_p + sus_p + err_p + time_p) / 4.0
    weighted = 0.35 * comp_p + 0.25 * time_p + 0.20 * err_p + 0.20 * sus_p
    return comp_p, sus_p, err_p, time_p, unweighted, weighted


w_comp_p, w_sus_p, w_err_p, w_time_p, w_unw, w_wgt = combined_percent_metrics(web_binary, web_time, web_errors, sus_web_scores)
m_comp_p, m_sus_p, m_err_p, m_time_p, m_unw, m_wgt = combined_percent_metrics(mob_binary, mob_time, mob_errors, sus_mob_scores)

# Combined Metric 3: Z-scores across all N=16 sessions (8 Web + 8 Mobile)
all_comp = np.concatenate([web_user_comp, mob_user_comp])
all_time_neg = -np.concatenate([web_user_time, mob_user_time])  # inverted so higher = better
all_err_neg = -np.concatenate([web_errors.sum(axis=1), mob_errors.sum(axis=1)])
all_sus = np.concatenate([sus_web_scores, sus_mob_scores])


def z_norm(arr):
    return (arr - np.mean(arr)) / np.std(arr, ddof=1)


z_comp = z_norm(all_comp)
z_time = z_norm(all_time_neg)
z_err = z_norm(all_err_neg)
z_sus = z_norm(all_sus)
z_composite = (z_comp + z_time + z_err + z_sus) / 4.0

# Combined Metric 4: SUM (Single Usability Metric) per task T1..T5 (Manual p. 24-25)
def calc_sum_per_task(bin_mat, time_mat, err_mat, asq_mat, targets):
    sums = []
    comp_pcts = bin_mat.mean(axis=0) * 100.0
    sat_pcts = (asq_mat.mean(axis=0) / 5.0) * 100.0
    time_pcts = []
    err_pcts = []
    for j in range(bin_mat.shape[1]):
        t_ok = np.mean(time_mat[:, j] <= targets[j]) * 100.0
        # Error-free rate or (1 - errors / max_possible_errors_in_task)
        max_e = max(int(np.max(err_mat[:, j])), 1)
        e_score = (1.0 - np.mean(err_mat[:, j]) / max_e) * 100.0
        time_pcts.append(t_ok)
        err_pcts.append(e_score)
        sums.append((comp_pcts[j] + sat_pcts[j] + t_ok + e_score) / 4.0)
    return comp_pcts, np.array(time_pcts), np.array(err_pcts), sat_pcts, np.array(sums)


w_targets = [t["target_web"] for t in tasks_meta]
m_targets = [t["target_mob"] for t in tasks_meta]
w_sum_parts = calc_sum_per_task(web_binary, web_time, web_errors, web_asq, w_targets)
m_sum_parts = calc_sum_per_task(mob_binary, mob_time, mob_errors, mob_asq, m_targets)


# =============================================================================
# SAVE EXACT TEXT SUMMARY FOR REPORT CONSISTENCY
# =============================================================================
with open(STATS_PATH, "w", encoding="utf-8") as f:
    f.write("========================================================================\n")
    f.write("LITERA LAB 6 STATISTICAL SUMMARY (AUTO-GENERATED)\n")
    f.write("========================================================================\n\n")

    f.write("--- 1. PERFORMANCE METRICS (N=8 per platform) ---\n")
    for j, tm in enumerate(tasks_meta):
        ws = int(web_binary[:, j].sum())
        ms = int(mob_binary[:, j].sum())
        wp, wlo, whi = adjusted_wald_ci(ws, 8)
        mp, mlo, mhi = adjusted_wald_ci(ms, 8)
        w_t_in = int(np.sum(web_time[:, j] <= tm["target_web"]))
        m_t_in = int(np.sum(mob_time[:, j] <= tm["target_mob"]))
        w_eff = (tm["opt_steps_web"] / np.mean(web_steps_fact[:, j])) * 100.0
        m_eff = (tm["opt_steps_mob"] / np.mean(mob_steps_fact[:, j])) * 100.0
        f.write(
            f"{tm['id']} ({tm['name']}):\n"
            f"  WEB: Binary={ws}/8 ({ws/8*100:.1f}%), AdjWald={wp:.1f}% [{wlo:.1f}%, {whi:.1f}%], "
            f"Graded={web_graded[:, j].mean()*100:.1f}%, Time={web_time[:, j].mean():.1f}±{web_time[:, j].std():.1f}s "
            f"(Med={np.median(web_time[:, j]):.1f}s, InTarget={w_t_in}/8={w_t_in/8*100:.1f}%), "
            f"Errors={web_errors[:, j].sum()} ({web_errors[:, j].mean():.2f}/user), Eff={w_eff:.1f}%, ASQ={web_asq[:, j].mean():.2f}\n"
            f"  MOB: Binary={ms}/8 ({ms/8*100:.1f}%), AdjWald={mp:.1f}% [{mlo:.1f}%, {mhi:.1f}%], "
            f"Graded={mob_graded[:, j].mean()*100:.1f}%, Time={mob_time[:, j].mean():.1f}±{mob_time[:, j].std():.1f}s "
            f"(Med={np.median(mob_time[:, j]):.1f}s, InTarget={m_t_in}/8={m_t_in/8*100:.1f}%), "
            f"Errors={mob_errors[:, j].sum()} ({mob_errors[:, j].mean():.2f}/user), Eff={m_eff:.1f}%, ASQ={mob_asq[:, j].mean():.2f}\n"
        )
    f.write(f"WEB Overall Binary Success: {web_binary.mean()*100:.1f}%, Graded: {web_graded.mean()*100:.1f}%, Mean Time: {web_time.mean():.1f}s, Total Errors: {web_errors.sum()}\n")
    f.write(f"MOB Overall Binary Success: {mob_binary.mean()*100:.1f}%, Graded: {mob_graded.mean()*100:.1f}%, Mean Time: {mob_time.mean():.1f}s, Total Errors: {mob_errors.sum()}\n\n")

    # Discrete time buckets across all 40 task attempts (8 users x 5 tasks)
    buckets = [(0, 30, "<30s"), (30, 60, "30-60s"), (60, 90, "60-90s"), (90, 120, "90-120s"), (120, 999, ">120s")]
    f.write("Discrete Time Intervals (all 40 attempts = 8 users x 5 tasks):\n")
    for lo_b, hi_b, lbl in buckets:
        wc = int(np.sum((web_time >= lo_b) & (web_time < hi_b)))
        mc = int(np.sum((mob_time >= lo_b) & (mob_time < hi_b)))
        f.write(f"  {lbl:8s}: Web={wc}/40 ({wc/40*100:.1f}%), Mob={mc}/40 ({mc/40*100:.1f}%)\n")
    f.write("\n")

    f.write("--- 2. OFFLINE REVERSE CARD SORTING (N=8) ---\n")
    for lbl, wh, wp, mh, mp in zip(ors_tasks, ors_web_hits, ors_web_pct, ors_mob_hits, ors_mob_pct):
        f.write(f"  {lbl:42s}: Web={wh}/8 ({wp:.1f}%), Mob={mh}/8 ({mp:.1f}%)\n")
    f.write(f"  Overall Mean: Web={np.mean(ors_web_pct):.1f}%, Mob={np.mean(ors_mob_pct):.1f}%\n\n")

    f.write("--- 3. TREEJACK IA TESTING (N=10) ---\n")
    for tmeta, wr, mr in zip(tj_tasks, tj_web_raw, tj_mob_raw):
        wsuc = (wr[0] + wr[1]) * 10
        wdir = (wr[0] / (wr[0] + wr[1])) * 100.0
        msuc = (mr[0] + mr[1]) * 10
        mdir = (mr[0] / (mr[0] + mr[1])) * 100.0
        f.write(
            f"  {tmeta['id']} {tmeta['name']:38s} | "
            f"WEB: Suc={wsuc}% Dir={wdir:.1f}% (D={wr[0]}, I={wr[1]}, DF={wr[2]}, IF={wr[3]}) 1stClick={wr[4]:.0f}% T={wr[5]:.1f}s | "
            f"MOB: Suc={msuc}% Dir={mdir:.1f}% (D={mr[0]}, I={mr[1]}, DF={mr[2]}, IF={mr[3]}) 1stClick={mr[4]:.0f}% T={mr[5]:.1f}s\n"
        )
    w_tj_suc = np.mean([(r[0] + r[1]) * 10 for r in tj_web_raw])
    w_tj_dir = np.mean([r[0] / (r[0] + r[1]) * 100 for r in tj_web_raw])
    m_tj_suc = np.mean([(r[0] + r[1]) * 10 for r in tj_mob_raw])
    m_tj_dir = np.mean([r[0] / (r[0] + r[1]) * 100 for r in tj_mob_raw])
    f.write(f"  Overall Treejack: WEB Success={w_tj_suc:.1f}%, Directness={w_tj_dir:.1f}% | MOB Success={m_tj_suc:.1f}%, Directness={m_tj_dir:.1f}%\n\n")

    f.write("--- 4. EXPECTATION TESTING (N=8) & CHECKLISTS ---\n")
    for name, hits in exp_web_elements:
        f.write(f"  WEB Expect | {name:40s}: {hits}/8 ({hits/8*100:.1f}%)\n")
    f.write(f"  WEB Expect Overall: {np.mean([h/8*100 for _, h in exp_web_elements]):.1f}%\n")
    for name, hits in exp_mob_elements:
        f.write(f"  MOB Expect | {name:40s}: {hits}/8 ({hits/8*100:.1f}%)\n")
    f.write(f"  MOB Expect Overall: {np.mean([h/8*100 for _, h in exp_mob_elements]):.1f}%\n")

    w_tot_pts = sum(y + 0.5 * p for _, _, y, p, _ in web_checklist_cats)
    w_tot_cnt = sum(tot for _, tot, _, _, _ in web_checklist_cats)
    m_tot_pts = sum(y + 0.5 * p for _, _, y, p, _ in mob_checklist_cats)
    m_tot_cnt = sum(tot for _, tot, _, _, _ in mob_checklist_cats)
    f.write(f"  WEB Checklist: {w_tot_pts:.1f}/{w_tot_cnt} ({w_tot_pts/w_tot_cnt*100:.1f}%)\n")
    for cat, tot, y, p, n_no in web_checklist_cats:
        pts = y + 0.5 * p
        f.write(f"    {cat:34s}: {pts:4.1f}/{tot} ({pts/tot*100:5.1f}%) [Y={y}, P={p}, N={n_no}]\n")
    f.write(f"  MOB Checklist: {m_tot_pts:.1f}/{m_tot_cnt} ({m_tot_pts/m_tot_cnt*100:.1f}%)\n")
    for cat, tot, y, p, n_no in mob_checklist_cats:
        pts = y + 0.5 * p
        f.write(f"    {cat:34s}: {pts:4.1f}/{tot} ({pts/tot*100:5.1f}%) [Y={y}, P={p}, N={n_no}]\n")
    f.write("\n")

    f.write("--- 5. GOMS / KLM 12 WEB MODELS ---\n")
    for g in goms_computed:
        f.write(
            f"  {g['code']} | {g['form']:25s} | {g['var']:22s} | {g['meth']:16s} | "
            f"{g['formula']:20s} = H:{g['tH']:.2f} + P:{g['tP']:.2f} + K:{g['tK']:.2f} + M:{g['tM']:.2f} = {g['total']:.2f} s\n"
        )
    f.write("\n")

    f.write("--- 6. TLM / FLM 6 MOBILE MODELS ---\n")
    for t in tlm_computed:
        f.write(
            f"  {t['code']} | {t['form']:27s} | {t['var']:32s} | "
            f"T:{t['nT']} PT:{t['nPT']} F:{t['nF']} D:{t['nD']} GB:{t['nGB']} M:{t['nM']} => {t['total']:.2f} s (Emp={t['emp']:.1f} s)\n"
        )
    f.write("\n")

    f.write("--- 7. SUS, COMBINED METRICS & SUM ---\n")
    f.write(f"  WEB SUS per user: {[float(x) for x in sus_web_scores]} | Mean={sus_web_scores.mean():.2f}, SD={sus_web_scores.std(ddof=1):.2f}\n")
    f.write(f"  MOB SUS per user: {[float(x) for x in sus_mob_scores]} | Mean={sus_mob_scores.mean():.2f}, SD={sus_mob_scores.std(ddof=1):.2f}\n")
    f.write(f"  Goal-based Combined: WEB={web_goal_met.sum()}/8 ({web_goal_met.mean()*100:.1f}%), MOB={mob_goal_met.sum()}/8 ({mob_goal_met.mean()*100:.1f}%)\n")
    f.write(f"  Percentage Combined (Unweighted): WEB={w_unw.mean():.1f}%, MOB={m_unw.mean():.1f}%\n")
    f.write(f"  Percentage Combined (Weighted):   WEB={w_wgt.mean():.1f}%, MOB={m_wgt.mean():.1f}%\n")
    f.write(f"  Z-Score Composite Means: WEB z={z_composite[:8].mean():+.3f}, MOB z={z_composite[8:].mean():+.3f} (Grand={z_composite.mean():.3f})\n")
    f.write("  SUM per task:\n")
    for j, tm in enumerate(tasks_meta):
        f.write(f"    {tm['id']}: WEB SUM={w_sum_parts[4][j]:.1f}% (C={w_sum_parts[0][j]:.1f}, T={w_sum_parts[1][j]:.1f}, E={w_sum_parts[2][j]:.1f}, S={w_sum_parts[3][j]:.1f}) | "
                f"MOB SUM={m_sum_parts[4][j]:.1f}% (C={m_sum_parts[0][j]:.1f}, T={m_sum_parts[1][j]:.1f}, E={m_sum_parts[2][j]:.1f}, S={m_sum_parts[3][j]:.1f})\n")
    f.write(f"  Overall Mean SUM: WEB={w_sum_parts[4].mean():.1f}%, MOB={m_sum_parts[4].mean():.1f}%\n")

print(f"Saved stats summary: {STATS_PATH}")


# =============================================================================
# CHART 1: PERFORMANCE METRICS & LEARNABILITY (lab6_performance_learnability.png)
# =============================================================================
fig, axes = plt.subplots(1, 3, figsize=(18, 6.2), dpi=300)

# Panel A: Task Success + 95% Adjusted Wald CI
ax = axes[0]
x = np.arange(len(tasks_meta))
width = 0.35
w_raw = [web_binary[:, j].mean() * 100.0 for j in range(5)]
m_raw = [mob_binary[:, j].mean() * 100.0 for j in range(5)]
w_wald = [adjusted_wald_ci(int(web_binary[:, j].sum()), 8) for j in range(5)]
m_wald = [adjusted_wald_ci(int(mob_binary[:, j].sum()), 8) for j in range(5)]

w_err_bars = [[max(0.0, r - lo) for r, (_, lo, _) in zip(w_raw, w_wald)],
              [max(0.0, hi - r) for r, (_, _, hi) in zip(w_raw, w_wald)]]
m_err_bars = [[max(0.0, r - lo) for r, (_, lo, _) in zip(m_raw, m_wald)],
              [max(0.0, hi - r) for r, (_, _, hi) in zip(m_raw, m_wald)]]

b1 = ax.bar(x - width/2, w_raw, width, yerr=w_err_bars, capsize=4, color=ROYAL, edgecolor=NAVY, label="Litera Web", error_kw=dict(ecolor=NAVY, lw=1.2))
b2 = ax.bar(x + width/2, m_raw, width, yerr=m_err_bars, capsize=4, color=TEAL, edgecolor=NAVY, label="Litera Mobile", error_kw=dict(ecolor=NAVY, lw=1.2))
ax.axhline(85.0, color=RED, linestyle="--", lw=1.6, label="Целевой порог KPI (85%)")
ax.set_xticks(x)
ax.set_xticklabels([t["id"] for t in tasks_meta], fontweight="bold", fontsize=10.5)
ax.set_ylim(0, 130)
ax.set_ylabel("Бинарный успех задания (%)", fontsize=10.5, fontweight="bold")
ax.set_title("А. Успешность (Task Success)\nс 95% ДИ (метод Вальда, N=8)", fontsize=11.5, fontweight="bold", color=NAVY, pad=10)
ax.grid(axis="y", linestyle=":", alpha=0.7)
ax.legend(loc="upper right", ncol=2, fontsize=7.8, framealpha=0.95)
for bar, val in zip(b1, w_raw):
    lbl = f"{val:.0f}%" if val in (50.0, 100.0) else f"{val:.1f}%"
    ax.text(bar.get_x() + bar.get_width()/2 - 0.02, min(val + 2.5, 108), lbl, ha="center", va="bottom", fontsize=7.0, fontweight="bold", color=ROYAL,
            bbox=dict(boxstyle="square,pad=0.05", fc="white", ec="none", alpha=0.75))
for bar, val in zip(b2, m_raw):
    lbl = f"{val:.0f}%" if val in (50.0, 100.0) else f"{val:.1f}%"
    ax.text(bar.get_x() + bar.get_width()/2 + 0.02, min(val + 2.5, 108), lbl, ha="center", va="bottom", fontsize=7.0, fontweight="bold", color=TEAL,
            bbox=dict(boxstyle="square,pad=0.05", fc="white", ec="none", alpha=0.75))

# Panel B: Time-on-Task vs Targets
ax = axes[1]
w_tmean = web_time.mean(axis=0)
m_tmean = mob_time.mean(axis=0)
w_tstd = web_time.std(axis=0)
m_tstd = mob_time.std(axis=0)

b3 = ax.bar(x - width/2, w_tmean, width, yerr=w_tstd, capsize=3, color=ROYAL, alpha=0.9, edgecolor=NAVY, label="Web: среднее время ± σ")
b4 = ax.bar(x + width/2, m_tmean, width, yerr=m_tstd, capsize=3, color=TEAL, alpha=0.9, edgecolor=NAVY, label="Mobile: среднее время ± σ")
ax.plot(x, w_targets, "o--", color=AMBER, lw=2.0, markersize=6, label="Норматив Web (сек)")
ax.plot(x, m_targets, "s:", color=RED, lw=1.8, markersize=5, label="Норматив Mobile (сек)")
ax.set_xticks(x)
ax.set_xticklabels([t["id"] for t in tasks_meta], fontweight="bold", fontsize=10.5)
ax.set_ylim(0, 162)
ax.set_ylabel("Время выполнения (сек)", fontsize=10.5, fontweight="bold")
ax.set_title("Б. Время выполнения (Time-on-Task)\nв сравнении с целевым порогом", fontsize=11.5, fontweight="bold", color=NAVY, pad=10)
ax.grid(axis="y", linestyle=":", alpha=0.7)
ax.legend(loc="upper left", fontsize=8, framealpha=0.95)
for idx in range(5):
    ax.text(x[idx] - width/2, w_tmean[idx] + w_tstd[idx] + 3, f"{w_tmean[idx]:.0f}с", ha="center", fontsize=7.5, fontweight="bold", color=ROYAL,
            bbox=dict(boxstyle="square,pad=0.05", fc="white", ec="none", alpha=0.8))
    ax.text(x[idx] + width/2, m_tmean[idx] + m_tstd[idx] + 3, f"{m_tmean[idx]:.0f}с", ha="center", fontsize=7.5, fontweight="bold", color=TEAL,
            bbox=dict(boxstyle="square,pad=0.05", fc="white", ec="none", alpha=0.8))

# Panel C: Learnability Curves (5 iterations)
ax = axes[2]
ax.plot(learn_iters, learn_web_time, "o-", color=ROYAL, lw=2.5, markersize=7, label="Web: время задания T5 (сек)")
ax.plot(learn_iters, learn_mob_time, "s-", color=TEAL, lw=2.5, markersize=7, label="Mobile: время задания T5 (сек)")
ax.axhline(120.0, color=AMBER, linestyle="--", lw=1.4, label="Порог Web (120 с)")
ax.set_xticks(learn_iters)
ax.set_xticklabels([f"Сцен. {i}" for i in learn_iters], fontsize=9.5, fontweight="bold")
ax.set_ylim(40, 165)
ax.set_ylabel("Среднее время (сек)", fontsize=10.5, fontweight="bold", color=NAVY)
ax.set_title("В. Кривая обучаемости (Learnability)\nза 5 тренировочных сценариев", fontsize=11.5, fontweight="bold", color=NAVY, pad=10)
ax.grid(True, linestyle=":", alpha=0.7)

ax_err = ax.twinx()
ax_err.plot(learn_iters, learn_web_err, "^--", color=AMBER, lw=1.8, markersize=6, label="Web: ср. ошибок")
ax_err.plot(learn_iters, learn_mob_err, "d--", color=RED, lw=1.8, markersize=6, label="Mobile: ср. ошибок")
ax_err.set_ylim(0, 3.0)
ax_err.set_ylabel("Среднее число ошибок", fontsize=10, fontweight="bold", color=RED)

lines1, labels1 = ax.get_legend_handles_labels()
lines2, labels2 = ax_err.get_legend_handles_labels()
ax.legend(lines1 + lines2, labels1 + labels2, loc="upper right", fontsize=7.8, framealpha=0.95)

fig.suptitle("Показатели производительности и обучаемости прототипа «Litera» (Usability-тест, N=8)", fontsize=14, fontweight="bold", color=NAVY, y=0.99)
plt.tight_layout(rect=[0, 0, 1, 0.94])
p1 = os.path.join(OUTPUT_DIR, "lab6_performance_learnability.png")
fig.savefig(p1, dpi=300)
plt.close(fig)
print(f"Saved: {p1}")


# =============================================================================
# CHART 2: OFFLINE REVERSE CARD SORTING (lab6_offline_reverse_sorting.png)
# =============================================================================
fig, (ax_map, ax_bar) = plt.subplots(1, 2, figsize=(16.5, 6.8), dpi=300, gridspec_kw={"width_ratios": [1.15, 1.0]})

# Left panel: Numbered screen map diagram (Web + Mobile side by side)
ax_map.set_xlim(0, 100)
ax_map.set_ylim(0, 100)
ax_map.axis("off")
ax_map.set_title("А. Схема пронумерованных зон экранов (Способ 3, оффлайн)", fontsize=12, fontweight="bold", color=NAVY, pad=8)

# Web Screen Mockup (left half x=2..58)
web_bg = patches.FancyBboxPatch((2, 6), 56, 86, boxstyle="round,pad=0.6,rounding_size=2", facecolor="#F8FAFC", edgecolor=NAVY, lw=1.8)
ax_map.add_patch(web_bg)
ax_map.text(30, 94.5, "Веб-интерфейс Litera (1440px)", ha="center", fontsize=10, fontweight="bold", color=ROYAL)

# Web header
ax_map.add_patch(patches.Rectangle((2, 81), 56, 11, facecolor=NAVY))
ax_map.add_patch(patches.Rectangle((3.5, 83), 10, 7, facecolor=AMBER, edgecolor="#FFFFFF", lw=0.8))
ax_map.text(8.5, 86.5, "[1] Litera", ha="center", va="center", color="#FFFFFF", fontsize=7.5, fontweight="bold")
ax_map.add_patch(patches.Rectangle((15, 83), 15, 7, facecolor="#334155", edgecolor="#94A3B8", lw=0.8))
ax_map.text(22.5, 86.5, "[2] Поиск", ha="center", va="center", color="#FFFFFF", fontsize=7.5)
ax_map.add_patch(patches.Rectangle((31, 83), 14, 7, facecolor="#1E293B", edgecolor="#64748B", lw=0.8))
ax_map.text(38, 86.5, "[3] Меню", ha="center", va="center", color="#CBD5E1", fontsize=7.2)
ax_map.add_patch(patches.Rectangle((46, 83), 10.5, 7, facecolor=RED, alpha=0.85, edgecolor="#FFFFFF", lw=0.8))
ax_map.text(51.2, 86.5, "[4] Прод./[5]", ha="center", va="center", color="#FFFFFF", fontsize=6.8, fontweight="bold")

# Web subnav
ax_map.add_patch(patches.Rectangle((2, 73), 56, 7.5, facecolor="#1E293B"))
ax_map.text(30, 76.7, "[6] Категории: Все | Романы | Программирование и IT | Бестселлеры", ha="center", va="center", color="#F8FAFC", fontsize=7)

# Web sidebar + cards
ax_map.add_patch(patches.Rectangle((4, 22), 16, 48, facecolor="#FFFFFF", edgecolor=BORDER, lw=1.2))
ax_map.text(12, 46, "[7]\nСайдбар\nфильтров:\n• Наличие\n• Самовывоз\n• Предзаказ\n• Цена BYN", ha="center", va="center", fontsize=7.2, color=NAVY)

ax_map.add_patch(patches.Rectangle((22, 22), 34, 48, facecolor="#FFFFFF", edgecolor=BORDER, lw=1.2))
ax_map.text(39, 64, "[9] Заголовок и сортировка", ha="center", fontsize=7.5, fontweight="bold", color=ROYAL)
ax_map.add_patch(patches.Rectangle((24, 25), 14, 34, facecolor="#F1F5F9", edgecolor=ROYAL, lw=1.1))
ax_map.text(31, 42, "[8] Карточка\nкниги:\n• Обложка\n• Фрагмент\n• В корзину", ha="center", va="center", fontsize=7, color=NAVY)
ax_map.add_patch(patches.Rectangle((40, 25), 14, 34, facecolor="#F1F5F9", edgecolor=SLATE, lw=1.0))
ax_map.text(47, 42, "[8] Карточка\nиздания #2\n(избранное,\nрейтинг)", ha="center", va="center", fontsize=7, color=SLATE)

# Web footer
ax_map.add_patch(patches.Rectangle((2, 6), 56, 13, facecolor=NAVY))
ax_map.text(30, 12.5, "[10] Футер: Филиалы (Минск ТЦ Галерея), контакты, доставка", ha="center", va="center", color="#F8FAFC", fontsize=7.2)

# Mobile Screen Mockup (right half x=64..98)
mob_bg = patches.FancyBboxPatch((64, 6), 34, 86, boxstyle="round,pad=0.6,rounding_size=3", facecolor="#F8FAFC", edgecolor=NAVY, lw=2.0)
ax_map.add_patch(mob_bg)
ax_map.text(81, 94.5, "Мобильное прил. (390px)", ha="center", fontsize=10, fontweight="bold", color=TEAL)

ax_map.add_patch(patches.Rectangle((64, 82), 34, 10, facecolor=NAVY))
ax_map.text(81, 87, "[1] Litera Logo       [≡]", ha="center", va="center", color="#FFFFFF", fontsize=8, fontweight="bold")
ax_map.add_patch(patches.Rectangle((66, 73), 30, 7, facecolor="#FFFFFF", edgecolor=BORDER))
ax_map.text(81, 76.5, "[2] Строка поиска (сворач.)", ha="center", va="center", color=SLATE, fontsize=7.2)
ax_map.add_patch(patches.Rectangle((66, 64), 30, 7, facecolor="#E2E8F0"))
ax_map.text(81, 67.5, "[3] Чипы жанров (свайп)", ha="center", va="center", color=NAVY, fontsize=7.2)
ax_map.add_patch(patches.Rectangle((66, 54), 30, 8, facecolor="#FEF3C7", edgecolor=AMBER))
ax_map.text(81, 58, "[4] Фильтры / Наши филиалы", ha="center", va="center", color=NAVY, fontsize=7.2, fontweight="bold")
ax_map.add_patch(patches.Rectangle((66, 23), 30, 29, facecolor="#FFFFFF", edgecolor=TEAL, lw=1.2))
ax_map.text(81, 37.5, "[5] Карточка издания\n(обложка, цена,\nкнопка «В корзину»)", ha="center", va="center", fontsize=7.5, color=NAVY)

# Mobile bottom bar (zones 6, 7, 8)
ax_map.add_patch(patches.Rectangle((64, 6), 34, 14, facecolor=NAVY))
ax_map.text(81, 15.8, "Bottom Bar (Thumb Zone):", ha="center", color=GOLD, fontsize=7, fontweight="bold")
ax_map.text(81, 10.0, "[6] Увед.  [7] Закл.  [8] Корз.  [8] Книга", ha="center", color="#FFFFFF", fontsize=6.6, fontweight="bold")

# Right panel: Horizontal bar chart of 1st-attempt accuracy
y = np.arange(len(ors_tasks))
h = 0.36
ax_bar.barh(y - h/2, ors_web_pct, h, color=ROYAL, edgecolor=NAVY, label="Litera Web (ср. 85.4%)")
ax_bar.barh(y + h/2, ors_mob_pct, h, color=TEAL, edgecolor=NAVY, label="Litera Mobile (ср. 68.8%)")
ax_bar.axvline(80.0, color=RED, linestyle="--", lw=1.6, label="Целевой порог ИА (80%)")
ax_bar.set_ylim(len(ors_tasks) - 0.1, -0.7)
ax_bar.set_yticks(y)
ax_bar.set_yticklabels(ors_tasks, fontsize=9, fontweight="bold", color=NAVY)
ax_bar.set_xlim(0, 122)
ax_bar.set_xlabel("Доля точных попаданий с 1-й попытки (%)", fontsize=10, fontweight="bold")
ax_bar.set_title("Б. Точность нахождения разделов (N=8)", fontsize=12, fontweight="bold", color=NAVY, pad=8)
ax_bar.grid(axis="x", linestyle=":", alpha=0.7)
ax_bar.legend(loc="upper center", bbox_to_anchor=(0.5, -0.11), ncol=3, fontsize=8.2, framealpha=0.95)

for idx, (wv, mv) in enumerate(zip(ors_web_pct, ors_mob_pct)):
    ax_bar.text(wv + 1.8, idx - h/2, f"{wv:.1f}%", va="center", fontsize=8.2, fontweight="bold", color=ROYAL,
                bbox=dict(boxstyle="square,pad=0.08", fc="white", ec="none", alpha=0.88))
    ax_bar.text(mv + 1.8, idx + h/2, f"{mv:.1f}%", va="center", fontsize=8.2, fontweight="bold", color=TEAL,
                bbox=dict(boxstyle="square,pad=0.08", fc="white", ec="none", alpha=0.88))

fig.suptitle("Оффлайн обратная карточная сортировка прототипа «Litera» (тестирование экранов)", fontsize=14, fontweight="bold", color=NAVY, y=0.98)
plt.tight_layout(rect=[0, 0.05, 1, 0.94])
p2 = os.path.join(OUTPUT_DIR, "lab6_offline_reverse_sorting.png")
fig.savefig(p2, dpi=300)
plt.close(fig)
print(f"Saved: {p2}")


# =============================================================================
# CHART 3: TREEJACK IA ANALYSIS (lab6_treejack_analysis.png)
# =============================================================================
fig, (ax_stk, ax_pie) = plt.subplots(1, 2, figsize=(17, 7.1), dpi=300, gridspec_kw={"width_ratios": [1.1, 1.0]})

# Left panel: Stacked horizontal outcome bars for TJ-1..TJ-6 (Web & Mobile paired)
labels_tj = []
ds_vals, is_vals, df_vals, if_vals = [], [], [], []
for tmeta, wr, mr in zip(tj_tasks, tj_web_raw, tj_mob_raw):
    labels_tj.append(f"{tmeta['id']} (Web): {tmeta['name']}")
    ds_vals.append(wr[0] * 10); is_vals.append(wr[1] * 10); df_vals.append(wr[2] * 10); if_vals.append(wr[3] * 10)
    labels_tj.append(f"{tmeta['id']} (Mob): {tmeta['name']}")
    ds_vals.append(mr[0] * 10); is_vals.append(mr[1] * 10); df_vals.append(mr[2] * 10); if_vals.append(mr[3] * 10)

y_tj = np.arange(len(labels_tj))
ds_arr = np.array(ds_vals)
is_arr = np.array(is_vals)
df_arr = np.array(df_vals)
if_arr = np.array(if_vals)

ax_stk.barh(y_tj, ds_arr, color=EMERALD, edgecolor=NAVY, lw=0.6, label="Direct Success (Прямой успех)")
ax_stk.barh(y_tj, is_arr, left=ds_arr, color="#86EFAC", edgecolor=NAVY, lw=0.6, label="Indirect Success (С возвратом)")
ax_stk.barh(y_tj, df_arr, left=ds_arr + is_arr, color=RED, edgecolor=NAVY, lw=0.6, label="Direct Fail (Прямой провал)")
ax_stk.barh(y_tj, if_arr, left=ds_arr + is_arr + df_arr, color="#FCA5A5", edgecolor=NAVY, lw=0.6, label="Indirect Fail (С возвратом)")
ax_stk.axvline(80.0, color=NAVY, linestyle="--", lw=1.4, label="Целевой успех (80%)")
ax_stk.invert_yaxis()
ax_stk.set_yticks(y_tj)
ax_stk.set_yticklabels(labels_tj, fontsize=8.2, fontweight="bold", color=NAVY)
ax_stk.set_xlim(0, 108)
ax_stk.set_xlabel("Распределение исходов респондентов (%)", fontsize=10, fontweight="bold")
ax_stk.set_title("А. Результаты Treejack по 6 задачам (Web vs Mobile, N=10)", fontsize=11.5, fontweight="bold", color=NAVY, pad=8)
ax_stk.legend(loc="upper center", bbox_to_anchor=(0.48, -0.10), fontsize=7.8, framealpha=0.95, ncol=3)
for idx in range(len(labels_tj)):
    tot_suc = ds_arr[idx] + is_arr[idx]
    ax_stk.text(101.5, idx, f"{tot_suc:.0f}%", va="center", fontsize=8, fontweight="bold", color=ROYAL if idx % 2 == 0 else TEAL)

# Right panel: Pietree visualization for TJ-1 (Preorder IT book) & TJ-6 (Branches)
ax_pie.set_xlim(0, 100)
ax_pie.set_ylim(0, 100)
ax_pie.axis("off")
ax_pie.set_title("Б. Диаграмма переходов Pietree: Задача TJ-1 (Предзаказ IT-новинки)", fontsize=11.5, fontweight="bold", color=NAVY, pad=8)

# Root node
ax_pie.add_patch(patches.FancyBboxPatch((32, 85), 36, 10, boxstyle="round,pad=0.4,rounding_size=2", facecolor=NAVY, edgecolor=NAVY))
ax_pie.text(50, 90, "Корень: Главная Litera (100%)", ha="center", va="center", color="#FFFFFF", fontsize=9, fontweight="bold")

# Level 1 branches
lvl1 = [
    (4, 54, 28, "Каталог книг\n1-й клик: 60% (6/10)\n+2 возврата => 80%", EMERALD),
    (36, 54, 28, "Предзаказы новинок\n1-й клик: 20% (2/10)\n[Отд. ветка уровня 1]", AMBER),
    (68, 54, 28, "Акции / Бестселлеры\n1-й клик: 20% (2/10)\n[Ложный уход]", RED),
]
for bx, by, bw, txt, col in lvl1:
    ax_pie.annotate("", xy=(bx + bw/2, by + 13), xytext=(50, 85),
                    arrowprops=dict(arrowstyle="->", color=col, lw=2.2))
    ax_pie.add_patch(patches.FancyBboxPatch((bx, by), bw, 13, boxstyle="round,pad=0.3,rounding_size=1.5",
                                            facecolor=LIGHT_BG, edgecolor=col, lw=2.0))
    ax_pie.text(bx + bw/2, by + 6.5, txt, ha="center", va="center", color=NAVY, fontsize=7.6, fontweight="bold")

# Level 2 under Catalog
ax_pie.annotate("", xy=(22, 40), xytext=(18, 54), arrowprops=dict(arrowstyle="->", color=EMERALD, lw=2.2))
ax_pie.add_patch(patches.FancyBboxPatch((6, 28), 32, 12, boxstyle="round,pad=0.3,rounding_size=1.5",
                                        facecolor="#ECFDF5", edgecolor=EMERALD, lw=2.0))
ax_pie.text(22, 34, "Программирование и IT\n(70% переходов в ветке)", ha="center", va="center", color=NAVY, fontsize=8, fontweight="bold")

# Clean backtrack arrow looping cleanly BELOW the Level 1 boxes (y=53.5 -> bow downward)
ax_pie.annotate("", xy=(25, 53.5), xytext=(78, 53.5),
                arrowprops=dict(arrowstyle="->", color=AMBER, lw=1.8, linestyle="--", connectionstyle="arc3,rad=-0.18"))
ax_pie.text(56, 46.5, "Возврат 20% через корень в «Каталог»", fontsize=7.6, fontweight="bold", color=AMBER, ha="center",
            bbox=dict(boxstyle="round,pad=0.2", fc="white", ec=AMBER, lw=0.8))

# Level 3 Destination vs Conflict
ax_pie.annotate("", xy=(22, 18), xytext=(22, 28), arrowprops=dict(arrowstyle="->", color=EMERALD, lw=2.2))
ax_pie.add_patch(patches.FancyBboxPatch((5, 5), 34, 13, boxstyle="round,pad=0.3,rounding_size=1.5",
                                        facecolor=EMERALD, edgecolor=NAVY, lw=1.5))
ax_pie.text(22, 11.5, "ЦЕЛЬ: Предзаказы новинок\nWeb: 80% успех (60% Direct)\nMob: 70% успех (50% Direct)", ha="center", va="center", color="#FFFFFF", fontsize=7.8, fontweight="bold")

# Insight callout box on right bottom
insight_box = patches.FancyBboxPatch((44, 5), 52, 35, boxstyle="round,pad=0.5,rounding_size=2", facecolor="#FEF3C7", edgecolor=AMBER, lw=1.5)
ax_pie.add_patch(insight_box)
ax_pie.text(46, 36.5, "Диагноз Treejack (Web & Mobile):", fontsize=9, fontweight="bold", color=NAVY)
ax_pie.text(46, 20.5,
            "1. Дублирование «Предзаказы новинок» на\n"
            "   уровне 1 (Sitemap) и в фильтре Каталога\n"
            "   снижает Directness в TJ-1 до 75% (Web)\n"
            "   и 71.4% (Mobile).\n"
            "2. Ветка контактов филиалов (TJ-6) размыта\n"
            "   между «О нас», «Доставка» и футером.\n"
            "3. Рекомендация: перенести предзаказы в\n"
            "   единый явный раздел и выделить «Филиалы».",
            fontsize=7.8, color=NAVY, va="center")

fig.suptitle("Тестирование информационной архитектуры в Treejack (OptimalWorkshop, N=10)", fontsize=14, fontweight="bold", color=NAVY, y=0.98)
plt.tight_layout(rect=[0, 0.06, 1, 0.94])
p3 = os.path.join(OUTPUT_DIR, "lab6_treejack_analysis.png")
fig.savefig(p3, dpi=300)
plt.close(fig)
print(f"Saved: {p3}")


# =============================================================================
# CHART 4: EXPECTATION TESTING & CHECKLISTS (lab6_expectation_checklists.png)
# =============================================================================
fig, (ax_exp, ax_chk) = plt.subplots(1, 2, figsize=(17.5, 7.2), dpi=300, gridspec_kw={"width_ratios": [1.05, 1.0]})

# Left panel: Expectation match vs broken expectations
all_exp_labels = [f"[Web] {n}" for n, _ in exp_web_elements] + [f"[Mob] {n}" for n, _ in exp_mob_elements]
all_exp_pct = [h / 8.0 * 100.0 for _, h in exp_web_elements] + [h / 8.0 * 100.0 for _, h in exp_mob_elements]
exp_colors = [EMERALD if p >= 75 else (AMBER if p >= 50 else RED) for p in all_exp_pct]

y_e = np.arange(len(all_exp_labels))
ax_exp.barh(y_e, all_exp_pct, color=exp_colors, edgecolor=NAVY, lw=0.8, height=0.68)
ax_exp.axvline(75.0, color=NAVY, linestyle="--", lw=1.4, label="Порог ясности контрола (75%)")
ax_exp.invert_yaxis()
ax_exp.set_yticks(y_e)
ax_exp.set_yticklabels(all_exp_labels, fontsize=8.0, fontweight="bold", color=NAVY)
ax_exp.set_xlim(0, 114)
ax_exp.set_xlabel("Совпадение ожиданий пользователей с поведением UI (%)", fontsize=9.8, fontweight="bold")
ax_exp.set_title("А. Тестирование ожиданий: выявление «обманутых ожиданий» (N=8)", fontsize=11.5, fontweight="bold", color=NAVY, pad=8)
ax_exp.grid(axis="x", linestyle=":", alpha=0.7)
ax_exp.legend(loc="lower right", fontsize=8.2, framealpha=0.95)
for idx, val in enumerate(all_exp_pct):
    ax_exp.text(val + 1.5, idx, f"{val:.1f}%", va="center", fontsize=8, fontweight="bold", color=NAVY,
                bbox=dict(boxstyle="square,pad=0.06", fc="white", ec="none", alpha=0.88))

# Right panel: Checklists compliance by category (Web 72 items + Mobile 50 items)
chk_labels = [f"Web | {c}" for c, _, _, _, _ in web_checklist_cats] + [f"Mob | {c}" for c, _, _, _, _ in mob_checklist_cats]
chk_pcts = [((y + 0.5 * p) / tot) * 100.0 for _, tot, y, p, _ in web_checklist_cats] + \
           [((y + 0.5 * p) / tot) * 100.0 for _, tot, y, p, _ in mob_checklist_cats]
chk_cols = [ROYAL] * len(web_checklist_cats) + [TEAL] * len(mob_checklist_cats)

y_c = np.arange(len(chk_labels))
ax_chk.barh(y_c, chk_pcts, color=chk_cols, edgecolor=NAVY, lw=0.8, height=0.68)
ax_chk.axvline(85.0, color=RED, linestyle="--", lw=1.5, label="Целевой стандарт качества (85%)")
ax_chk.invert_yaxis()
ax_chk.set_yticks(y_c)
ax_chk.set_yticklabels(chk_labels, fontsize=8.0, fontweight="bold", color=NAVY)
ax_chk.set_xlim(0, 114)
ax_chk.set_xlabel("Соответствие контрольному списку (%)", fontsize=9.8, fontweight="bold")
ax_chk.set_title(f"Б. Оценка по чеклистам: Web ({w_tot_pts/w_tot_cnt*100:.1f}%) и Mobile ({m_tot_pts/m_tot_cnt*100:.1f}%)", fontsize=11.5, fontweight="bold", color=NAVY, pad=8)
ax_chk.grid(axis="x", linestyle=":", alpha=0.7)
ax_chk.legend(loc="lower right", fontsize=8.2, framealpha=0.95)
for idx, val in enumerate(chk_pcts):
    ax_chk.text(val + 1.5, idx, f"{val:.1f}%", va="center", fontsize=8, fontweight="bold", color=chk_cols[idx],
                bbox=dict(boxstyle="square,pad=0.06", fc="white", ec="none", alpha=0.88))

fig.suptitle("Этапы 3 и 4: Тестирование ожиданий и аудит по чеклистам (72 пункта Web + 50 пунктов Mobile)", fontsize=14, fontweight="bold", color=NAVY, y=0.98)
plt.tight_layout(rect=[0, 0, 1, 0.94])
p4 = os.path.join(OUTPUT_DIR, "lab6_expectation_checklists.png")
fig.savefig(p4, dpi=300)
plt.close(fig)
print(f"Saved: {p4}")


# =============================================================================
# CHART 5: 12 GOMS / KLM MODELS FOR WEB (lab6_goms_12_models.png)
# =============================================================================
fig, ax = plt.subplots(figsize=(15.5, 7.2), dpi=300)

codes = [f"{g['code']}\n{g['var'].split('(')[1].replace(')', '')}\n{g['meth'].split(' ')[0]}" for g in goms_computed]
x_g = np.arange(len(goms_computed))
# Visual group spacing: offset groups by small gap
x_pos = np.array([0, 1, 2, 3,  4.6, 5.6, 6.6, 7.6,  9.2, 10.2, 11.2, 12.2])

tK_arr = np.array([g["tK"] for g in goms_computed])
tH_arr = np.array([g["tH"] for g in goms_computed])
tP_arr = np.array([g["tP"] for g in goms_computed])
tM_arr = np.array([g["tM"] for g in goms_computed])
tot_arr = np.array([g["total"] for g in goms_computed])

w_bar = 0.72
ax.bar(x_pos, tK_arr, w_bar, color=ROYAL, edgecolor=NAVY, lw=0.7, label="K (Нажатие клавиш / клик, 0.20 с)")
ax.bar(x_pos, tH_arr, w_bar, bottom=tK_arr, color=TEAL, edgecolor=NAVY, lw=0.7, label="H (Перенос руки, 0.40 с)")
ax.bar(x_pos, tP_arr, w_bar, bottom=tK_arr + tH_arr, color=AMBER, edgecolor=NAVY, lw=0.7, label="P (Наведение мыши, 1.10 с)")
ax.bar(x_pos, tM_arr, w_bar, bottom=tK_arr + tH_arr + tP_arr, color="#94A3B8", edgecolor=NAVY, lw=0.7, label="M (Ментальная пауза, 1.35 с)")

for xp, tot, g in zip(x_pos, tot_arr, goms_computed):
    ax.text(xp, tot + 0.5, f"{tot:.2f} с", ha="center", va="bottom", fontsize=9, fontweight="bold", color=NAVY)

# Group background boxes & headers
s1 = (1.0 - tot_arr[3] / tot_arr[0]) * 100.0
s2 = (1.0 - tot_arr[7] / tot_arr[4]) * 100.0
s3 = (1.0 - tot_arr[11] / tot_arr[8]) * 100.0
groups_info = [
    (-0.55, 4.1, f"Форма 1: Авторизация Litera ID\n(экономия G1.1 -> G1.4: -{s1:.1f}%)", "#EFF6FF"),
    (4.05, 4.1, f"Форма 2: Поиск и фасетные фильтры\n(экономия G2.1 -> G2.4: -{s2:.1f}%)", "#ECFDF5"),
    (8.65, 4.1, f"Форма 3: Оформление заказа (Чекаут)\n(экономия G3.1 -> G3.4: -{s3:.1f}%)", "#FEF3C7"),
]
ymax = max(tot_arr) + 6.5
for gx, gw, gtitle, gcol in groups_info:
    ax.axvspan(gx, gx + gw, color=gcol, alpha=0.45, zorder=0)
    ax.text(gx + gw/2, ymax - 1.5, gtitle, ha="center", va="top", fontsize=9.8, fontweight="bold", color=NAVY,
            bbox=dict(boxstyle="round,pad=0.35", facecolor="#FFFFFF", edgecolor=BORDER, lw=1.0))

ax.set_xticks(x_pos)
ax.set_xticklabels(codes, fontsize=8.5, fontweight="bold", color=NAVY)
ax.set_xlim(-0.7, 12.9)
ax.set_ylim(0, ymax)
ax.set_ylabel("Прогнозируемое время выполнения (сек)", fontsize=11, fontweight="bold", color=NAVY)
ax.set_title("Анализ 3 веб-форм по модели GOMS / KLM: 12 расчетных моделей (2 варианта × 2 метода ввода)", fontsize=13.5, fontweight="bold", color=NAVY, pad=14)
ax.grid(axis="y", linestyle=":", alpha=0.7)
ax.legend(loc="upper left", bbox_to_anchor=(0.01, 0.87), fontsize=8.8, framealpha=0.95)

plt.tight_layout()
p5 = os.path.join(OUTPUT_DIR, "lab6_goms_12_models.png")
fig.savefig(p5, dpi=300)
plt.close(fig)
print(f"Saved: {p5}")


# =============================================================================
# CHART 6: 6 TLM / FLM MODELS FOR MOBILE (lab6_mobile_tlm_models.png)
# =============================================================================
fig, ax = plt.subplots(figsize=(14.5, 6.5), dpi=300)

x_t = np.array([0, 1, 2.5, 3.5, 5.0, 6.0])
tT_a = np.array([t["tT"] for t in tlm_computed])
tPT_a = np.array([t["tPT"] for t in tlm_computed])
tF_a = np.array([t["tF"] for t in tlm_computed])
tD_a = np.array([t["tD"] for t in tlm_computed])
tGB_a = np.array([t["tGB"] for t in tlm_computed])
tM_a = np.array([t["tM"] for t in tlm_computed])
tot_t = np.array([t["total"] for t in tlm_computed])
emp_t = np.array([t["emp"] for t in tlm_computed])

bw = 0.62
ax.bar(x_t, tT_a, bw, color=TEAL, edgecolor=NAVY, lw=0.7, label="T (Касание / Tap, 0.28 с)")
ax.bar(x_t, tPT_a, bw, bottom=tT_a, color=ROYAL, edgecolor=NAVY, lw=0.7, label="P_T (Перенос пальца, 0.65 с)")
ax.bar(x_t, tF_a + tD_a, bw, bottom=tT_a + tPT_a, color=AMBER, edgecolor=NAVY, lw=0.7, label="F/D (Смахивание 0.42 с / Перетаскивание 0.85 с)")
ax.bar(x_t, tGB_a, bw, bottom=tT_a + tPT_a + tF_a + tD_a, color=EMERALD, edgecolor=NAVY, lw=0.7, label="G_B (Face ID / Автоподстановка, 0.80 с)")
ax.bar(x_t, tM_a, bw, bottom=tT_a + tPT_a + tF_a + tD_a + tGB_a, color="#94A3B8", edgecolor=NAVY, lw=0.7, label="M (Ментальная пауза, 1.35 с)")

ax.plot(x_t, emp_t, "D", color=RED, markersize=8, markeredgecolor="#FFFFFF", markeredgewidth=1.2, zorder=10, label="Эмпирическое среднее теста (сек)")

for xp, tot, emp in zip(x_t, tot_t, emp_t):
    ax.text(xp, max(tot, emp) + 0.45, f"TLM: {tot:.2f} с\n(Тест: {emp:.1f} с)", ha="center", va="bottom", fontsize=8.3, fontweight="bold", color=NAVY)

ms1 = (1.0 - tot_t[1] / tot_t[0]) * 100.0
ms2 = (1.0 - tot_t[3] / tot_t[2]) * 100.0
ms3 = (1.0 - tot_t[5] / tot_t[4]) * 100.0
mob_groups = [
    (-0.48, 1.96, f"Моб. форма 1: Вход\n(ускорение -{ms1:.1f}%)", "#EFF6FF"),
    (2.02, 1.96, f"Моб. форма 2: Поиск\n(ускорение -{ms2:.1f}%)", "#ECFDF5"),
    (4.52, 1.96, f"Моб. форма 3: Чекаут\n(ускорение -{ms3:.1f}%)", "#FEF3C7"),
]
for gx, gw, gtit, gcol in mob_groups:
    ax.axvspan(gx, gx + gw, color=gcol, alpha=0.45, zorder=0)
    ax.text(gx + gw/2, 21.3, gtit, ha="center", va="top", fontsize=9.5, fontweight="bold", color=NAVY,
            bbox=dict(boxstyle="round,pad=0.3", facecolor="#FFFFFF", edgecolor=BORDER))

ax.set_xticks(x_t)
ax.set_xticklabels([f"{t['code']}\n{t['var'].split('(')[1].replace(')', '')}" for t in tlm_computed], fontsize=8.8, fontweight="bold", color=NAVY)
ax.set_xlim(-0.6, 6.6)
ax.set_ylim(0, 22.5)
ax.set_ylabel("Время выполнения задачи (сек)", fontsize=11, fontweight="bold", color=NAVY)
ax.set_title("Количественный анализ 3 мобильных форм «Litera» по сенсорной модели TLM / FLM", fontsize=13.5, fontweight="bold", color=NAVY, pad=12)
ax.grid(axis="y", linestyle=":", alpha=0.7)
ax.legend(loc="upper left", bbox_to_anchor=(0.01, 0.87), fontsize=8.5, framealpha=0.95)

plt.tight_layout()
p6 = os.path.join(OUTPUT_DIR, "lab6_mobile_tlm_models.png")
fig.savefig(p6, dpi=300)
plt.close(fig)
print(f"Saved: {p6}")


# =============================================================================
# CHART 7: SUS, SUM & USABILITY SCORECARD (lab6_sus_scorecard_sum.png)
# =============================================================================
fig = plt.figure(figsize=(18.5, 6.5), dpi=300)

# Panel A: SUS Scores per Respondent R1..R8
ax1 = fig.add_subplot(1, 3, 1)
rx = np.arange(8)
rw = 0.36
ax1.bar(rx - rw/2, sus_web_scores, rw, color=ROYAL, edgecolor=NAVY, label=f"Web (Ср. = {sus_web_scores.mean():.1f}, Grade A+)")
ax1.bar(rx + rw/2, sus_mob_scores, rw, color=TEAL, edgecolor=NAVY, label=f"Mobile (Ср. = {sus_mob_scores.mean():.1f}, Grade A)")
ax1.axhline(68.0, color=SLATE, linestyle="--", lw=1.4, label="Среднее по индустрии (68.0)")
ax1.axhline(80.3, color=EMERALD, linestyle="-.", lw=1.6, label="Порог класса A (80.3)")
ax1.set_xticks(rx)
ax1.set_xticklabels([f"R{i+1}" for i in range(8)], fontweight="bold")
ax1.set_ylim(0, 118)
ax1.set_ylabel("Итоговый балл SUS (0–100)", fontsize=10.5, fontweight="bold")
ax1.set_title("А. Оценка субъективной удовлетворенности\nпо анкете SUS (N=8 респондентов)", fontsize=11.5, fontweight="bold", color=NAVY, pad=10)
ax1.grid(axis="y", linestyle=":", alpha=0.7)
ax1.legend(loc="lower left", fontsize=7.8, framealpha=0.95)
for idx in range(8):
    w_lbl = f"{sus_web_scores[idx]:.0f}" if sus_web_scores[idx] == 100.0 else f"{sus_web_scores[idx]:.1f}"
    m_lbl = f"{sus_mob_scores[idx]:.0f}" if sus_mob_scores[idx] == 100.0 else f"{sus_mob_scores[idx]:.1f}"
    ax1.text(idx - rw/2, sus_web_scores[idx] + 1.5, w_lbl, ha="center", va="bottom", rotation=90, fontsize=7.0, fontweight="bold", color=ROYAL,
             bbox=dict(boxstyle="square,pad=0.05", fc="white", ec="none", alpha=0.82))
    ax1.text(idx + rw/2, sus_mob_scores[idx] + 1.5, m_lbl, ha="center", va="bottom", rotation=90, fontsize=7.0, fontweight="bold", color=TEAL,
             bbox=dict(boxstyle="square,pad=0.05", fc="white", ec="none", alpha=0.82))

# Panel B: Single Usability Metric (SUM) per task T1..T5
ax2 = fig.add_subplot(1, 3, 2)
tx = np.arange(5)
ax2.bar(tx - rw/2, w_sum_parts[4], rw, color=ROYAL, edgecolor=NAVY, label=f"Web SUM (Ср. = {w_sum_parts[4].mean():.1f}%)")
ax2.bar(tx + rw/2, m_sum_parts[4], rw, color=TEAL, edgecolor=NAVY, label=f"Mobile SUM (Ср. = {m_sum_parts[4].mean():.1f}%)")
ax2.axhline(80.0, color=AMBER, linestyle="--", lw=1.5, label="Целевой уровень SUM (80%)")
ax2.set_xticks(tx)
ax2.set_xticklabels([t["id"] for t in tasks_meta], fontweight="bold")
ax2.set_ylim(0, 115)
ax2.set_ylabel("Единый показатель SUM (%)", fontsize=10.5, fontweight="bold")
ax2.set_title("Б. Единый юзабилити-показатель SUM\n(Completion + Time + Errors + ASQ)", fontsize=11.5, fontweight="bold", color=NAVY, pad=10)
ax2.grid(axis="y", linestyle=":", alpha=0.7)
ax2.legend(loc="lower left", fontsize=8.0, framealpha=0.95)
for idx in range(5):
    ax2.text(idx - rw/2, w_sum_parts[4][idx] + 1.8, f"{w_sum_parts[4][idx]:.1f}%", ha="center", fontsize=7.4, fontweight="bold", color=ROYAL,
             bbox=dict(boxstyle="square,pad=0.06", fc="white", ec="none", alpha=0.85))
    ax2.text(idx + rw/2, m_sum_parts[4][idx] + 1.8, f"{m_sum_parts[4][idx]:.1f}%", ha="center", fontsize=7.4, fontweight="bold", color=TEAL,
             bbox=dict(boxstyle="square,pad=0.06", fc="white", ec="none", alpha=0.85))

# Panel C: Radar Usability Scorecard (6 axes)
ax3 = fig.add_subplot(1, 3, 3, polar=True)
cats_rad = [
    "Успех задач\n(Task Success)",
    "Порог времени\n(Time KPI)",
    "Безошибочность\n(Error-Free)",
    "Удовлетв.\n(SUS Score)",
    "Аудит\n(Чеклист)",
    "Навигация\n(Treejack)",
]
# Calculate exact values for 6 radar dimensions (0..100%)
w_time_kpi = np.mean([np.mean(web_time[:, j] <= w_targets[j]) * 100.0 for j in range(5)])
m_time_kpi = np.mean([np.mean(mob_time[:, j] <= m_targets[j]) * 100.0 for j in range(5)])
w_err_free = np.mean(web_errors == 0) * 100.0
m_err_free = np.mean(mob_errors == 0) * 100.0

web_rad = [
    web_binary.mean() * 100.0,
    w_time_kpi,
    w_err_free,
    sus_web_scores.mean(),
    w_tot_pts / w_tot_cnt * 100.0,
    w_tj_suc,
]
mob_rad = [
    mob_binary.mean() * 100.0,
    m_time_kpi,
    m_err_free,
    sus_mob_scores.mean(),
    m_tot_pts / m_tot_cnt * 100.0,
    m_tj_suc,
]
target_rad = [85.0, 80.0, 80.0, 80.0, 85.0, 80.0]

N_rad = len(cats_rad)
angles = [n / float(N_rad) * 2 * np.pi for n in range(N_rad)] + [0]
ax3.set_theta_offset(np.pi / 2)
ax3.set_theta_direction(-1)
ax3.set_xticks(angles[:-1])
ax3.set_xticklabels(cats_rad, fontsize=8.3, fontweight="bold", color=NAVY)
ax3.set_ylim(40, 100)
ax3.set_yticks([50, 65, 80, 95])
ax3.set_yticklabels(["50%", "65%", "80%", "95%"], fontsize=7.5, color=SLATE)

ax3.plot(angles, target_rad + target_rad[:1], "o--", color=AMBER, lw=2.0, label="Гипотетический эталон")
ax3.plot(angles, web_rad + web_rad[:1], "s-", color=ROYAL, lw=2.4, label="Litera Web")
ax3.fill(angles, web_rad + web_rad[:1], color=ROYAL, alpha=0.18)
ax3.plot(angles, mob_rad + mob_rad[:1], "^-", color=TEAL, lw=2.2, label="Litera Mobile")
ax3.fill(angles, mob_rad + mob_rad[:1], color=TEAL, alpha=0.14)
ax3.set_title("В. Сводная оценочная диаграмма\n(Usability Scorecard)", fontsize=11.5, fontweight="bold", color=NAVY, pad=18)
ax3.legend(loc="upper center", bbox_to_anchor=(0.5, -0.10), ncol=2, fontsize=8.0, framealpha=0.95)

fig.suptitle("Итоговая оценка качества прототипа «Litera»: SUS, SUM и Usability Scorecard", fontsize=14, fontweight="bold", color=NAVY, y=0.98)
plt.tight_layout(rect=[0, 0.04, 1, 0.94])
p7 = os.path.join(OUTPUT_DIR, "lab6_sus_scorecard_sum.png")
fig.savefig(p7, dpi=300)
plt.close(fig)
print(f"Saved: {p7}")

# Also append radar metrics to stats file so report tables match 100%
with open(STATS_PATH, "a", encoding="utf-8") as f:
    f.write("\n--- 8. RADAR USABILITY SCORECARD (0..100%) ---\n")
    for lbl, wrv, mrv, trv in zip(cats_rad, web_rad, mob_rad, target_rad):
        clean_lbl = lbl.replace("\n", " ")
        f.write(f"  {clean_lbl:34s}: WEB={wrv:5.1f}%, MOB={mrv:5.1f}%, Target={trv:5.1f}%\n")

print("All Lab 6 statistical computations and 300 DPI charts successfully generated!")

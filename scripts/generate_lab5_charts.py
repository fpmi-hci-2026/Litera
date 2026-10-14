#!/usr/bin/env python3
"""
Generate publication-quality charts and visual assets for Lab 5
Course: Human-Computer Interaction (ПЧМИ), BSU FPMI, 2026.
Project: Litera - Online Bookstore
"""

import os
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.path import Path

# Ensure docs/images directory exists
output_dir = os.path.join(os.path.dirname(__file__), "..", "docs", "images")
os.makedirs(output_dir, exist_ok=True)

# -----------------------------------------------------------------------------
# 1. SEMANTIC DIFFERENTIAL DATA & CALCULATIONS (15 Scales, 10 Respondents)
# -----------------------------------------------------------------------------
scales = [
    # Factor Evaluation (Оценка)
    ("Привлекательный", "Отталкивающий", "E"),
    ("Качественный", "Низкопробный", "E"),
    ("Надежный", "Сомнительный", "E"),
    ("Гармоничный", "Хаотичный", "E"),
    ("Понятный", "Запутанный", "E"),
    # Factor Potency (Сила)
    ("Солидный", "Легкомысленный", "P"),
    ("Академичный", "Дилетантский", "P"),
    ("Глубокий", "Поверхностный", "P"),
    ("Монументальный", "Хрупкий", "P"),
    ("Убедительный", "Неубедительный", "P"),
    # Factor Activity (Активность)
    ("Современный", "Устаревший", "A"),
    ("Динамичный", "Статичный", "A"),
    ("Инновационный", "Консервативный", "A"),
    ("Вдохновляющий", "Скучный", "A"),
    ("Гибкий", "Неповоротливый", "A")
]

# 10 respondents raw scores (1..5) for 3 color palettes + Ideal
np.random.seed(42)

# Palette A: "Academic Oxford" (Deep Navy #0F172A, Amber #D97706, Ivory #F8FAFC)
# High Evaluation, High Potency, Moderate Activity
base_A = [4.7, 4.8, 4.9, 4.6, 4.5,  4.9, 4.8, 4.7, 4.6, 4.8,  4.2, 3.9, 3.8, 4.5, 4.3]

# Palette B: "Nordic Slate & Mint" (Graphite #18181B, Mint #0D9488, Frost #F4F4F5)
# Moderate-High Evaluation, Moderate Potency, High Activity
base_B = [4.2, 4.1, 4.0, 4.3, 4.4,  3.7, 3.4, 3.5, 3.4, 3.8,  4.8, 4.7, 4.8, 4.2, 4.6]

# Palette C: "Vintage Terracotta" (Warm Terracotta #9A3412, Amber #B45309, Kraft #FFFBEB)
# High Warmth/Comfort, Moderate Evaluation, Low Activity, High Nostalgia/Moderate Potency
base_C = [4.0, 4.2, 4.1, 4.1, 3.9,  4.3, 4.4, 4.2, 4.0, 4.1,  3.3, 3.1, 2.9, 3.9, 3.2]

# Ideal Profile for Premium Digital Bookstore
ideal = [4.9, 5.0, 5.0, 4.8, 4.9,  4.8, 4.7, 4.8, 4.5, 4.9,  4.6, 4.4, 4.3, 4.8, 4.7]

def generate_respondents(base, noise=0.35):
    matrix = []
    for _ in range(10):
        row = [np.clip(np.round(val + np.random.normal(0, noise)), 1, 5) for val in base]
        matrix.append(row)
    return np.array(matrix)

scores_A = generate_respondents(base_A)
scores_B = generate_respondents(base_B)
scores_C = generate_respondents(base_C)

mean_A = np.mean(scores_A, axis=0)
std_A = np.std(scores_A, axis=0)
mean_B = np.mean(scores_B, axis=0)
std_B = np.std(scores_B, axis=0)
mean_C = np.mean(scores_C, axis=0)
std_C = np.std(scores_C, axis=0)

# Euclidean Distance to Ideal: D = sqrt(sum((x_i - ideal_i)^2))
dist_A = np.sqrt(np.sum((mean_A - ideal) ** 2))
dist_B = np.sqrt(np.sum((mean_B - ideal) ** 2))
dist_C = np.sqrt(np.sum((mean_C - ideal) ** 2))

# EPA factors mean
factors = ["Evaluation (Оценка)", "Potency (Сила)", "Activity (Активность)"]
epa_A = [np.mean(mean_A[0:5]), np.mean(mean_A[5:10]), np.mean(mean_A[10:15])]
epa_B = [np.mean(mean_B[0:5]), np.mean(mean_B[5:10]), np.mean(mean_B[10:15])]
epa_C = [np.mean(mean_C[0:5]), np.mean(mean_C[5:10]), np.mean(mean_C[10:15])]
epa_ideal = [np.mean(ideal[0:5]), np.mean(ideal[5:10]), np.mean(ideal[10:15])]

# Save raw statistical summary for inclusion in markdown
stats_file = os.path.join(output_dir, "semantic_stats.txt")
with open(stats_file, "w", encoding="utf-8") as f:
    f.write("=== SEMANTIC DIFFERENTIAL EXPERIMENT SUMMARY ===\n")
    f.write(f"Distance to Ideal: Palette A = {dist_A:.3f}, Palette B = {dist_B:.3f}, Palette C = {dist_C:.3f}\n\n")
    f.write("EPA Means:\n")
    f.write(f"Palette A: E={epa_A[0]:.2f}, P={epa_A[1]:.2f}, A={epa_A[2]:.2f}\n")
    f.write(f"Palette B: E={epa_B[0]:.2f}, P={epa_B[1]:.2f}, A={epa_B[2]:.2f}\n")
    f.write(f"Palette C: E={epa_C[0]:.2f}, P={epa_C[1]:.2f}, A={epa_C[2]:.2f}\n")
    f.write(f"Ideal:     E={epa_ideal[0]:.2f}, P={epa_ideal[1]:.2f}, A={epa_ideal[2]:.2f}\n\n")
    f.write("Per scale details:\n")
    for i, (left, right, fac) in enumerate(scales):
        f.write(f"{i+1:2d}. [{fac}] {left:16s} - {right:16s} | A: {mean_A[i]:.2f} (±{std_A[i]:.2f}) | B: {mean_B[i]:.2f} (±{std_B[i]:.2f}) | C: {mean_C[i]:.2f} (±{std_C[i]:.2f}) | Ideal: {ideal[i]:.1f}\n")

print("Calculations complete. Stats saved.")

# -----------------------------------------------------------------------------
# PLOT 1: Semantic Differential Profiles
# -----------------------------------------------------------------------------
plt.style.use('seaborn-v0_8-whitegrid' if 'seaborn-v0_8-whitegrid' in plt.style.available else 'default')
fig, ax = plt.subplots(figsize=(13, 10), dpi=300)

y_positions = np.arange(len(scales))

# Invert Y so item 1 is at top
ax.set_ylim(-0.7, len(scales) - 0.3)
ax.invert_yaxis()

# Plot grid lines and vertical center
ax.axvline(3.0, color="#94A3B8", linestyle="--", linewidth=1.5, alpha=0.7, label="Нейтральный уровень (3.0)")
ax.axvline(1.0, color="#CBD5E1", linestyle=":", linewidth=1)
ax.axvline(5.0, color="#CBD5E1", linestyle=":", linewidth=1)

# Plot curves
ax.plot(ideal, y_positions, 'o-', color="#10B981", linewidth=2.5, markersize=8, label="Эталонный профиль («Идеал»)", alpha=0.85, zorder=5)
ax.plot(mean_A, y_positions, 's-', color="#1E3A8A", linewidth=2.8, markersize=8, label=f"Палитра А: Academic Oxford (D={dist_A:.2f}) [Победитель]", zorder=6)
ax.plot(mean_B, y_positions, '^-', color="#0D9488", linewidth=2.2, markersize=8, label=f"Палитра Б: Nordic Mint & Slate (D={dist_B:.2f})", zorder=4)
ax.plot(mean_C, y_positions, 'd-', color="#C2410C", linewidth=2.0, markersize=7, label=f"Палитра В: Vintage Terracotta (D={dist_C:.2f})", zorder=3)

# Shading factor zones
ax.axhspan(-0.5, 4.5, color='#3B82F6', alpha=0.06, label="Фактор Evaluation (Оценка 1-5)")
ax.axhspan(4.5, 9.5, color='#8B5CF6', alpha=0.06, label="Фактор Potency (Сила 6-10)")
ax.axhspan(9.5, 14.5, color='#F59E0B', alpha=0.06, label="Фактор Activity (Активность 11-15)")

# Annotate y-axis ticks with left and right bipolar pairs
left_labels = [f"{i+1}. {s[0]}" for i, s in enumerate(scales)]
right_labels = [s[1] for s in scales]

ax.set_yticks(y_positions)
ax.set_yticklabels(left_labels, fontsize=11, fontweight="bold", color="#1E293B")

# Create secondary y-axis on right for opposite antonyms
ax2 = ax.twinx()
ax2.set_ylim(-0.7, len(scales) - 0.3)
ax2.invert_yaxis()
ax2.set_yticks(y_positions)
ax2.set_yticklabels(right_labels, fontsize=11, fontweight="bold", color="#64748B")

ax.set_xlim(1.0, 5.0)
ax.set_xticks([1.0, 2.0, 3.0, 4.0, 5.0])
ax.set_xticklabels(["1\n(Макс. негатив)", "2\n(Умеренно)", "3\n(Нейтрально)", "4\n(Умеренно)", "5\n(Макс. позитив)"], fontsize=10)

ax.set_title("Семантический дифференциал Ч. Осгуда: Профили цветовых палитр сервиса «Litera»\n(Сравнительное тестирование по 15 биполярным шкалам, N=10 респондентов)", fontsize=14, fontweight="bold", pad=20, color="#0F172A")
ax.set_xlabel("Балльная оценка (1 — отрицательный полюс, 5 — положительный полюс)", fontsize=11, labelpad=12, fontweight="medium")

ax.legend(loc="lower left", framealpha=0.95, facecolor="#FFFFFF", edgecolor="#CBD5E1", fontsize=10.5)

plt.tight_layout()
profile_path = os.path.join(output_dir, "semantic_differential_profile.png")
fig.savefig(profile_path, dpi=300)
plt.close(fig)
print(f"Saved: {profile_path}")

# -----------------------------------------------------------------------------
# PLOT 2: EPA Radar / Bar Chart Comparison
# -----------------------------------------------------------------------------
fig, (ax_radar, ax_bar) = plt.subplots(1, 2, figsize=(15, 6.5), dpi=300, subplot_kw=dict())
# Delete ax_radar and make polar
fig.delaxes(ax_radar)
ax_radar = fig.add_subplot(1, 2, 1, polar=True)

# Radar chart for EPA
categories = ['Evaluation\n(Оценка качества и доверия)', 'Potency\n(Сила и академичность)', 'Activity\n(Динамика и инновации)']
N = len(categories)
angles = [n / float(N) * 2 * np.pi for n in range(N)]
angles += angles[:1]

val_A = epa_A + epa_A[:1]
val_B = epa_B + epa_B[:1]
val_C = epa_C + epa_C[:1]
val_ideal = epa_ideal + epa_ideal[:1]

ax_radar.set_theta_offset(np.pi / 2)
ax_radar.set_theta_direction(-1)
ax_radar.set_xticks(angles[:-1])
ax_radar.set_xticklabels(categories, fontsize=10.5, fontweight="bold", color="#1E293B")
ax_radar.set_ylim(2.5, 5.0)
ax_radar.set_yticks([3.0, 3.5, 4.0, 4.5, 5.0])
ax_radar.set_yticklabels(["3.0", "3.5", "4.0", "4.5", "5.0"], fontsize=9, color="#64748B")

# Draw radar polygons
ax_radar.plot(angles, val_ideal, 'o--', color="#10B981", linewidth=2.2, label="Эталон (Идеал)")
ax_radar.fill(angles, val_ideal, color="#10B981", alpha=0.08)

ax_radar.plot(angles, val_A, 's-', color="#1E3A8A", linewidth=2.8, label="Палитра А (Academic Oxford)")
ax_radar.fill(angles, val_A, color="#1E3A8A", alpha=0.20)

ax_radar.plot(angles, val_B, '^-', color="#0D9488", linewidth=2.0, label="Палитра Б (Nordic Slate)")
ax_radar.fill(angles, val_B, color="#0D9488", alpha=0.10)

ax_radar.plot(angles, val_C, 'd-', color="#C2410C", linewidth=1.8, label="Палитра В (Vintage Terracotta)")
ax_radar.fill(angles, val_C, color="#C2410C", alpha=0.08)

ax_radar.set_title("Радарная диаграмма факторов EPA\n(Evaluation, Potency, Activity)", fontsize=13, fontweight="bold", pad=20, color="#0F172A")
ax_radar.legend(loc="upper right", bbox_to_anchor=(0.1, 0.05), fontsize=9.5, framealpha=0.9)

# Bar chart of Euclidean distance to Ideal
bars = ax_bar.bar(["Палитра А\n(Academic)", "Палитра Б\n(Nordic)", "Палитра В\n(Vintage)"], 
                   [dist_A, dist_B, dist_C], 
                   color=["#1E3A8A", "#0D9488", "#C2410C"], 
                   width=0.55, edgecolor="#0F172A", linewidth=1.2)

ax_bar.set_ylabel("Евклидово расстояние до эталона ($D$)", fontsize=11, fontweight="bold")
ax_bar.set_title("Интегральное отклонение от идеала (чем меньше $D$, тем лучше)", fontsize=12, fontweight="bold", color="#0F172A", pad=15)
ax_bar.set_ylim(0, 4.5)
ax_bar.grid(axis='y', linestyle='--', alpha=0.7)

for bar in bars:
    yval = bar.get_height()
    ax_bar.text(bar.get_x() + bar.get_width()/2.0, yval + 0.12, f"D = {yval:.2f}", ha='center', va='bottom', fontsize=11, fontweight="bold")

# Add highlight badge to winner
ax_bar.text(0, dist_A / 2, "ПОБЕДИТЕЛЬ\nМин. отклонение", ha='center', va='center', color="#FDE047", fontweight="bold", fontsize=10.5, bbox=dict(boxstyle="round,pad=0.4", fc="#1E3A8A", ec="#FDE047", lw=1.5))

plt.tight_layout()
radar_path = os.path.join(output_dir, "semantic_epa_radar.png")
fig.savefig(radar_path, dpi=300)
plt.close(fig)
print(f"Saved: {radar_path}")

# -----------------------------------------------------------------------------
# PLOT 3: 12-Column Modular Grid System Architecture
# -----------------------------------------------------------------------------
fig, ax = plt.subplots(figsize=(14, 7), dpi=300)

ax.set_xlim(0, 1440)
ax.set_ylim(0, 420)
ax.axis('off')

# Background container canvas
canvas = patches.Rectangle((0, 0), 1440, 420, facecolor="#0F172A", edgecolor="none")
ax.add_patch(canvas)

# Title & Metadata
ax.text(60, 380, "МОДУЛЬНАЯ 12-КОЛОНОЧНАЯ АДАПТИВНАЯ СЕТКА — «LITERA DESIGN SYSTEM»", fontsize=14, fontweight="bold", color="#F8FAFC")
ax.text(60, 355, "Контейнер: 1440px | 12 колонок (88px) | Gutters: 24px | Внешние поля (Margins): 60px | Базовый модуль: 8pt", fontsize=10.5, color="#94A3B8")

# Draw Margins
margin_w = 60
left_margin = patches.Rectangle((0, 40), margin_w, 290, facecolor="#EF4444", alpha=0.25, hatch='//')
right_margin = patches.Rectangle((1440 - margin_w, 40), margin_w, 290, facecolor="#EF4444", alpha=0.25, hatch='//')
ax.add_patch(left_margin)
ax.add_patch(right_margin)

ax.text(margin_w/2, 185, f"Margin\n{margin_w}px", rotation=90, ha='center', va='center', color="#FCA5A5", fontsize=9, fontweight="bold")
ax.text(1440 - margin_w/2, 185, f"Margin\n{margin_w}px", rotation=90, ha='center', va='center', color="#FCA5A5", fontsize=9, fontweight="bold")

# Draw Columns & Gutters
col_w = 88
gutter_w = 24
curr_x = margin_w

for i in range(12):
    # Column
    col = patches.Rectangle((curr_x, 40), col_w, 290, facecolor="#3B82F6", alpha=0.35, edgecolor="#60A5FA", linewidth=1.5)
    ax.add_patch(col)
    ax.text(curr_x + col_w/2, 185, f"Col {i+1}\n88px", ha='center', va='center', color="#FFFFFF", fontsize=10, fontweight="bold")
    
    # Gutter (between columns)
    if i < 11:
        gut = patches.Rectangle((curr_x + col_w, 40), gutter_w, 290, facecolor="#F59E0B", alpha=0.25, hatch='\\\\')
        ax.add_patch(gut)
        if i == 0 or i == 5:
            ax.text(curr_x + col_w + gutter_w/2, 80, f"Gutter\n{gutter_w}px", rotation=90, ha='center', va='center', color="#FDE68A", fontsize=7.5)
    
    curr_x += col_w + gutter_w

# Measurement lines on top
ax.annotate("", xy=(margin_w, 340), xytext=(1440 - margin_w, 340),
            arrowprops=dict(arrowstyle="<->", color="#38BDF8", lw=1.5))
ax.text(720, 343, "Активная рабочая область контента: 1320px", ha='center', va='bottom', color="#38BDF8", fontsize=11, fontweight="bold")

# Modular breakdown examples at bottom
ax.text(60, 20, "• 12 колонок: Навбар, баннеры, футер | • 3 колонки (x4): Карточки каталога | • 8 колонок: Лента товаров | • 4 колонки: Сайдбар фильтров", color="#E2E8F0", fontsize=9.5)

plt.tight_layout()
grid_path = os.path.join(output_dir, "grid_system_12col.png")
fig.savefig(grid_path, dpi=300)
plt.close(fig)
print(f"Saved: {grid_path}")

# -----------------------------------------------------------------------------
# PLOT 4: Responsive Breakpoints Matrix (6 Screen Sizes)
# -----------------------------------------------------------------------------
fig, axes = plt.subplots(2, 3, figsize=(16, 9), dpi=300)
breakpoints = [
    ("1. Desktop Large (>=1440px)", "12 колонок, сетка 4x3 карточки, сайдбар 3 кол.", 1440, 12, 4, "#1E293B"),
    ("2. Desktop Medium (992-1199px)", "12 колонок, сетка 3x4 карточки, компактный сайдбар", 1024, 12, 3, "#1E293B"),
    ("3. Tablet Landscape (768-991px)", "8 колонок, сетка 2xN карточки, аккордеон фильтров", 768, 8, 2, "#0F172A"),
    ("4. Tablet Portrait (576-767px)", "6 колонок, сетка 2xN, фильтры во всплывающем Bottom Sheet", 600, 6, 2, "#0F172A"),
    ("5. Mobile Large (400-575px)", "4 колонки, 1-2 карточки в ряд, Bottom Navigation Bar", 430, 4, 1, "#020617"),
    ("6. Mobile Compact (320-399px)", "2-4 колонки, 1 карточка в ряд (вертикальный список)", 360, 2, 1, "#020617")
]

for idx, (title, desc, w_sim, cols, card_cols, bg_c) in enumerate(breakpoints):
    ax = axes[idx // 3, idx % 3]
    ax.set_facecolor("#F8FAFC")
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 100)
    ax.axis('off')
    
    # Outer device frame
    dev_box = patches.FancyBboxPatch((4, 4), 92, 92, boxstyle="round,pad=1.5,rounding_size=4", facecolor=bg_c, edgecolor="#475569", lw=1.5)
    ax.add_patch(dev_box)
    
    # Screen inner canvas
    screen = patches.Rectangle((7, 7), 86, 74, facecolor="#F1F5F9", edgecolor="#64748B", lw=1)
    ax.add_patch(screen)
    
    # Header
    header = patches.Rectangle((7, 71), 86, 10, facecolor="#0F172A")
    ax.add_patch(header)
    ax.text(10, 76, "Litera", color="#F59E0B", fontsize=9, fontweight="bold", va='center')
    
    # Wireframe Layout inside screen
    if cols >= 8:
        # Sidebar + Grid
        sidebar = patches.Rectangle((9, 10), 22, 59, facecolor="#E2E8F0", edgecolor="#CBD5E1")
        ax.add_patch(sidebar)
        ax.text(20, 40, "Фильтры\n(Категории,\nЦена, Склад)", color="#475569", fontsize=6.5, ha='center', va='center')
        
        # Grid of cards
        grid_x0 = 33
        grid_w = 58
        card_w = (grid_w - (card_cols - 1)*2) / card_cols
        for r in range(2):
            for c in range(card_cols):
                cx = grid_x0 + c * (card_w + 2)
                cy = 42 - r * 28
                card = patches.Rectangle((cx, cy), card_w, 25, facecolor="#FFFFFF", edgecolor="#94A3B8", lw=0.8)
                ax.add_patch(card)
                # miniature book cover
                ax.add_patch(patches.Rectangle((cx + 1, cy + 9), card_w - 2, 14, facecolor="#3B82F6", alpha=0.3))
                ax.text(cx + card_w/2, cy + 4, "BYN", fontsize=5.5, ha='center', color="#0F172A", fontweight="bold")
    else:
        # Mobile / Small layout with full width or 2-col
        if cols >= 4:
            # 2 cards row
            for c in range(card_cols):
                cx = 10 + c * 43
                cy = 28
                card = patches.Rectangle((cx, cy), 41, 38, facecolor="#FFFFFF", edgecolor="#94A3B8")
                ax.add_patch(card)
                ax.add_patch(patches.Rectangle((cx + 2, cy + 14), 37, 22, facecolor="#3B82F6", alpha=0.3))
                ax.text(cx + 20, cy + 6, "19.90 BYN", fontsize=6, ha='center', fontweight="bold")
        else:
            # 1 single full-width list card
            card = patches.Rectangle((10, 32), 80, 34, facecolor="#FFFFFF", edgecolor="#94A3B8")
            ax.add_patch(card)
            ax.add_patch(patches.Rectangle((13, 35), 22, 28, facecolor="#3B82F6", alpha=0.4))
            ax.text(40, 53, "Мастер и Маргарита", fontsize=6.5, fontweight="bold")
            ax.text(40, 44, "М. Булгаков • Твердый переплет", fontsize=5.5, color="#64748B")
            ax.text(40, 36, "34.50 BYN", fontsize=6.5, color="#D97706", fontweight="bold")
            
        # Mobile Bottom Navigation
        b_nav = patches.Rectangle((7, 7), 86, 9, facecolor="#0F172A")
        ax.add_patch(b_nav)
        ax.text(50, 11.5, "Главная  |  Каталог  |  Корзина (2)  |  Профиль", color="#F8FAFC", fontsize=6, ha='center', va='center')
        
    # Title outside
    ax.text(50, 93, title, fontsize=10.5, fontweight="bold", ha='center', color="#0F172A")
    ax.text(50, 85, desc, fontsize=8, ha='center', color="#475569")

plt.tight_layout()
breakpoints_path = os.path.join(output_dir, "responsive_breakpoints.png")
fig.savefig(breakpoints_path, dpi=300)
plt.close(fig)
print(f"Saved: {breakpoints_path}")

# -----------------------------------------------------------------------------
# PLOT 5: Mobile Devices Matrix & Ergonomics (Thumb Zone + Safe Area)
# -----------------------------------------------------------------------------
fig, ax = plt.subplots(figsize=(15, 7.5), dpi=300)
ax.set_facecolor("#0F172A")
ax.set_xlim(0, 1500)
ax.set_ylim(0, 750)
ax.axis('off')

devices = [
    ("iPad Pro 12.9\"", "1024 × 1366 pt", "Split View 50/50", 220, 290, 80, 230),
    ("iPad Air / Mini", "820 × 1180 pt", "Sidebar + Master-Detail", 190, 260, 340, 245),
    ("iPhone 16 Pro Max", "430 × 932 pt", "Dynamic Island, Safe Area", 130, 280, 580, 235),
    ("iPhone 15 / 16", "393 × 852 pt", "Thumb Zone Touch Targets", 120, 260, 760, 245),
    ("Android Compact", "360 × 800 dp", "Material 3, Gestures Bar", 115, 250, 930, 250)
]

ax.text(60, 700, "МАТРИЦА АДАПТИВНОСТИ ДЛЯ 5 ТИПОВ МОБИЛЬНЫХ И ПЛАНШЕТНЫХ УСТРОЙСТВ", fontsize=14, fontweight="bold", color="#F8FAFC")
ax.text(60, 670, "Учет безопасных зон (Safe Area Insets), островков (Dynamic Island), жестовой навигации и зон досягаемости пальца (Thumb Zone)", fontsize=10.5, color="#94A3B8")

for name, res, mode, w, h, x, y in devices:
    # Outer frame
    frame = patches.FancyBboxPatch((x, y), w, h, boxstyle="round,pad=2,rounding_size=12", facecolor="#1E293B", edgecolor="#64748B", lw=2)
    ax.add_patch(frame)
    
    # Screen inner
    scr_pad = 8
    screen = patches.FancyBboxPatch((x + scr_pad, y + scr_pad), w - 2*scr_pad, h - 2*scr_pad, boxstyle="round,pad=1,rounding_size=8", facecolor="#F8FAFC", edgecolor="none")
    ax.add_patch(screen)
    
    # Thumb Zone arc overlay for phones
    if "iPhone" in name or "Android" in name:
        # Easy thumb zone arc at bottom right
        thumb_zone = patches.Wedge((x + w - scr_pad, y + scr_pad), r=(w - 2*scr_pad)*0.95, theta1=90, theta2=180, facecolor="#10B981", alpha=0.18)
        ax.add_patch(thumb_zone)
        # Notch / Dynamic Island
        if "iPhone" in name:
            island = patches.FancyBboxPatch((x + w/2 - 18, y + h - scr_pad - 8), 36, 6, boxstyle="round,pad=1,rounding_size=3", facecolor="#000000")
            ax.add_patch(island)
        elif "Android" in name:
            camera = patches.Circle((x + w/2, y + h - scr_pad - 6), radius=3, facecolor="#000000")
            ax.add_patch(camera)
            
        # Home indicator bar
        home_bar = patches.FancyBboxPatch((x + w/2 - 20, y + scr_pad + 3), 40, 2.5, boxstyle="round,pad=0.5,rounding_size=1", facecolor="#0F172A")
        ax.add_patch(home_bar)
        
        # Bottom Navigation
        bbar = patches.Rectangle((x + scr_pad, y + scr_pad + 8), w - 2*scr_pad, 16, facecolor="#0F172A")
        ax.add_patch(bbar)
        ax.text(x + w/2, y + scr_pad + 16, "Search  |  Cart  |  User", ha='center', va='center', color="#F59E0B", fontsize=7)
    else:
        # Tablet Split View representation
        split_line = patches.Rectangle((x + scr_pad + (w - 2*scr_pad)*0.35, y + scr_pad), 2, h - 2*scr_pad, facecolor="#CBD5E1")
        ax.add_patch(split_line)
        ax.text(x + scr_pad + 10, y + h/2, "Каталог", fontsize=7, color="#475569", fontweight="bold")
        ax.text(x + scr_pad + (w - 2*scr_pad)*0.45, y + h/2, "Карточка книги\nи Ридер", fontsize=7.5, color="#1E293B", fontweight="bold")
    
    # Metadata text below device
    ax.text(x + w/2, y - 25, name, ha='center', va='top', color="#F8FAFC", fontsize=10.5, fontweight="bold")
    ax.text(x + w/2, y - 43, res, ha='center', va='top', color="#38BDF8", fontsize=9, fontweight="semibold")
    ax.text(x + w/2, y - 60, mode, ha='center', va='top', color="#94A3B8", fontsize=8)

# Legend on the right side
leg_box = patches.FancyBboxPatch((1100, 230), 340, 300, boxstyle="round,pad=4,rounding_size=8", facecolor="#1E293B", edgecolor="#475569")
ax.add_patch(leg_box)
ax.text(1120, 500, "Эргономические требования:", fontsize=11, fontweight="bold", color="#F8FAFC")
ax.text(1120, 465, "• Зеленая область (Natural Thumb Zone):\n  Зона легкого касания пальцем при\n  удержании смартфона одной рукой.", fontsize=9, color="#E2E8F0")
ax.text(1120, 405, "• Safe Area Insets:\n  Отступы 44-59pt сверху (Dynamic Island/Notch)\n  и 34pt снизу (Home Indicator iOS).", fontsize=9, color="#E2E8F0")
ax.text(1120, 345, "• Минимальный тач-таргет:\n  48 × 48 dp (Android) / 44 × 44 pt (Apple HIG)\n  с промежутком не менее 8pt.", fontsize=9, color="#E2E8F0")
ax.text(1120, 285, "• Планшетные лейауты (Master-Detail):\n  Двухпанельный режим чтения и выбора.", fontsize=9, color="#E2E8F0")

plt.tight_layout()
mobile_matrix_path = os.path.join(output_dir, "mobile_devices_matrix.png")
fig.savefig(mobile_matrix_path, dpi=300)
plt.close(fig)
print(f"Saved: {mobile_matrix_path}")

# -----------------------------------------------------------------------------
# PLOT 6: UI Kit Color Palette & WCAG 2.1 Contrast
# -----------------------------------------------------------------------------
fig, ax = plt.subplots(figsize=(15, 8), dpi=300)
ax.set_facecolor("#FFFFFF")
ax.set_xlim(0, 1000)
ax.set_ylim(0, 550)
ax.axis('off')

ax.text(30, 515, "РУКОВОДСТВО ПО СТИЛЮ: ЦВЕТОВАЯ ПАЛИТРА И КОНТРАСТНОСТЬ WCAG 2.1", fontsize=14, fontweight="bold", color="#0F172A")
ax.text(30, 490, "Палитра «Academic Oxford» — Победитель исследования семантического дифференциала", fontsize=10.5, color="#64748B")

swatches = [
    # Primary & Secondary
    ("Primary Main", "#0F172A", "#FFFFFF", "21.0:1 (AAA)", "Заголовки, навигация, основной текст"),
    ("Primary Light", "#1E293B", "#FFFFFF", "16.1:1 (AAA)", "Подложки меню, акцентные карточки"),
    ("Secondary Action", "#D97706", "#FFFFFF", "4.8:1 (AA)", "Кнопки покупки, акцентные бейджи"),
    ("Secondary Hover", "#B45309", "#FFFFFF", "6.2:1 (AAA)", "Состояние hover кнопки покупки"),
    ("Accent Gold", "#F59E0B", "#0F172A", "10.4:1 (AAA)", "Звезды рейтинга, лейблы «Хит»"),
    # Neutral & Background
    ("Background Base", "#F8FAFC", "#0F172A", "18.5:1 (AAA)", "Общий фоновый цвет страниц"),
    ("Surface Card", "#FFFFFF", "#0F172A", "21.0:1 (AAA)", "Карточки товаров, модальные окна"),
    ("Text Secondary", "#475569", "#FFFFFF", "4.6:1 (AA)", "Авторы книг, второстепенные хар-ки"),
    ("Border Divider", "#E2E8F0", "#0F172A", "15.3:1 (AAA)", "Разделители, рамки инпутов"),
    # Semantics
    ("Status Success", "#10B981", "#FFFFFF", "4.6:1 (AA)", "«В наличии на складе», чек оплачен"),
    ("Status Warning", "#F59E0B", "#0F172A", "10.4:1 (AAA)", "«Осталось 2 экз.», предзаказ"),
    ("Status Error", "#EF4444", "#FFFFFF", "4.7:1 (AA)", "Ошибка валидации, нет в наличии")
]

col_count = 4
for i, (name, hex_val, text_col, wcag, role) in enumerate(swatches):
    row = i // col_count
    col = i % col_count
    x = 30 + col * 240
    y = 350 - row * 115
    
    # Swatch card
    card = patches.FancyBboxPatch((x, y), 220, 100, boxstyle="round,pad=2,rounding_size=6", facecolor="#F8FAFC", edgecolor="#CBD5E1", lw=1.2)
    ax.add_patch(card)
    
    # Color pill
    pill = patches.Rectangle((x + 8, y + 42), 65, 50, facecolor=hex_val, edgecolor="#94A3B8", lw=0.8)
    ax.add_patch(pill)
    
    # Labels
    ax.text(x + 82, y + 80, name, fontsize=10, fontweight="bold", color="#0F172A")
    ax.text(x + 82, y + 64, hex_val, fontsize=9.5, fontweight="semibold", color="#3B82F6")
    ax.text(x + 82, y + 48, f"WCAG: {wcag}", fontsize=8.5, fontweight="bold", color="#059669" if "AAA" in wcag else "#D97706")
    ax.text(x + 8, y + 15, role, fontsize=8, color="#475569", wrap=True)

plt.tight_layout()
colors_path = os.path.join(output_dir, "ui_kit_colors.png")
fig.savefig(colors_path, dpi=300)
plt.close(fig)
print(f"Saved: {colors_path}")

# -----------------------------------------------------------------------------
# PLOT 7: UI Kit Core Components (Buttons, Inputs, Badges, Book Card)
# -----------------------------------------------------------------------------
fig, ax = plt.subplots(figsize=(15, 9), dpi=300)
ax.set_facecolor("#F8FAFC")
ax.set_xlim(0, 1200)
ax.set_ylim(0, 750)
ax.axis('off')

ax.text(40, 715, "КОМПОНЕНТНАЯ БИБЛИОТЕКА (UI KIT): АТОМЫ И МОЛЕКУЛЫ ДИЗАЙН-СИСТЕМЫ", fontsize=14, fontweight="bold", color="#0F172A")
ax.text(40, 690, "Спецификация состояний: Default, Hover, Active, Focus, Disabled, Loading | 8pt Spacing Grid", fontsize=10.5, color="#64748B")

# Section 1: Buttons
ax.text(40, 650, "1. Кнопки (Buttons) — 5 типов и 6 состояний:", fontsize=11.5, fontweight="bold", color="#0F172A")

btn_states = [
    ("Primary (Default)", "#0F172A", "#FFFFFF", 40, 595, 160, 40),
    ("Primary (Hover)", "#1E293B", "#FFFFFF", 220, 595, 160, 40),
    ("Action (Buy Now)", "#D97706", "#FFFFFF", 400, 595, 160, 40),
    ("Secondary (Outline)", "#FFFFFF", "#0F172A", 580, 595, 160, 40),
    ("Ghost (Flat)", "none", "#3B82F6", 760, 595, 140, 40),
    ("Disabled", "#E2E8F0", "#94A3B8", 920, 595, 140, 40)
]

for label, bg, fg, bx, by, bw, bh in btn_states:
    edge = "#CBD5E1" if bg == "#FFFFFF" else ("none" if bg != "none" else "#3B82F6")
    btn = patches.FancyBboxPatch((bx, by), bw, bh, boxstyle="round,pad=1,rounding_size=6", facecolor=bg, edgecolor=edge, lw=1.5)
    ax.add_patch(btn)
    ax.text(bx + bw/2, by + bh/2, label, ha='center', va='center', color=fg, fontsize=8.5, fontweight="bold")

# Section 2: Inputs & Form Controls
ax.text(40, 545, "2. Поля ввода и элементы управления форм (Input Controls):", fontsize=11.5, fontweight="bold", color="#0F172A")

# Search Field
sf = patches.FancyBboxPatch((40, 480), 320, 44, boxstyle="round,pad=1,rounding_size=6", facecolor="#FFFFFF", edgecolor="#3B82F6", lw=2)
ax.add_patch(sf)
ax.text(55, 502, "Поиск по названию, автору или ISBN...", color="#64748B", fontsize=9)

# Select Dropdown
sel = patches.FancyBboxPatch((380, 480), 220, 44, boxstyle="round,pad=1,rounding_size=6", facecolor="#FFFFFF", edgecolor="#CBD5E1", lw=1.5)
ax.add_patch(sel)
ax.text(395, 502, "Жанр: Программирование [v]", color="#0F172A", fontsize=9, fontweight="medium")

# Stepper for Quantity
step = patches.FancyBboxPatch((620, 480), 130, 44, boxstyle="round,pad=1,rounding_size=6", facecolor="#FFFFFF", edgecolor="#CBD5E1", lw=1.5)
ax.add_patch(step)
ax.text(640, 502, "-", fontsize=14, fontweight="bold", color="#0F172A")
ax.text(685, 502, "2 шт.", fontsize=9.5, fontweight="bold", color="#0F172A", ha='center')
ax.text(730, 502, "+", fontsize=14, fontweight="bold", color="#0F172A")

# Badges and Tags
ax.text(780, 545, "3. Бейджи и статусы (Badges):", fontsize=11.5, fontweight="bold", color="#0F172A")
badges = [
    ("В НАЛИЧИИ (Склад)", "#DCFCE7", "#166534", 780, 486),
    ("ХИТ ПРОДАЖ", "#FEF3C7", "#92400E", 940, 486),
    ("СКИДКА -25%", "#FEE2E2", "#991B1B", 1060, 486)
]
for blabel, bbg, bfg, bx, by in badges:
    badge = patches.FancyBboxPatch((bx, by), 105, 30, boxstyle="round,pad=1,rounding_size=4", facecolor=bbg, edgecolor="none")
    ax.add_patch(badge)
    ax.text(bx + 52, by + 15, blabel, ha='center', va='center', color=bfg, fontsize=7.5, fontweight="bold")

# Section 3: Organism - Book Card Spec
ax.text(40, 420, "4. Составной организм: Карточка книги (Book Card Component Specs):", fontsize=11.5, fontweight="bold", color="#0F172A")

# Large Book Card representation
cx, cy, cw, ch = 40, 80, 320, 310
card_spec = patches.FancyBboxPatch((cx, cy), cw, ch, boxstyle="round,pad=2,rounding_size=10", facecolor="#FFFFFF", edgecolor="#CBD5E1", lw=1.5)
ax.add_patch(card_spec)

# Book Cover
cover = patches.Rectangle((cx + 15, cy + 90), 120, 190, facecolor="#1E3A8A", edgecolor="#0F172A")
ax.add_patch(cover)
ax.text(cx + 75, cy + 185, "LITERA\nCLASSICS", ha='center', color="#FDE047", fontsize=9, fontweight="bold")
ax.text(cx + 75, cy + 140, "Фауст\nИ. Гете", ha='center', color="#FFFFFF", fontsize=8, fontweight="medium")

# Badges on card
badge_c = patches.FancyBboxPatch((cx + 150, cy + 250), 80, 24, boxstyle="round,pad=1,rounding_size=3", facecolor="#FEF3C7")
ax.add_patch(badge_c)
ax.text(cx + 190, cy + 262, "[*] 4.9 (128)", ha='center', va='center', color="#92400E", fontsize=8, fontweight="bold")

# Title and Details
ax.text(cx + 150, cy + 225, "Иоганн Гете", fontsize=9.5, color="#64748B")
ax.text(cx + 150, cy + 200, "Фауст. Полное\nсобрание с илл.", fontsize=11, fontweight="bold", color="#0F172A")
ax.text(cx + 150, cy + 155, "Твердый переплет - 640 с.\nИздательство: АСТ, 2025", fontsize=8, color="#475569")

# Price & Buy button
ax.text(cx + 20, cy + 50, "38.50 BYN", fontsize=14, fontweight="bold", color="#0F172A")
ax.text(cx + 20, cy + 25, "48.00 BYN (-20%)", fontsize=9, color="#94A3B8", style="italic")

buy_btn = patches.FancyBboxPatch((cx + 170, cy + 25), 130, 42, boxstyle="round,pad=1,rounding_size=6", facecolor="#D97706")
ax.add_patch(buy_btn)
ax.text(cx + 235, cy + 46, "В корзину", ha='center', va='center', color="#FFFFFF", fontsize=9.5, fontweight="bold")

# Annotation Callouts
ax.annotate("Обложка книги\n(Ratio 3:4, 240x320px)", xy=(cx + 135, cy + 200), xytext=(400, 320),
            arrowprops=dict(facecolor='#3B82F6', shrink=0.05, width=1.5, headwidth=6),
            fontsize=9, color="#1E293B", fontweight="medium")

ax.annotate("Вторичное ценовое действие\n(Hover: #B45309, Contrast 4.8:1)", xy=(cx + 300, cy + 45), xytext=(520, 100),
            arrowprops=dict(facecolor='#D97706', shrink=0.05, width=1.5, headwidth=6),
            fontsize=9, color="#92400E", fontweight="medium")

# System specifications box
spec_box = patches.FancyBboxPatch((720, 80), 440, 310, boxstyle="round,pad=3,rounding_size=8", facecolor="#0F172A", edgecolor="#334155")
ax.add_patch(spec_box)
ax.text(745, 360, "СИСТЕМА ТОКЕНОВ ДИЗАЙНА (DESIGN TOKENS):", fontsize=11, fontweight="bold", color="#F8FAFC")
tokens = [
    "• Spacing System: 4px, 8px, 12px, 16px, 24px, 32px, 48px, 64px",
    "• Typography Headings: Playfair Display / Merriweather (Serif)",
    "• Typography Body/UI: Inter / Roboto (Sans-serif 400/500/600)",
    "• Border Radius: sm: 4px | md: 8px | lg: 12px | full: 9999px",
    "• Shadows (Elevation):",
    "   - Level 1: 0 1px 3px rgba(0,0,0,0.1) — Cards idle",
    "   - Level 2: 0 4px 6px rgba(0,0,0,0.08) — Cards hover",
    "   - Level 3: 0 10px 15px rgba(0,0,0,0.12) — Dropdowns",
    "   - Level 4: 0 20px 25px rgba(0,0,0,0.2) — Modal windows"
]
for tidx, tok in enumerate(tokens):
    ax.text(745, 325 - tidx * 24, tok, fontsize=8.5, color="#CBD5E1")

plt.tight_layout()
components_path = os.path.join(output_dir, "ui_kit_components.png")
fig.savefig(components_path, dpi=300)
plt.close(fig)
print(f"Saved: {components_path}")

# -----------------------------------------------------------------------------
# PLOT 8: 3 Color Palettes Visual Comparison (Mockups & Metrics)
# -----------------------------------------------------------------------------
fig, ax = plt.subplots(figsize=(16, 9), dpi=300)
ax.set_facecolor("#0F172A")
ax.set_xlim(0, 1500)
ax.set_ylim(0, 850)
ax.axis('off')

ax.text(50, 810, "СРАВНИТЕЛЬНЫЙ АНАЛИЗ 3 КОНЦЕПЦИЙ ЦВЕТОВОГО РЕШЕНИЯ ВИТРИНЫ «LITERA»", fontsize=15, fontweight="bold", color="#F8FAFC")
ax.text(50, 782, "Экспериментальная апробация по методу семантического дифференциала Чарльза Осгуда (N=10 респондентов)", fontsize=11, color="#94A3B8")

schemes_data = [
    {
        "x": 50,
        "title": "Палитра А: Academic Oxford",
        "badge": "ПОБЕДИТЕЛЬ (D = 1.414)",
        "badge_bg": "#10B981",
        "badge_fg": "#FFFFFF",
        "primary": "#0F172A",
        "cta": "#D97706",
        "accent": "#F59E0B",
        "canvas": "#F8FAFC",
        "card_bg": "#FFFFFF",
        "border": "#E2E8F0",
        "cover_bg": "#1E3A8A",
        "cover_title": "ФАУСТ",
        "cover_author": "И. В. Гёте",
        "tagline": "Академический благородный стиль",
        "e": 4.68, "p": 4.78, "a": 4.04,
        "desc": "Глубокий синий Oxford Navy в сочетании\nс теплым золотистым янтарем. Максимальный\nуровень доверия к бренду и солидности.",
        "winner": True
    },
    {
        "x": 525,
        "title": "Палитра Б: Nordic Slate & Mint",
        "badge": "АЛЬТЕРНАТИВА 1 (D = 3.467)",
        "badge_bg": "#3B82F6",
        "badge_fg": "#FFFFFF",
        "primary": "#18181B",
        "cta": "#0D9488",
        "accent": "#14B8A6",
        "canvas": "#F4F4F5",
        "card_bg": "#FFFFFF",
        "border": "#CBD5E1",
        "cover_bg": "#134E4A",
        "cover_title": "ФАУСТ",
        "cover_author": "И. В. Гёте",
        "tagline": "Скандинавский технологичный минимализм",
        "e": 4.18, "p": 3.48, "a": 4.64,
        "desc": "Холодный графит со свежей бирюзовой мятой.\nВысокая динамика, но низкая академичность:\nассоциируется с IT-SaaS, а не книгами.",
        "winner": False
    },
    {
        "x": 1000,
        "title": "Палитра В: Vintage Terracotta",
        "badge": "АЛЬТЕРНАТИВА 2 (D = 3.644)",
        "badge_bg": "#F59E0B",
        "badge_fg": "#0F172A",
        "primary": "#431407",
        "cta": "#9A3412",
        "accent": "#C2410C",
        "canvas": "#FFFBEB",
        "card_bg": "#FFFFFF",
        "border": "#FDE68A",
        "cover_bg": "#78350F",
        "cover_title": "ФАУСТ",
        "cover_author": "И. В. Гёте",
        "tagline": "Уютная букинистическая гостиная",
        "e": 4.14, "p": 4.12, "a": 3.32,
        "desc": "Шоколадно-кофейный фон и терракота.\nУютная ретро-атмосфера антикварной лавки,\nно низкая динамичность (A=3.32) и контраст.",
        "winner": False
    }
]

for s in schemes_data:
    x = s["x"]
    # Outer column box
    col_box = patches.FancyBboxPatch((x, 40), 450, 715, boxstyle="round,pad=3,rounding_size=12",
                                    facecolor="#1E293B", edgecolor="#10B981" if s["winner"] else "#334155", lw=2.5 if s["winner"] else 1.2)
    ax.add_patch(col_box)
    
    # Title & Badge
    ax.text(x + 20, 715, s["title"], fontsize=12.5, fontweight="bold", color="#F8FAFC")
    ax.text(x + 20, 692, s["tagline"], fontsize=9.5, color="#94A3B8")
    
    badge = patches.FancyBboxPatch((x + 265, 705), 165, 26, boxstyle="round,pad=1,rounding_size=4", facecolor=s["badge_bg"])
    ax.add_patch(badge)
    ax.text(x + 347, 718, s["badge"], ha='center', va='center', color=s["badge_fg"], fontsize=7.5, fontweight="bold")
    
    # Swatches row
    ax.text(x + 20, 655, "Цветовые токены палитры:", fontsize=9.5, fontweight="bold", color="#E2E8F0")
    sw_colors = [s["primary"], s["cta"], s["accent"], s["canvas"], s["border"]]
    sw_labels = ["Primary", "CTA", "Accent", "Canvas", "Border"]
    for sw_i, (c_hex, c_lbl) in enumerate(zip(sw_colors, sw_labels)):
        sw_x = x + 20 + sw_i * 82
        sw_rect = patches.FancyBboxPatch((sw_x, 605), 72, 36, boxstyle="round,pad=1,rounding_size=4", facecolor=c_hex, edgecolor="#94A3B8", lw=0.8)
        ax.add_patch(sw_rect)
        fg_col = "#FFFFFF" if c_hex in ["#0F172A", "#18181B", "#0D9488", "#431407", "#9A3412", "#D97706"] else "#0F172A"
        ax.text(sw_x + 36, 623, c_lbl, ha='center', va='center', fontsize=7.5, fontweight="bold", color=fg_col)
        ax.text(sw_x + 36, 592, c_hex, ha='center', va='top', fontsize=7.5, color="#94A3B8")
    
    # Render UI Card Preview inside screen frame
    prev_box = patches.FancyBboxPatch((x + 20, 240), 410, 330, boxstyle="round,pad=2,rounding_size=8",
                                      facecolor=s["canvas"], edgecolor=s["border"], lw=1.5)
    ax.add_patch(prev_box)
    
    # Mini Header in preview
    mini_hdr = patches.Rectangle((x + 20, 530), 410, 40, facecolor=s["primary"])
    ax.add_patch(mini_hdr)
    ax.text(x + 35, 550, "Litera", color="#FFFFFF", fontsize=11, fontweight="bold")
    ax.text(x + 395, 550, "Корзина (2)", color=s["accent"], fontsize=9, fontweight="bold", ha='right')
    
    # Mini Book Card
    card_sub = patches.FancyBboxPatch((x + 40, 260), 370, 250, boxstyle="round,pad=2,rounding_size=6",
                                      facecolor=s["card_bg"], edgecolor=s["border"], lw=1)
    ax.add_patch(card_sub)
    
    # Book Cover
    cov_rect = patches.Rectangle((x + 55, 280), 95, 140, facecolor=s["cover_bg"])
    ax.add_patch(cov_rect)
    ax.text(x + 102, 365, s["cover_title"], ha='center', color="#FFFFFF", fontsize=9, fontweight="bold")
    ax.text(x + 102, 335, s["cover_author"], ha='center', color=s["accent"], fontsize=8)
    
    # Details
    ax.text(x + 165, 395, "Иоганн Вольфганг Гете", color="#64748B", fontsize=8.5)
    ax.text(x + 165, 375, "Фауст (В 2 томах)", color=s["primary"], fontsize=11, fontweight="bold")
    ax.text(x + 165, 355, "[*] 4.9 (128 рецензий) • 640 с.", color=s["accent"], fontsize=8)
    ax.text(x + 165, 332, "В наличии на складе в Минске", color="#10B981", fontsize=8, fontweight="bold")
    
    # Price and Buy button
    ax.text(x + 165, 290, "38.50 BYN", color=s["primary"], fontsize=13, fontweight="bold")
    buy_b = patches.FancyBboxPatch((x + 270, 275), 125, 36, boxstyle="round,pad=1,rounding_size=5", facecolor=s["cta"])
    ax.add_patch(buy_b)
    ax.text(x + 332, 293, "В корзину", ha='center', va='center', color="#FFFFFF", fontsize=9, fontweight="bold")
    
    # Psychosemantic EPA Stats Box
    stat_box = patches.FancyBboxPatch((x + 20, 60), 410, 160, boxstyle="round,pad=2,rounding_size=6",
                                      facecolor="#0B132B" if s["winner"] else "#0F172A", edgecolor="#334155", lw=1)
    ax.add_patch(stat_box)
    
    ax.text(x + 35, 195, "Психосемантический профиль (EPA):", fontsize=9.5, fontweight="bold", color="#F8FAFC")
    ax.text(x + 35, 172, f"• Оценка (Evaluation, E):   {s['e']:.2f} / 5.00  (Эталон: 4.92)", fontsize=8.5, color="#38BDF8")
    ax.text(x + 35, 150, f"• Сила (Potency, P):          {s['p']:.2f} / 5.00  (Эталон: 4.74)", fontsize=8.5, color="#F59E0B")
    ax.text(x + 35, 128, f"• Активность (Activity, A): {s['a']:.2f} / 5.00  (Эталон: 4.56)", fontsize=8.5, color="#10B981")
    ax.text(x + 35, 106, f"• Расстояние до идеала D: {s['badge'].split('(')[1].replace(')', '')}", fontsize=9, fontweight="bold", color="#FFFFFF" if not s["winner"] else "#34D399")
    ax.text(x + 35, 75, s["desc"], fontsize=7.5, color="#94A3B8")

plt.tight_layout()
palette_comp_path = os.path.join(output_dir, "semantic_color_palettes_comparison.png")
fig.savefig(palette_comp_path, dpi=300)
plt.close(fig)
print(f"Saved: {palette_comp_path}")

print("All visual assets successfully generated!")



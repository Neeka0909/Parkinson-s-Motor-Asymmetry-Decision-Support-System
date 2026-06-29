# Feature Matrix — Digital Motor Biomarkers

## Internal Features (Captured per Session)

| Feature | Abbrev | Unit | Source Game | Description |
|---------|--------|------|-------------|-------------|
| Reaction Time | RT | ms | Bubble Pop | Time from stimulus onset to first touch |
| Flight Time | FT | ms | Piano Tiles, Typing Race | Time between consecutive taps/keystrokes |
| Hold Time | HT | ms | Typing Race | Duration a key remains pressed |
| Directional Asymmetry | DA | ratio | All | Left-side vs right-side performance ratio |
| RT Variance | RT_var | ms² | Bubble Pop | Session-level standard deviation of RT |
| FT Variance | FT_var | ms² | Piano Tiles | Session-level standard deviation of FT |
| HT Variance | HT_var | ms² | Typing Race | Session-level standard deviation of HT |
| Spatial Accuracy | SA | % | Bubble Pop | Correct target hits / total targets |
| Tap Accuracy | TA | % | Piano Tiles | On-time taps / total tiles |
| Typing Accuracy | TypA | % | Typing Race | Correct characters / total characters |

## External Parameters (User Profile)

| Parameter | Type | Values | Purpose |
|-----------|------|--------|---------|
| Age | integer | 50–90 | Age-normalized baselines |
| Handedness | enum | left, right, ambidextrous | Asymmetry interpretation |
| Time of Day | enum | morning, afternoon, evening, night | Circadian variance control |
| Device Orientation | enum | portrait, landscape | Consistency tracking |
| Language Preference | enum | en, si, mixed | UI localization |

## Longitudinal Derived Features (ML Pipeline)

| Feature | Window | Description |
|---------|--------|-------------|
| RT_rolling_mean_7d | 7 days | Rolling average reaction time |
| RT_rolling_std_7d | 7 days | Rolling RT variability |
| FT_asymmetry_trend | 30 days | Slope of left/right FT difference |
| HT_asymmetry_trend | 30 days | Slope of left/right HT difference |
| Performance_degradation_rate | 30 days | Linear regression slope of composite score |
| Session_consistency | 14 days | Coefficient of variation across sessions |
| Sustained_asymmetry_flag | 14 days | Binary: asymmetry > threshold for ≥5 sessions |

## Risk Profile Output

| Profile | Criteria (longitudinal) | Action |
|---------|------------------------|--------|
| Baseline | No sustained deviation | Continue regular assessments |
| Monitor | Mild asymmetry trend, 1–2 sessions/week | Encourage consistency |
| Elevated | Sustained asymmetry + variance increase | Recommend neurologist consultation |
| Referral | Progressive multi-feature degradation | Mandatory neurologist prompt + PDF report |

## Hand-Side Mapping

- **Bubble Pop:** Left third / center / right third of screen → left / bilateral / right
- **Piano Tiles:** Left column / right column lanes
- **Typing Race:** QWERTY left-hand keys (Q–T, A–G, Z–B) vs right-hand keys (Y–P, H–L, N–M)

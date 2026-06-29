# Literature Review — Key References & Rationale

## Early PD Motor Asymmetry

Parkinson's Disease characteristically presents with **unilateral motor symptom onset** in early stages. Asymmetric bradykinesia, rigidity, and tremor are among the most sensitive clinical indicators during the prodromal and early Hoehn-Yahr stages (Postuma et al., 2015; Berg et al., 2015).

## Digital Biomarkers via Touch & Keystroke Dynamics

### Reaction Time (RT)
- Mobile touch-based RT tasks can detect sub-clinical motor slowing (Zhan et al., 2018).
- Elderly populations show RT increases of 20–40 ms per decade; longitudinal deviation from personal baseline is more informative than cross-sectional norms.

### Flight Time (FT) & Hold Time (HT)
- Keystroke dynamics (dwell time ≈ hold time, flight time between keys) have been used in typing-based PD detection studies (Adi-Japha et al., 2010; Westin et al., 2017).
- Asymmetric HT between dominant and non-dominant hand key regions correlates with lateralized motor dysfunction.

### Longitudinal vs Cross-Sectional
- Single-session motor tests are confounded by fatigue, medication timing, stress, and circadian effects (Espay et al., 2016).
- Continuous mHealth monitoring over weeks/months improves signal-to-noise for progressive neurodegeneration detection.

## Gamification for Elderly Compliance

- Game-based motor assessments increase adherence compared to clinical tap tests (Bot et al., 2014).
- Large typography, high contrast, and localized (Sinhala) interfaces are essential for Sri Lankan elderly populations with varying digital literacy.

## Machine Learning Approaches

- Random Forest and SVM classifiers on multi-feature motor profiles outperform single-feature asymmetry ratios (Arora et al., 2019).
- Rolling window feature engineering (7-day means, 30-day trend slopes) captures progressive degradation patterns.

## Safety & Ethics

- FDA/EU MDR classify diagnostic apps as medical devices; this system is explicitly positioned as **decision-support only** (SaMD Class II consideration if pursued commercially).
- Mandatory disclaimers, no autonomous diagnosis, and neurologist referral prompts are required guardrails.

## References

1. Postuma RB et al. (2015). MDS clinical diagnostic criteria for Parkinson's disease. *Movement Disorders*.
2. Berg D et al. (2015). MDS research criteria for prodromal Parkinson's disease. *Movement Disorders*.
3. Zhan A et al. (2018). Using smartphones and machine learning to quantify Parkinson's disease severity. *JAMA Neurology*.
4. Adi-Japha E et al. (2010). Micrographia in Parkinson's disease: effect on handwriting and keyboard typing. *Movement Disorders*.
5. Westin J et al. (2017). A new computer method for assessing the severity of Parkinson's disease. *Journal of Neurology*.
6. Espay AJ et al. (2016). Technology in Parkinson's disease: challenges and opportunities. *Movement Disorders*.
7. Bot BM et al. (2014). The mPower study, Parkinson disease mobile data collected using ResearchKit. *Scientific Data*.
8. Arora S et al. (2019). Detecting and monitoring the symptoms of Parkinson's disease using smartphones. *NPJ Digital Medicine*.

## Gap Addressed by This System

Existing solutions focus on single-modality tests (finger tapping only) or lack:
- Bilingual elderly UX for Sri Lankan context
- Multi-game composite biomarker profiles
- Explicit longitudinal trend analysis with clinical PDF export
- Non-diagnostic decision-support framing with exercise recommendations

# Judging Engine & Evaluation Strategy

## 1. Assignment Strategy
Judges are assigned to projects within their declared domain expertise (tracks). In `fixtures.json`, judges have assigned tracks, and submissions belong to one track. Evaluations are tracked in the `scores` table.

## 2. Rubric & Scoring Math
The rubric evaluates submissions along three criteria:
- **Functionality** (40% weight)
- **Quality** (30% weight)
- **Innovation** (30% weight)

Raw composite score for evaluation $i$:
$$S_i = 0.40 \cdot \text{Functionality} + 0.30 \cdot \text{Quality} + 0.30 \cdot \text{Innovation}$$

## 3. Cross-Judge Normalization (Z-Score Standardization)
Different judges have different calibration baselines: harsh judges give scores centered at 2.5, while generous judges score around 4.5.

To prevent teams evaluated by tougher judges from being penalized, we calculate Z-scores per judge $j$:
$$Z_{i,j} = \frac{S_{i,j} - \mu_j}{\sigma_j}$$

Where:
- $\mu_j$ is the mean of all scores assigned by judge $j$.
- $\sigma_j$ is the standard deviation of scores assigned by judge $j$.

Final normalized project score is the mean of Z-scores across all independent judges who evaluated the project:
$$\text{Project Score} = \frac{1}{K} \sum_{k=1}^K Z_{k}$$

## 4. Role Isolation Enforcement
Role isolation is guaranteed in `app.py`:
- Judges are authenticated via session cookies.
- Queries for judge score inspection are scoped strictly to `current_user.judge_id`.
- Any attempt to query peer judges returns HTTP `403 Forbidden`.

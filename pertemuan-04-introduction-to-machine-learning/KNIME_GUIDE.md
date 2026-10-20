# Panduan KNIME — Pertemuan 4 (Machine Learning)

> Panduan membangun workflow di **KNIME Analytics Platform 5.x**. Berkas `.knwf` tidak disertakan (harus diekspor dari
> aplikasi). Nama node dapat berbeda antarversi.

Input: `data/mahasiswa_sintetis.csv`

## A. Supervised: klasifikasi kelulusan
1. **CSV Reader**.
2. **Number To String** pada `lulus_tepat` (target klasifikasi harus bertipe string di KNIME).
3. **Partitioning** (75% latih, *Stratified sampling* pada `lulus_tepat`, seed tetap).
4. Model pembanding (tiap model = pasangan Learner → Predictor):
   - **Normalizer** (Z-score) → **Logistic Regression Learner** → **Regression Predictor**/**Logistic Regression Predictor**
   - **Decision Tree Learner** (batasi *Max depth* 4) → **Decision Tree Predictor**
   - **Random Forest Learner** → **Random Forest Predictor**
5. **Scorer** (atau **Scorer (JavaScript)**) per model → *Accuracy*, *F-measure*, matriks konfusi.
6. Validasi silang: **X-Partitioner** (5 fold) … **X-Aggregator**.
7. Baseline: hitung proporsi kelas mayoritas dengan **GroupBy** (Count) agar akurasi model punya pembanding.

**Eksperimen GIGO:** pakai **Rule Engine** + **Math Formula** + random (**Random Number Assigner**) untuk membalik sebagian label latih (10–40%), lalu bandingkan *Accuracy* pada data uji yang bersih.

## B. Unsupervised
1. Hilangkan kolom target (**Column Filter**), lalu **Normalizer**.
2. **k-Means** untuk k = 2…6; hitung kualitas klaster dengan **Silhouette Coefficient** (bila ada di instalasi Anda) atau bandingkan *within-cluster SSE*.
3. **PCA** (2 komponen) → **Scatter Plot** diwarnai klaster dari **Color Manager**.
4. Anomali: **Numeric Outliers** (IQR) per fitur, atau gunakan node deteksi outlier yang tersedia di versi Anda.

## C. Semi-supervised
KNIME tidak punya node Label Spreading bawaan. Dua cara:
- **Python Script** yang menjalankan `LabelSpreading` dari scikit-learn (lihat `kode.py`, bagian 4), atau
- *Self-training* manual: latih model pada 10% berlabel → prediksi sisanya → ambil prediksi berkeyakinan tinggi sebagai label tambahan dalam **Recursive Loop**.

## D. Reinforcement
Tidak natural di KNIME; gunakan **Python Script** dengan kode Q-Learning dari `kode.py` (bagian 5) lalu tampilkan kebijakan dan kurva reward dengan **Line Plot**.

## E. Menjalankan Python di KNIME
Pasang *KNIME Python Integration* dan arahkan ke lingkungan (conda) yang berisi pandas dan scikit-learn.

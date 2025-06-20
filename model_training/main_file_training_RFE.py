# -*- coding: utf-8 -*-

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from logistic_regression_pipeline_RFE import logistic_regression_pipeline_RFE
import seaborn as sns

# Load data
df_input = pd.read_excel(r"D:\Extra data\LBxSF_labeled.xlsx")

# Log-10 transform the protein markers and cfDNA concentration
X = pd.DataFrame()
names_log10_var = ['CA125', 'CA15.3', 'CEA', 'Cyfra 21.1', 'HE4', 'NSE', 'proGRP', 'SCC', 'cfDNA']
for name in names_log10_var:
    X[name] = np.log10(df_input[name])

# Add non-log-transformed features
names_nolog10_var = ['ctDNA', 'Age', 'Gender']
for name in names_nolog10_var:
    X[name] = df_input[name]

# Create binary labels
y_primary = df_input['label'].isin([1, 2]).astype(int)  # LC (1 or 2) vs no LC (0)
y_nsclc = (df_input['label'] == 1).astype(int)  # NSCLC (1) vs others
y_sclc = (df_input['label'] == 2).astype(int)  # SCLC (2) vs others
y_nsclc_vs_sclc = df_input['label'].map({1: 1, 2: 0})  # NSCLC (1) vs SCLC (2), NaN for label=0

# Define the classification problem that will be addressed by the model
problem = 'NSCLC_vs_SCLC'  # Options: 'LC', 'NSCLC', 'SCLC', 'NSCLC_vs_SCLC'
if problem == 'LC':
    names_classes = ['No lung cancer', 'Primary lung carcinoma']
    y = y_primary
    ppv_aim = 0.98
    X_filtered = X
    df_filtered = df_input
elif problem == 'NSCLC':
    names_classes = ['No lung cancer + SCLC', 'NSCLC']
    y = y_nsclc
    ppv_aim = 0.95
    X_filtered = X
    df_filtered = df_input
elif problem == 'SCLC':
    names_classes = ['No lung cancer + NSCLC', 'SCLC']
    y = y_sclc
    ppv_aim = 0.95
    X_filtered = X
    df_filtered = df_input
elif problem == 'NSCLC_vs_SCLC':
    names_classes = ['SCLC', 'NSCLC']
    # Filter to include only NSCLC (label=1) and SCLC (label=2)
    mask = df_input['label'].isin([1, 2])
    X_filtered = X[mask].copy()
    y = y_nsclc_vs_sclc[mask].copy()
    df_filtered = df_input[mask].copy()
    ppv_aim = 0.95

# Define input variables for the model (only protein TMs for RFE)
X_filtered = X_filtered.loc[:, ['CA125', 'CA15.3', 'CEA', 'Cyfra 21.1', 'HE4', 'NSE', 'proGRP', 'SCC']]

# Names of the input variables
names_TMs = list(X_filtered)
# Define continuous variables for standardization
cnt_var = ['CA125', 'CA15.3', 'CEA', 'Cyfra 21.1', 'HE4', 'NSE', 'proGRP', 'SCC']
solver = 'saga'

# Define the number of features to select
n_features_to_select = [1, 2, 3, 4, 5, 6, 7, 8]

# Initialize lists to store results
performances_per_threshold_val_nfeatures = []
performance_val_nfeatures = []
predicted_prob_nfeatures = []
predicted_class_nfeatures = []
percentage_class_one_nfeatures = []
y_pred_val_percv_nfeatures = []
y_pred_class_per_cv_nfeatures = []
performances_per_threshold_train_nfeatures = []
performances_train_nfeatures = []
predicted_prob_train_nfeatures = []
val_indices_nfeatures = []
coefficients_nfeatures = []
prob_thresholds_nfeatures = []
logregs_nfeatures = []
scalers_nfeatures = []
ranking_nfeatures = []
selected_features_all_nfeatures = []

logregs_above_thresh_nfeatures = []
scalers_above_thresh_nfeatures = []
prob_thresholds_above_thresh_nfeatures = []
val_indices_above_thresh_nfeatures = []
y_pred_class_percv_above_thresh_nfeatures = []
y_pred_val_percv_above_thresh_nfeatures = []
selected_features_all_above_thresh_nfeatures = []
ranking_above_thresh_nfeatures = []
predicted_class_above_thresh_nfeatures = []
predicted_prob_above_thresh_nfeatures = []
performance_val_above_thresh_nfeatures = []
percentage_class_one_above_thresh_nfeatures = []
cvfolds_above_thresh = []

for n_features in n_features_to_select:
    print('Fitting model with %d features' % n_features)
    [performances_per_threshold_val, performance_val, predicted_prob, predicted_class,
     percentage_class_one, y_pred_val_percv, y_pred_class_percv, performances_per_threshold_train,
     performances_train, predicted_prob_train, val_indices, probabilities, coefficients,
     prob_thresholds, logregs, scalers, ranking, selected_features_all] = logistic_regression_pipeline_RFE(
        X_filtered, y, names_TMs, cnt_var, names_classes, solver, n_features)

    performances_per_threshold_val_nfeatures.append(performances_per_threshold_val)
    performance_val_nfeatures.append(performance_val)
    predicted_prob_nfeatures.append(predicted_prob)
    predicted_class_nfeatures.append(predicted_class)
    percentage_class_one_nfeatures.append(percentage_class_one)
    y_pred_val_percv_nfeatures.append(y_pred_val_percv)
    y_pred_class_per_cv_nfeatures.append(y_pred_class_percv)
    performances_per_threshold_train_nfeatures.append(performances_per_threshold_train)
    performances_train_nfeatures.append(performances_train)
    predicted_prob_train_nfeatures.append(predicted_prob_train)
    val_indices_nfeatures.append(val_indices)
    coefficients_nfeatures.append(coefficients)
    prob_thresholds_nfeatures.append(prob_thresholds)
    logregs_nfeatures.append(logregs)
    scalers_nfeatures.append(scalers)
    ranking_nfeatures.append(ranking)
    selected_features_all_nfeatures.append(selected_features_all)

    # Filter folds where training set met the pre-set PPV
    n_splits = len(logregs)
    logregs_above_thresh = []
    scalers_above_thresh = []
    prob_thresholds_above_thresh = []
    val_indices_above_thresh = []
    y_pred_class_percv_above_thresh = []
    y_pred_val_percv_above_thresh = []
    selected_features_all_above_thresh = []
    ranking_above_thresh = []
    for i in range(0, len(logregs)):
        if sum(performances_per_threshold_train[:, 2, i] >= ppv_aim) > 0:
            logregs_above_thresh.append(logregs[i])
            scalers_above_thresh.append(scalers[i])
            prob_thresholds_above_thresh.append(prob_thresholds[i])
            val_indices_above_thresh.append(val_indices[i])
            y_pred_class_percv_above_thresh.append(y_pred_class_percv[i])
            y_pred_val_percv_above_thresh.append(y_pred_val_percv[i])

    selected_features_all_above_thresh = selected_features_all.transpose()[
        sum(performances_per_threshold_train[:, 2, :] >= ppv_aim) > 0].transpose()
    ranking_above_thresh = ranking.transpose()[
        sum(performances_per_threshold_train[:, 2, :] >= ppv_aim) > 0].transpose()

    performance_val_above_thresh = performance_val[sum(performances_per_threshold_train[:, 2, :] >= ppv_aim) > 0]
    print('CV-folds where training set could meet pre-set PPV: %3.1f%%' % (
            len(performance_val_above_thresh) / len(performance_val) * 100.0))
    print('Performances for these CV-folds:')
    for i in ['Sens val', 'Spec val', 'PPV val', 'NPV val', 'AUC val']:
        print('%s: %3.3f (%3.3f - %3.3f)' % (
            i, performance_val_above_thresh.loc[:, i].median(),
            performance_val_above_thresh.loc[:, i].quantile(q=0.25),
            performance_val_above_thresh.loc[:, i].quantile(q=0.75)))

    # Save predicted probabilities and classes for folds meeting PPV criteria
    predicted_class_above_thresh = np.ones((len(y), n_splits)) * np.nan
    predicted_prob_above_thresh = np.ones((len(y), n_splits)) * np.nan

    for i in range(0, len(val_indices_above_thresh)):
        predicted_class_above_thresh[val_indices_above_thresh[i], i] = y_pred_class_percv_above_thresh[i]
        predicted_prob_above_thresh[val_indices_above_thresh[i], i] = y_pred_val_percv_above_thresh[i]

    # Compute percentage classified as class one
    percentage_class_one_above_thresh = []
    for i in range(0, len(percentage_class_one)):
        percentage_class_one_above_thresh.append(
            sum(predicted_class_above_thresh[i, :] == 1) / (n_splits - sum(np.isnan(predicted_class_above_thresh[i, :]))) * 100.0)

    logregs_above_thresh_nfeatures.append(logregs_above_thresh)
    scalers_above_thresh_nfeatures.append(scalers_above_thresh)
    prob_thresholds_above_thresh_nfeatures.append(prob_thresholds_above_thresh)
    val_indices_above_thresh_nfeatures.append(val_indices_above_thresh)
    y_pred_class_percv_above_thresh_nfeatures.append(y_pred_class_percv_above_thresh)
    y_pred_val_percv_above_thresh_nfeatures.append(y_pred_val_percv_above_thresh)
    selected_features_all_above_thresh_nfeatures.append(selected_features_all_above_thresh)
    ranking_above_thresh_nfeatures.append(ranking_above_thresh)
    predicted_class_above_thresh_nfeatures.append(predicted_class_above_thresh)
    predicted_prob_above_thresh_nfeatures.append(predicted_prob_above_thresh)
    performance_val_above_thresh_nfeatures.append(performance_val_above_thresh)
    percentage_class_one_above_thresh_nfeatures.append(percentage_class_one_above_thresh)
    cvfolds_above_thresh.append(len(logregs_above_thresh) / n_splits * 100.0)

# Make a table with median (IQR) performance metrics for CV-folds meeting PPV criteria
performance_metrics_names = ['Sens val', 'Spec val', 'PPV val', 'NPV val', 'AUC val']
performance_metrics_table_above_thresh = pd.DataFrame()
performance_metrics_table_above_thresh['Number features'] = n_features_to_select
performance_metrics_table_above_thresh['CV folds PPV criteria'] = cvfolds_above_thresh

for j in range(0, len(performance_metrics_names)):
    performance_metric = []
    for i in range(0, len(n_features_to_select)):
        performance_metric.append('%3.2f (%3.2f-%3.2f)' % (
            performance_val_above_thresh_nfeatures[i].loc[:, performance_metrics_names[j]].median(),
            performance_val_above_thresh_nfeatures[i].loc[:, performance_metrics_names[j]].quantile(q=0.25),
            performance_val_above_thresh_nfeatures[i].loc[:, performance_metrics_names[j]].quantile(q=0.75)))
    performance_metrics_table_above_thresh['%s' % performance_metrics_names[j]] = performance_metric

print(performance_metrics_table_above_thresh)

# Show variables selected per number of features for CV-folds meeting PPV criteria
selected_features_matrix_above_thresh = np.zeros((len(names_TMs), len(n_features_to_select)))

for i in range(0, len(n_features_to_select)):
    selected_features_matrix_above_thresh[:, i] = sum(
        selected_features_all_above_thresh_nfeatures[i].transpose()) / \
        selected_features_all_above_thresh_nfeatures[i].shape[1] * 100.0

plt.figure()
sns.heatmap(selected_features_matrix_above_thresh, annot=True, fmt=".0f", cmap="Blues")
plt.xticks(ticks=np.linspace(0.5, len(n_features_to_select) - 0.5, len(n_features_to_select)), labels=n_features_to_select)
plt.xlabel('Number of selected features')
plt.yticks(ticks=np.linspace(0.5, len(names_TMs) - 0.5, len(names_TMs)), labels=names_TMs, rotation=0)
plt.ylabel('Input variables')
plt.tight_layout()

# Save results with problem-specific filenames
file_prefix = problem.lower()  # Convert to lowercase (e.g., 'lc', 'nsclc', 'sclc', 'nsclc_vs_sclc')

# Save performance metrics table
performance_metrics_table_above_thresh.to_csv(f"{file_prefix}_performance_metrics_table.csv")
print(f"Performance metrics saved to {file_prefix}_performance_metrics_table.csv")

# Save selected features matrix
np.savetxt(f"{file_prefix}_selected_features_matrix.csv", selected_features_matrix_above_thresh, delimiter=",",
           header=",".join([str(n) for n in n_features_to_select]), comments="")
print(f"Selected features matrix saved to {file_prefix}_selected_features_matrix.csv")

# Save predicted probabilities (for first n_features as example)
np.savetxt(f"{file_prefix}_predicted_prob_above_thresh.csv", predicted_prob_above_thresh_nfeatures[0], delimiter=",")
print(f"Predicted probabilities saved to {file_prefix}_predicted_prob_above_thresh.csv")

# Save heatmap
plt.savefig(f"{file_prefix}_feature_selection_heatmap.png", dpi=300, bbox_inches='tight')
print(f"Heatmap saved to {file_prefix}_feature_selection_heatmap.png")
plt.close()
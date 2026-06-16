# train_model.py - Applied ML Classifier Training Pipeline
import os
import sys
import pickle
import pandas as pd
import numpy as np

# Reconfigure stdout to support UTF-8 characters on Windows consoles
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, confusion_matrix
from sklearn.pipeline import Pipeline

# Paths
DATASET_DIR = "project_dataset"
FEATURES_CSV = os.path.join(DATASET_DIR, "code_features.csv")
MODEL_PKL = os.path.join(DATASET_DIR, "complexity_classifier.pkl")

def train_pipeline():
    print("=" * 60)
    print("🚀 Starting Machine Learning Model Training Pipeline")
    print("=" * 60)

    # 1. Load dataset
    if not os.path.exists(FEATURES_CSV):
        raise FileNotFoundError(f"Dataset CSV not found at: {FEATURES_CSV}. Please run data_harvester.py first.")
        
    print(f"Loading dataset from: {FEATURES_CSV}...")
    df = pd.read_csv(FEATURES_CSV)
    print(f"Dataset loaded successfully. Shape: {df.shape}")

    # 2. Clean missing/null data blocks and validate
    print("\n[Data Cleaning & Validation]")
    initial_rows = len(df)
    
    # Drop rows where critical feature columns or target are null
    feature_cols = [
        "loc", "nested_loops", "silent_exceptions", 
        "mutable_defaults", "global_vars", "raw_new_count", 
        "unsafe_copies"
    ]
    target_col = "is_vulnerable"
    
    df = df.dropna(subset=feature_cols + [target_col])
    dropped_rows = initial_rows - len(df)
    if dropped_rows > 0:
        print(f"⚠️ Dropped {dropped_rows} rows containing null values.")
    else:
        print("✅ No null values found. Dataset is clean.")

    # Ensure clean types
    for col in feature_cols:
        df[col] = df[col].astype(float)
    df[target_col] = df[target_col].astype(int)

    X = df[feature_cols]
    y = df[target_col]

    # Check for empty dataset
    if len(df) == 0:
        raise ValueError("Dataset is empty after removing null values. Cannot train model.")

    # 3. Split dataset into Train, Validation, and Test (70/15/15 split)
    print("\n[Dataset Splitting]")
    print(f"Total samples available: {len(df)}")
    
    # Calculate unique classes and counts
    classes, counts = np.unique(y, return_counts=True)
    print("Class distribution:")
    for cls, count in zip(classes, counts):
        print(f"  Class {cls}: {count} samples")

    # Handle tiny datasets gracefully (like our mock dataset with 10 rows)
    if len(df) < 5:
        print("⚠️ Dataset is too small for standard 70/15/15 splitting. Using entire dataset for training and testing.")
        X_train, y_train = X, y
        X_val, y_val = X, y
        X_test, y_test = X, y
    else:
        # Perform 70/15/15 split
        # First split off the training set (70%) and a temporary set (30%)
        try:
            # Try stratified split first
            X_train, X_temp, y_train, y_temp = train_test_split(
                X, y, test_size=0.30, random_state=42, stratify=y
            )
            # Split the temporary set (30%) into validation (50% of temp -> 15% of total) and test (50% of temp -> 15% of total)
            X_val, X_test, y_val, y_test = train_test_split(
                X_temp, y_temp, test_size=0.50, random_state=42, stratify=y_temp
            )
            print("✅ Stratified 70/15/15 split completed successfully.")
        except Exception as e:
            print(f"⚠️ Stratified split failed ({e}). Falling back to non-stratified random split...")
            # Fallback to random splits if class sizes are too small for stratification
            X_train, X_temp, y_train, y_temp = train_test_split(
                X, y, test_size=0.30, random_state=42
            )
            X_val, X_test, y_val, y_test = train_test_split(
                X_temp, y_temp, test_size=0.50, random_state=42
            )
            print("✅ Non-stratified random 70/15/15 split completed successfully.")

    print(f"  Training set: {len(X_train)} samples")
    print(f"  Validation set: {len(X_val)} samples")
    print(f"  Testing set: {len(X_test)} samples")

    # 4. Define and Train Pipeline (Standardizer + Random Forest Classifier)
    print("\n[Model Architecture & Training]")
    # We use a pipeline to bundle scaling and modeling to ensure no data leakage during prediction
    pipeline = Pipeline([
        ('scaler', StandardScaler()),
        ('classifier', RandomForestClassifier(n_estimators=50, max_depth=5, random_state=42))
    ])
    
    print("Fitting Standardizer and Random Forest Classifier on training data...")
    pipeline.fit(X_train, y_train)
    print("✅ Model training completed.")

    # 5. Evaluate Performance
    print("\n" + "="*30 + " EVALUATION METRICS " + "="*30)
    
    def print_metrics(name, X_split, y_true):
        y_pred = pipeline.predict(X_split)
        
        acc = accuracy_score(y_true, y_pred)
        # Using zero_division=0 to handle case where no positive predictions are made in tiny splits
        prec = precision_score(y_true, y_pred, zero_division=0)
        rec = recall_score(y_true, y_pred, zero_division=0)
        f1 = f1_score(y_true, y_pred, zero_division=0)
        cm = confusion_matrix(y_true, y_pred)
        
        print(f"📊 {name} Set Metrics:")
        print(f"  Accuracy  : {acc:.4f}")
        print(f"  Precision : {prec:.4f}")
        print(f"  Recall    : {rec:.4f}")
        print(f"  F1-Score  : {f1:.4f}")
        print(f"  Confusion Matrix:")
        print(f"    {cm[0] if len(cm) > 0 else 'N/A'}")
        print(f"    {cm[1] if len(cm) > 1 else 'N/A'}")
        print("-" * 40)
        
    print_metrics("TRAIN", X_train, y_train)
    print_metrics("VALIDATION", X_val, y_val)
    print_metrics("TEST", X_test, y_test)

    # 6. Save model artifact
    print("\n[Saving Model Artifact]")
    os.makedirs(DATASET_DIR, exist_ok=True)
    with open(MODEL_PKL, 'wb') as model_file:
        pickle.dump(pipeline, model_file)
        
    print(f"✅ Trained pipeline (Standardizer + RandomForest) saved cleanly to: {MODEL_PKL}")
    print("=" * 60)

if __name__ == "__main__":
    train_pipeline()

# train_eval.py
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.metrics import r2_score, mean_squared_error
import matplotlib.pyplot as plt
import joblib
import os
from xgboost import XGBRegressor
from config import DATA_DIR, MODEL_DIR, TEST_DIR


def train_and_eval(dataset_csv=DATA_DIR / "dataset.csv"):
    # train_eval.py snippet: choose relative target
    df = pd.read_csv(DATA_DIR / "dataset.csv")
    # feature columns same as before (static + flags)
    all_flags = ['-O1','-O2','-O3','-Ofast','-Os','-funroll-loops','-ftree-vectorize','-ffast-math','-march','-flto']
    X_cols = ['num_for','num_while','num_if','num_funcs','num_brackets','loc'] + [f'has_{fl}' for fl in all_flags]
    X_cols = [c for c in X_cols if c in df.columns]
    X = df[X_cols].fillna(0)

    # target: log(runtime / baseline) -> model learns multiplicative effect of flags
    y = np.log(df['runtime'].values) - np.log(df['baseline_O3_time'].values)

    # train/test split and model as before
    X_train, X_test, y_train, y_test = train_test_split(df[X_cols], y, test_size=0.25, random_state=42)
    model =XGBRegressor(
    n_estimators=300,
    max_depth=4,
    learning_rate=0.05,
    subsample=0.9,
    colsample_bytree=0.7,
    objective='reg:squarederror',
    tree_method="hist",
    n_jobs=4)
    model.fit(X_train, y_train)

    # evaluate: predict relative log and convert back to runtime for reporting
    y_pred_log_rel = model.predict(X_test)
    # predicted runtime = baseline * exp(pred_log_rel)
    baseline_test = df.loc[y_test.index, 'baseline_O3_time'] if hasattr(y_test, 'index') else df['baseline_O3_time'].iloc[X_test.index]
    # compute actual runtimes for error metrics
    y_test_runtime = np.exp(y_test) * baseline_test  # because y_test = log(actual / baseline)
    y_pred_runtime = np.exp(y_pred_log_rel) * baseline_test

    from sklearn.metrics import r2_score, mean_squared_error
    print("R² on runtime scale:", r2_score(y_test_runtime, y_pred_runtime))
    print("RMSE on runtime scale:", np.sqrt(mean_squared_error(y_test_runtime, y_pred_runtime)))
    # Feature importances
    importances = model.feature_importances_
    idx = np.argsort(importances)[::-1]
    top = [(X_cols[i], importances[i]) for i in idx[:15]]
    print("Top features:")
    for name, imp in top:
        print(f"  {name}: {imp:.4f}")
    # plot
    '''plt.figure(figsize=(10,5))
    plt.bar([n for n,_ in top], [v for _,v in top])
    plt.xticks(rotation=45)
    plt.title("Top feature importances")
    plt.tight_layout()
    plt.savefig("feature_importances.png")
    print("Saved feature_importances.png")'''

    #saving the model
    MODEL_PATH = os.path.join(MODEL_DIR, "xgb_model_main.joblib")
    os.makedirs(MODEL_DIR, exist_ok=True)
    joblib.dump(model,MODEL_PATH)
    print(f"Saved XGB model -> {MODEL_PATH}")
    return model

if __name__ == "__main__":
    train_and_eval()
    

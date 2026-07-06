# -*- coding: utf-8 -*-
"""
Created on Sun Feb 15 21:45:25 2026

@author: 33133
"""

import pandas as pd
import numpy as np

from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import r2_score, mean_squared_error, mean_absolute_error
from itertools import combinations
import matplotlib.pyplot as plt
import seaborn as sns



df = pd.read_csv(r"D:\桌面\数据集4（模型训练） .CSV", encoding='gbk')
trait_cols = [col for col in df.columns if col not in ['Trait','Group','N','Nue',
                                                       '备注','行号','新备注','数据个数','年份']]
traits = df[trait_cols]
feature_all =df.copy()

for t1, t2 in combinations(trait_cols, 2):
    interaction_name = f"{t1}×{t2}"
    feature_all[interaction_name] = df[t1] * df[t2]
    
#######################################################
#统一评估函数
def evaluate_model(model, X_train, X_test, y_train, y_test):
    model.fit(X_train, y_train)
    predictions = model.predict(X_test)

    r2 = r2_score(y_test, predictions)
    rmse = np.sqrt(mean_squared_error(y_test, predictions))
    mae = mean_absolute_error(y_test, predictions)
    mape = np.mean(np.abs((y_test - predictions) / y_test)) * 100

    print("R²:", round(r2, 3))
    print("RMSE:", round(rmse, 3))
    print("MAE:", round(mae, 3))
    print("MAPE:", round(mape, 2), "%")
    print("-" * 40)
    #########################################
    ##预测图
    plt.figure(figsize=(12,5))

    plt.subplot(1,2,1)
    sns.scatterplot(x=y_test, y=predictions, alpha=0.6)
    plt.plot([min(y_test), max(y_test)], [min(y_test), max(y_test)], 
             color='red', linestyle='--', label='Ideal Fit')
    plt.xlabel("real", fontsize=12)
    plt.ylabel("predict", fontsize=12)
    plt.title("real vs predict", fontsize=14)
    plt.legend()
    # 在图上标注指标
    plt.text(min(y_test), max(predictions), f"R² = {r2:.3f}\nRMSE = {rmse:.3f}\nMAE = {mae:.3f}", 
             fontsize=10, color="blue")
    
    ########################################
    ##特征重要性图
    importances = model.feature_importances_
    feature_importances = sorted(zip(feature_cols, importances), key=lambda x:x[1], reverse=True)
    for f, imp in feature_importances:
        print(f"Variable: {f:15} importance: {imp:.3f}")
    #直方图
    features, importances = zip(*feature_importances)
    plt.figure(figsize=(8,5))
    plt.bar(features, importances, color='skyblue')
    plt.xlabel('features')
    plt.ylabel('importance')
    plt.title('RF-importance-list')
    plt.xticks(rotation=-45, ha='left')
    plt.show() 
    
    
    return r2, rmse, mae, mape

#######################################################
##N浓度
feature_cols = ['length', 'width', 'H', 'S', 'area×length', 'area×V', 'length×S',
                'length×DOCI', 'width×S', 'width×V', 'width×DOCI', 'H×S', 'H×DOCI',
                'H×T_weight', 'S×DOCI', 'T_weight×Yield']

X = feature_all[feature_cols]
y_N = feature_all['N']
X_train, X_test, y_train, y_test = train_test_split(X, y_N, test_size=0.20, random_state=46)

rf_N = RandomForestRegressor(
    n_estimators=1400,
    max_depth=11,
    max_features='log2',
    min_samples_split=6,
    min_samples_leaf=2,
    bootstrap=False,
    random_state=21,
    n_jobs=-1
)
rf_N.fit(X_train, y_train)
evaluate_model(rf_N, X_train, X_test, y_train, y_test)
###############################################################
##N利用效率
feature_cols = ['T_weight', 'H×Vol', 'H×H_weight', 'H×Yield', 'DOCI×H_weight', 
                'Vol×H_weight', 'Vol×T_weight', 'H_weight×Yield']

X = feature_all[feature_cols]
y_NUE = feature_all['Nue']
X_train, X_test, y_train, y_test = train_test_split(X, y_NUE, test_size=0.20, random_state=46)

####模型训练
rf_NUE = RandomForestRegressor(
    n_estimators=2300,
    max_depth=11,
    max_features='log2',
    min_samples_split=6,
    min_samples_leaf=2,
    bootstrap=False,
    random_state=21,
    n_jobs=-1
)
rf_NUE.fit(X_train, y_train)
evaluate_model(rf_NUE, X_train, X_test, y_train, y_test)




import joblib

joblib.dump(rf_N, "rf_N.pkl")
joblib.dump(rf_NUE, "rf_NUE.pkl")

N_REQUIRED_RAW_FEATURES = [
    "length", "width", "H", "S", "area", "V", "DOCI", "T_weight", "Yield"
]

NUE_REQUIRED_RAW_FEATURES = [
    "T_weight", "H", "Vol", "H_weight", "DOCI", "Yield"
]


def build_n_input(sample):
    """Build the feature row required by the N model."""
    row = {
        "length": sample["length"],
        "width": sample["width"],
        "H": sample["H"],
        "S": sample["S"],
        "area脳length": sample["area"] * sample["length"],
        "area脳V": sample["area"] * sample["V"],
        "length脳S": sample["length"] * sample["S"],
        "length脳DOCI": sample["length"] * sample["DOCI"],
        "width脳S": sample["width"] * sample["S"],
        "width脳V": sample["width"] * sample["V"],
        "width脳DOCI": sample["width"] * sample["DOCI"],
        "H脳S": sample["H"] * sample["S"],
        "H脳DOCI": sample["H"] * sample["DOCI"],
        "H脳T_weight": sample["H"] * sample["T_weight"],
        "S脳DOCI": sample["S"] * sample["DOCI"],
        "T_weight脳Yield": sample["T_weight"] * sample["Yield"],
    }
    return pd.DataFrame([row], columns=[
        "length", "width", "H", "S", "area脳length", "area脳V", "length脳S",
        "length脳DOCI", "width脳S", "width脳V", "width脳DOCI", "H脳S",
        "H脳DOCI", "H脳T_weight", "S脳DOCI", "T_weight脳Yield"
    ])


def build_nue_input(sample):
    """Build the feature row required by the NUE model."""
    row = {
        "T_weight": sample["T_weight"],
        "H脳Vol": sample["H"] * sample["Vol"],
        "H脳H_weight": sample["H"] * sample["H_weight"],
        "H脳Yield": sample["H"] * sample["Yield"],
        "DOCI脳H_weight": sample["DOCI"] * sample["H_weight"],
        "Vol脳H_weight": sample["Vol"] * sample["H_weight"],
        "Vol脳T_weight": sample["Vol"] * sample["T_weight"],
        "H_weight脳Yield": sample["H_weight"] * sample["Yield"],
    }
    return pd.DataFrame([row], columns=[
        "T_weight", "H脳Vol", "H脳H_weight", "H脳Yield", "DOCI脳H_weight",
        "Vol脳H_weight", "Vol脳T_weight", "H_weight脳Yield"
    ])


def read_float(prompt):
    while True:
        value = input(prompt).strip()
        try:
            return float(value)
        except ValueError:
            print("请输入数字。")


def predict_single_sample(rf_n_model, rf_nue_model):
    print("\n请输入单个样本的原始特征值：")
    sample = {}

    for name in [
        "length", "width", "H", "S", "area", "V", "DOCI",
        "T_weight", "Yield", "Vol", "H_weight"
    ]:
        sample[name] = read_float(f"{name}: ")

    true_n = input("真实N值（直接回车可跳过）: ").strip()
    true_nue = input("真实Nue值（直接回车可跳过）: ").strip()

    n_input = build_n_input(sample)
    nue_input = build_nue_input(sample)

    pred_n = rf_n_model.predict(n_input)[0]
    pred_nue = rf_nue_model.predict(nue_input)[0]

    print("\n========== 结果 ==========")
    if true_n:
        print(f"真实氮浓度 N   : {float(true_n):.4f}")
    else:
        print("真实氮浓度 N   : 未输入")
    print(f"预测氮浓度 N   : {pred_n:.4f}")

    if true_nue:
        print(f"真实氮利用效率 : {float(true_nue):.4f}")
    else:
        print("真实氮利用效率 : 未输入")
    print(f"预测氮利用效率 : {pred_nue:.4f}")


if __name__ == "__main__":
    predict_single_sample(rf_N, rf_NUE)



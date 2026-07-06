import sys
import os
import re
import faulthandler
import logging
import traceback
from datetime import datetime
from pathlib import Path

import joblib
import numpy as np
from PySide6.QtWidgets import (
    QApplication, QWidget, QFileDialog, QMessageBox, QProgressBar, QSizePolicy
)
from PySide6.QtCore import QObject, Signal, QThread, Qt, QEvent
from PySide6.QtGui import QPixmap, QColor, QDoubleValidator
from openpyxl import Workbook, load_workbook

from MaizeDesider_GPT1_ui import Ui_Form


BASE_DIR = Path(getattr(sys, "_MEIPASS", Path(__file__).resolve().parent))
APP_DIR = Path(sys.executable).resolve().parent if getattr(sys, "frozen", False) else Path(__file__).resolve().parent
LOG_DIR = APP_DIR / "logs"
LOG_DIR.mkdir(parents=True, exist_ok=True)
LOG_FILE = LOG_DIR / "app.log"
CRASH_LOG_FILE = LOG_DIR / "native_crash.log"
_crash_log_handle = open(CRASH_LOG_FILE, "a", encoding="utf-8")
faulthandler.enable(_crash_log_handle, all_threads=True)
logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)


def log_uncaught_exception(exc_type, exc_value, exc_traceback):
    logging.critical(
        "Uncaught exception",
        exc_info=(exc_type, exc_value, exc_traceback),
    )
    traceback.print_exception(exc_type, exc_value, exc_traceback)


sys.excepthook = log_uncaught_exception


def resource_path(file_name):
    return BASE_DIR / file_name


# =========================
# 图像处理线程
# =========================
class ImageProcessWorker(QObject):
    finished = Signal(dict)

    def process(self, image_input):
        """
        输入:image_path
        输出:dict(颜色特征 + 籽粒形态特征)
        """
        logging.info("Start image feature extraction: %s", image_input)
        try:
            from yolo_sam_features import extract_features

            sample_name = None
            if isinstance(image_input, dict):
                sample_name = image_input.get("name")
            result = extract_features(image_input, sample_name=sample_name)
        except Exception as e:
            logging.exception("Image feature extraction failed")
            result = {"error": str(e)}
        finally:
            logging.info("Finish image feature extraction")

        self.finished.emit(result)


# =========================
# 随机森林预测线程
# =========================
class PredictWorker(QObject):
    finished = Signal(dict)

    def __init__(self):
        super().__init__()

        # ===== 加载模型 =====
        self.model_N = joblib.load(resource_path("rf_N.pkl"))
        self.model_NUE = joblib.load(resource_path("rf_NUE.pkl"))

    def predict(self, f):
        try:
            # ===== 基础变量 =====
            H = f["H"]
            S = f["S"]
            V = f["V"]
            DOCI = f["DOCI"]

            # 界面显示/用户输入使用实际测量值；随机森林按训练时口径使用 8.628 倍长度宽度、74.446 倍面积。
            length = f["length"] *8.628
            width = f["width"] * 8.628
            area = f["area"] * 74.446
            H_weight = f["Hweight"]
            T_weight = f["Tweight"]
            Yield = f["Yield"]
            Vol = f["Vol"]

            # ===== N 模型特征 =====
            X_N = np.array([[
                H,
                S,
                Yield,
                area * length,
                length * H,
                width * V,
                H * S,
                H * V,
                S * V,
                T_weight * Yield
            ]])

            # ===== NUE 模型特征 =====
            X_NUE = np.array([[
                T_weight,
                H * Vol,
                H * H_weight,
                H * Yield,
                DOCI * H_weight,
                Vol * H_weight,
                Vol * T_weight,
                H_weight * Yield
            ]])

            # ===== 预测 =====
            N_pred = self.model_N.predict(X_N)[0]
            NUE_pred = self.model_NUE.predict(X_NUE)[0]

            result = {
                "N": round(N_pred, 4),
                "NUE": round(NUE_pred, 4)
            }

            self.finished.emit(result)

        except Exception as e:
            self.finished.emit({
                "N": "error",
                "NUE": str(e)
            })

# =========================
# 主界面
# =========================
class MyWindow(QWidget, Ui_Form):

    # 信号（用于跨线程调用）
    start_image_process = Signal(object)
    start_predict = Signal(dict)

    def __init__(self):
        super().__init__()
        self.setupUi(self)

        self.current_image_path = None
        self.current_image_name = ""
        self.image_paths = {}
        self.image_pairs = {}
        self.all_image_names = []
        self.excel_file_path = None
        self._updating_combo = False
        self._left_image_path = None
        self._right_image_path = None
        self.current_perimeter = None
        self.current_aspect_ratio = None
        self.current_circularity = None
        self.current_output_time = None

        self.init_interface()
        self.init_threads()
        self.bind_signals()
        self.update_action_state()

    # =========================
    # 初始化界面增强
    # =========================
    def init_interface(self):
        self.setMinimumSize(980, 640)
        self.apply_app_style()
        self.setup_responsive_layout()
        self.setup_field_behavior()
        self.setup_prediction_chart()
        self.statusLabel.setText("状态：请选择图片文件夹")

    def apply_app_style(self):
        self.setStyleSheet("""
            QWidget {
                font-family: "Microsoft YaHei";
                font-size: 10pt;
                color: #263238;
                background: #F6F8FA;
            }
            QGroupBox {
                font-weight: 600;
                border: 1px solid #D6DEE6;
                border-radius: 8px;
                margin-top: 12px;
                padding: 10px;
                background: #FFFFFF;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 6px;
                color: #174A63;
            }
            QLineEdit, QComboBox {
                min-height: 26px;
                border: 1px solid #CAD4DD;
                border-radius: 5px;
                padding: 2px 6px;
                background: #FFFFFF;
                selection-background-color: #8EC6D8;
            }
            QLineEdit:focus, QComboBox:focus {
                border: 1px solid #2B8FB8;
                background: #FBFEFF;
            }
            QLineEdit[readOnly="true"] {
                color: #0D4F67;
                background: #EEF8FB;
                font-weight: 600;
            }
            QPushButton {
                min-height: 30px;
                border: 1px solid #257A9E;
                border-radius: 6px;
                padding: 4px 10px;
                color: #FFFFFF;
                background: #2B8FB8;
                font-weight: 600;
            }
            QPushButton:hover {
                background: #237FA4;
            }
            QPushButton:pressed {
                background: #196A8B;
            }
            QPushButton:disabled {
                color: #7D8B94;
                border-color: #D0D8DE;
                background: #E9EEF2;
            }
            QLabel#imageLabelLeft, QLabel#imageLabelRight {
                background-color: #F9FBFC;
                border: 1px dashed #B7C7D1;
                border-radius: 6px;
                color: #7A8A93;
            }
            QLabel#colorLabel {
                background-color: white;
                border: 1px solid #AEBBC4;
                border-radius: 6px;
            }
            QLabel#statusLabel {
                min-height: 28px;
                padding: 4px 8px;
                border-radius: 5px;
                background: #EEF4F7;
                color: #31505B;
            }
            QProgressBar {
                min-height: 20px;
                border: 1px solid #CAD4DD;
                border-radius: 5px;
                background: #F2F5F7;
                text-align: center;
                color: #263238;
            }
            QProgressBar::chunk {
                border-radius: 4px;
                background: #56A66D;
            }
        """)

    def setup_responsive_layout(self):
        self.mainHorizontalLayout.setStretch(0, 1)
        self.mainHorizontalLayout.setStretch(1, 2)
        self.mainHorizontalLayout.setSpacing(10)
        self.mainHorizontalLayout.setContentsMargins(12, 12, 12, 12)

        for group in [
            self.groupBox_ColorFeature, self.groupBox_ShapeFeature,
            self.groupBox_ManualFeature, self.groupBox_Prediction,
        ]:
            group.setMinimumWidth(330)
            group.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)

        for field in [
            self.lineEdit_H, self.lineEdit_S, self.lineEdit_V, self.lineEdit_DOCI,
            self.lineEdit_Area, self.lineEdit_Length, self.lineEdit_Width,
            self.lineEdit_Yield, self.lineEdit_Hweight, self.lineEdit_Vol,
            self.lineEdit_Tweight, self.lineEdit_N, self.lineEdit_Nue,
            self.folderPathLineEdit, self.imageComboBox,
        ]:
            field.setMinimumWidth(90)
            field.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)

        self.colorLabel.setMinimumSize(78, 78)
        self.colorLabel.setMaximumSize(110, 110)

        for image_label in (self.imageLabelLeft, self.imageLabelRight):
            image_label.setMinimumSize(180, 220)
            image_label.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        self.groupBox_ImageDisplay.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Expanding,
        )

    def setup_field_behavior(self):
        numeric_fields = [
            self.lineEdit_H, self.lineEdit_S, self.lineEdit_V, self.lineEdit_DOCI,
            self.lineEdit_Area, self.lineEdit_Length, self.lineEdit_Width,
            self.lineEdit_Yield, self.lineEdit_Hweight, self.lineEdit_Vol,
            self.lineEdit_Tweight,
        ]

        validator = QDoubleValidator(bottom=-999999.0, top=999999.0, decimals=6, parent=self)
        validator.setNotation(QDoubleValidator.Notation.StandardNotation)
        for field in numeric_fields:
            field.setValidator(validator)
            field.textChanged.connect(self.update_action_state)

        for field in [self.lineEdit_H, self.lineEdit_S, self.lineEdit_V]:
            field.textChanged.connect(self.update_hsv_preview)
            field.textEdited.connect(self.update_hsv_preview)

        for field in [
            self.lineEdit_H, self.lineEdit_S, self.lineEdit_V, self.lineEdit_DOCI,
            self.lineEdit_Area, self.lineEdit_Length, self.lineEdit_Width,
        ]:
            field.setPlaceholderText("自动提取，或手动输入")

        self.lineEdit_DOCI.setReadOnly(True)
        self.lineEdit_DOCI.setPlaceholderText("随 HSV 自动计算")
        self.lineEdit_N.setReadOnly(True)
        self.lineEdit_Nue.setReadOnly(True)
        self.lineEdit_N.setPlaceholderText("等待预测")
        self.lineEdit_Nue.setPlaceholderText("等待预测")
        self.folderPathLineEdit.setReadOnly(True)
        self.imageComboBox.setInsertPolicy(self.imageComboBox.InsertPolicy.NoInsert)

########################氮分等级读条############
    def setup_prediction_chart(self):
        self.nProgress = QProgressBar(self.groupBox_Prediction)
        self.nProgress.setObjectName("nProgress")
        self.nProgress.setRange(0, 100)
        self.nProgress.setValue(0)
        self.nProgress.setFormat("N含量 预测状态：等待预测")
        self.gridLayout_Prediction.addWidget(self.nProgress, 2, 0, 1, 2)

        self.nueProgress = QProgressBar(self.groupBox_Prediction)
        self.nueProgress.setObjectName("nueProgress")
        self.nueProgress.setRange(0, 100)
        self.nueProgress.setValue(0)
        self.nueProgress.setFormat("NUEg 预测状态：等待预测")
        self.gridLayout_Prediction.addWidget(self.nueProgress, 3, 0, 1, 2)

        self.groupBox_Prediction.setSizePolicy(
            QSizePolicy.Policy.Preferred,
            QSizePolicy.Policy.Fixed,
        )

    # =========================
    # 初始化线程
    # =========================
    def init_threads(self):
        # 图像线程
        self.image_thread = QThread()
        self.image_worker = ImageProcessWorker()
        self.image_worker.moveToThread(self.image_thread)

        self.start_image_process.connect(self.image_worker.process)
        self.image_worker.finished.connect(self.on_image_processed)

        self.image_thread.start()

        # 预测线程
        self.predict_thread = QThread()
        self.predict_worker = PredictWorker()
        self.predict_worker.moveToThread(self.predict_thread)

        self.start_predict.connect(self.predict_worker.predict)
        self.predict_worker.finished.connect(self.on_predict_finished)

        self.predict_thread.start()

    # =========================
    # 绑定按钮
    # =========================
    def bind_signals(self):
        self.selectFolderBtn.clicked.connect(self.select_folder)
        self.imageComboBox.currentIndexChanged.connect(self.on_combo_index_changed)
        self.loadImageBtn.clicked.connect(self.load_selected_image)
        line_edit = self.imageComboBox.lineEdit()
        if line_edit is not None:
            line_edit.textEdited.connect(self.filter_image_list)
            line_edit.returnPressed.connect(self.load_selected_image)

        self.extractColorBtn.clicked.connect(self.extract_color)
        self.predictBtn.clicked.connect(self.predict)
        self.exportExcelBtn.clicked.connect(self.export_excel)
        self.exportExcelBtn.setToolTip("左键：导出到已选 Excel\n右键:重新选择 Excel")
        self.exportExcelBtn.installEventFilter(self)

        # 容重勾选框和体积勾选框互斥
        self.checkBox_Vol.stateChanged.connect(self.on_Vol_checked)
        self.checkBox_Tweight.stateChanged.connect(self.on_Tweight_checked)

        self.lineEdit_Hweight.textChanged.connect(self.update_calculation)
        self.lineEdit_Tweight.textChanged.connect(self.update_calculation)
        self.lineEdit_Vol.textChanged.connect(self.update_calculation)

    def update_action_state(self):
        # Keep primary actions clickable. Each action validates its own prerequisites
        # and gives a clear message, which is friendlier while debugging and demoing.
        self.extractColorBtn.setEnabled(True)
        self.predictBtn.setEnabled(True)
        self.exportExcelBtn.setEnabled(True)

    def set_status(self, text):
        self.statusLabel.setText(f"状态：{text}")

    def clear_prediction_result(self):
        self.lineEdit_N.clear()
        self.lineEdit_Nue.clear()
        self.current_n_level = ""
        self.current_nue_level = ""
        self.nProgress.setValue(0)
        self.nProgress.setFormat("N含量 预测状态：等待预测")
        self.nueProgress.setValue(0)
        self.nueProgress.setFormat("NUEg 预测状态：等待预测")
        self.update_action_state()

    def clear_image_features(self):
        for field in [
            self.lineEdit_H, self.lineEdit_S, self.lineEdit_V, self.lineEdit_DOCI,
            self.lineEdit_Area, self.lineEdit_Length, self.lineEdit_Width,
        ]:
            field.clear()
        self.current_perimeter = None
        self.current_aspect_ratio = None
        self.current_circularity = None
        self.colorLabel.setStyleSheet(
            "background-color: white; border: 1px solid #AEBBC4; border-radius: 6px;"
        )
        self.colorLabel.setText("颜色")

    def update_hsv_preview(self, *_):
        h_text = self.lineEdit_H.text().strip()
        s_text = self.lineEdit_S.text().strip()
        v_text = self.lineEdit_V.text().strip()

        if not h_text or not s_text or not v_text:
            self.lineEdit_DOCI.clear()
            self.colorLabel.setStyleSheet(
                "background-color: white; border: 1px solid #AEBBC4; border-radius: 6px;"
            )
            self.colorLabel.setText("颜色")
            return

        try:
            h = float(h_text)
            s = float(s_text)
            v = float(v_text)
        except ValueError:
            return

        h = max(0.0, min(179.0, h))
        s = max(0.0, min(255.0, s))
        v = max(0.0, min(255.0, v))

        self.show_color(h, s, v)
        h_std = h * 2.0
        doci = (((60.0 - h_std) / 60.0) + (1.0 - s / 255.0) + (1.0 - v / 255.0)) / 3.0
        self.lineEdit_DOCI.setText(f"{doci:.6f}")

    def read_required_float(self, field, label):
        text = field.text().strip()
        if not text:
            raise ValueError(f"{label}不能为空")
        try:
            return float(text)
        except ValueError as exc:
            raise ValueError(f"{label}必须是数字") from exc

    # =========================
    # 体积、容重转换函数
    def on_Vol_checked(self):
        if self.checkBox_Vol.isChecked():
            # 取消容重换算
            self.checkBox_Tweight.blockSignals(True)
            self.checkBox_Tweight.setChecked(False)
            self.checkBox_Tweight.blockSignals(False)

        self.update_calculation()


    def on_Tweight_checked(self):
        if self.checkBox_Tweight.isChecked():
            # 取消体积换算
            self.checkBox_Vol.blockSignals(True)
            self.checkBox_Vol.setChecked(False)
            self.checkBox_Vol.blockSignals(False)

        self.update_calculation()

    def update_calculation(self):
        try:
            weight_text = self.lineEdit_Hweight.text()
            density_text = self.lineEdit_Tweight.text()
            volume_text = self.lineEdit_Vol.text()

            weight = float(weight_text) if weight_text else None
            density = float(density_text) if density_text else None
            volume = float(volume_text) if volume_text else None

            # ===== 体积换算 =====
            if self.checkBox_Vol.isChecked():
                if weight is not None and density not in (None, 0):
                    v = weight / density
                    self.lineEdit_Vol.blockSignals(True)
                    self.lineEdit_Vol.setText(f"{v:.4f}")
                    self.lineEdit_Vol.blockSignals(False)

            # ===== 容重换算 =====
            if self.checkBox_Tweight.isChecked():
                if weight is not None and volume not in (None, 0):
                    d = weight / volume
                    self.lineEdit_Tweight.blockSignals(True)
                    self.lineEdit_Tweight.setText(f"{d:.4f}")
                    self.lineEdit_Tweight.blockSignals(False)

        except ValueError:
            # 输入过程中内容不完整时忽略
            pass
        finally:
            self.update_action_state()



    # =========================
    # 选择文件夹
    # =========================
    def select_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "选择图片文件夹")

        if not folder:
            return

        self.folderPathLineEdit.setText(folder)
        self.load_images(folder)

    # 加载图片
    def load_images(self, folder):
        self.image_paths.clear()
        self.image_pairs = {}
        self.all_image_names = []

        exts = [".jpg", ".jpeg", ".png", ".bmp", ".tif"]
        pair_pattern = re.compile(r"^(.*)_(L|R)$", re.IGNORECASE)

        for f in os.listdir(folder):
            base, ext = os.path.splitext(f)
            if ext.lower() not in exts:
                continue

            full_path = os.path.join(folder, f)
            self.image_paths[f] = full_path
            self.all_image_names.append(f)

            match = pair_pattern.match(base)
            if match:
                pair_base = match.group(1)
                side = match.group(2).upper()
                self.image_pairs.setdefault(pair_base, {})[side] = full_path

        self.filter_image_list("")
        self.clear_current_image()

        if self.all_image_names:
            self.set_status(f"已读取 {len(self.all_image_names)} 张图片，请选择样本")
        else:
            self.set_status("当前文件夹没有可识别图片")
            QMessageBox.information(self, "提示", "当前文件夹没有 jpg、jpeg、png、bmp 或 tif 图片")
        self.update_action_state()

    def clear_current_image(self):
        self.current_image_path = None
        self.current_image_name = ""
        self._left_image_path = None
        self._right_image_path = None
        self.imageLabelLeft.clear()
        self.imageLabelRight.clear()
        self.imageLabelLeft.setText("左目相机")
        self.imageLabelRight.setText("右目相机")
        self.clear_prediction_result()

    # =========================
    # 提取颜色（触发线程）
    # =========================
    def filter_image_list(self, text):
        if self._updating_combo:
            return

        query = text.strip().lower()
        if query:
            matches = [name for name in self.all_image_names if query in name.lower()]
        else:
            matches = list(self.all_image_names)

        self._updating_combo = True
        try:
            self.imageComboBox.blockSignals(True)
            self.imageComboBox.clear()
            self.imageComboBox.addItems(matches)
            self.imageComboBox.setEditText(text)
            self.imageComboBox.blockSignals(False)
        finally:
            self._updating_combo = False

    def on_combo_index_changed(self, *_):
        if self._updating_combo:
            return
        self.load_selected_image()

    def load_selected_image(self):
        text = self.imageComboBox.currentText().strip()
        if not text:
            return

        chosen_name = None
        text_lower = text.lower()

        if text in self.image_paths:
            chosen_name = text
        else:
            exact_matches = [name for name in self.all_image_names if name.lower() == text_lower]
            if exact_matches:
                chosen_name = exact_matches[0]
            else:
                fuzzy_matches = [name for name in self.all_image_names if text_lower in name.lower()]
                if len(fuzzy_matches) == 1:
                    chosen_name = fuzzy_matches[0]
                elif len(fuzzy_matches) > 1:
                    QMessageBox.information(
                        self,
                        "提示",
                        "匹配到多个文件，请从下拉列表中选择完整文件名：\n" +
                        "\n".join(fuzzy_matches[:10])
                    )
                    return
                else:
                    return

        base, _ = os.path.splitext(chosen_name)
        pair_match = re.match(r"^(.*)_(L|R)$", base, re.IGNORECASE)

        left_path = None
        right_path = None

        if pair_match:
            pair_base = pair_match.group(1)
            pair_info = self.image_pairs.get(pair_base, {})
            left_path = pair_info.get("L")
            right_path = pair_info.get("R")
            self.current_image_name = pair_base
        else:
            left_path = self.image_paths.get(chosen_name)
            self.current_image_name = os.path.splitext(chosen_name)[0]

        if not left_path and not right_path:
            return

        self.current_image_path = left_path or right_path
        self._left_image_path = left_path
        self._right_image_path = right_path
        self.clear_image_features()
        self.clear_prediction_result()

        if left_path and right_path:
            self.set_status(f"已加载 {self.current_image_name} 左右图")
        elif left_path:
            self.set_status(f"已加载 {self.current_image_name} 左图")
        else:
            self.set_status(f"已加载 {self.current_image_name} 右图")

        self.refresh_image_views()
        self.update_action_state()

    def refresh_image_views(self):
        self.set_image_to_label(self.imageLabelLeft, self._left_image_path, "左目相机")
        self.set_image_to_label(self.imageLabelRight, self._right_image_path, "右目相机")

    def set_image_to_label(self, label, image_path, empty_text):
        label.setScaledContents(False)
        if not image_path:
            label.clear()
            label.setText(empty_text)
            return

        pixmap = QPixmap(image_path)
        if pixmap.isNull():
            label.clear()
            label.setText("图片读取失败")
            return

        scaled = pixmap.scaled(
            label.size(),
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation,
        )
        label.setPixmap(scaled)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        if self._left_image_path or self._right_image_path:
            self.refresh_image_views()

    def extract_color(self):
        if not self.current_image_path:
            QMessageBox.warning(self, "提示", "请先选择图片")
            return

        self.extractColorBtn.setEnabled(False)
        self.predictBtn.setEnabled(False)
        self.set_status("正在提取图像特征")
        image_input = {
            "name": self.current_image_name or Path(self.current_image_path).stem,
            "L": self._left_image_path,
            "R": self._right_image_path,
        }
        self.start_image_process.emit(image_input)

    # =========================
    # 图像处理结果回调
    # =========================
    def on_image_processed(self, result):
        error = result.get("error")
        if error:
            self.set_status("图像特征提取失败")
            QMessageBox.critical(self, "图像处理失败", str(error))
            self.update_action_state()
            return

        self.lineEdit_H.setText(str(result.get("H", "")))
        self.lineEdit_S.setText(str(result.get("S", "")))
        self.lineEdit_V.setText(str(result.get("V", "")))

        self.lineEdit_Area.setText(str(result.get("area", "")))
        self.current_perimeter = result.get("perimeter", "")
        self.current_aspect_ratio = result.get("aspect_ratio", "")
        self.current_circularity = result.get("circularity", "")
        self.current_output_time = result.get("output_time", "")
        self.lineEdit_Length.setText(str(result.get("length", "")))
        self.lineEdit_Width.setText(str(result.get("width", "")))

        # HSV 改动会自动刷新色块和 DOCI
        self.update_hsv_preview()
        self.set_status("图像特征提取完成，可进行模型预测")
        self.update_action_state()

    # =========================
    # 预测（触发线程）
    # =========================
    def predict(self):
        if not self.current_image_path:
            QMessageBox.information(self, "提示", "还没有导入图片。你也可以先手动填写全部特征后再预测。")

        try:
            features = {
                "H": self.read_required_float(self.lineEdit_H, "色度 H"),
                "S": self.read_required_float(self.lineEdit_S, "饱和度 S"),
                "V": self.read_required_float(self.lineEdit_V, "明度 V"),
                "DOCI": self.read_required_float(self.lineEdit_DOCI, "DOCI"),

                "area": self.read_required_float(self.lineEdit_Area, "面积"),
                "length": self.read_required_float(self.lineEdit_Length, "长度"),
                "width": self.read_required_float(self.lineEdit_Width, "宽度"),

            # ===== 产量与考种数据 =====
                "Yield": self.read_required_float(self.lineEdit_Yield, "单株产量"),
                "Hweight": self.read_required_float(self.lineEdit_Hweight, "百粒重"),
                "Vol": self.read_required_float(self.lineEdit_Vol, "百粒体积"),
                "Tweight": self.read_required_float(self.lineEdit_Tweight, "容重")
            }
        except ValueError as e:
            QMessageBox.warning(self, "输入错误", str(e))
            return

        self.clear_prediction_result()
        self.predictBtn.setEnabled(False)
        self.set_status("模型正在预测")
        self.start_predict.emit(features)

    # =========================
    # 预测结果回调
    # =========================
    def on_predict_finished(self, result):
        n_value = result.get("N", "")
        nue_value = result.get("NUE", "")

        if n_value == "error":
            self.lineEdit_N.setText("")
            self.lineEdit_Nue.setText("")
            self.set_status("预测失败")
            QMessageBox.critical(self, "预测失败", str(nue_value))
            self.update_action_state()
            return

        self.lineEdit_N.setText(str(n_value))
        self.lineEdit_Nue.setText(str(nue_value))
        self.update_prediction_chart(n_value, nue_value)
        self.set_status("预测完成，可导出 Excel")
        self.update_action_state()

    def get_n_level(self, n_value):
        n_float = float(n_value)
        if n_float < 1.45:
            return "极低"
        if n_float < 1.57:
            return "低"
        if n_float < 1.69:
            return "中"
        if n_float < 1.81:
            return "高"
        return "极高"

    def get_nue_level(self, nue_value):
        nue_float = float(nue_value)
        if nue_float < 12.46:
            return "极低"
        if nue_float < 17.40:
            return "低"
        if nue_float < 22.33:
            return "中"
        if nue_float < 27.27:
            return "高"
        return "极高"

    def update_prediction_chart(self, n_value, nue_value):
        try:
            n_float = float(n_value)
            nue_float = float(nue_value)
        except (TypeError, ValueError):
            return

        self.current_n_level = self.get_n_level(n_float)
        self.current_nue_level = self.get_nue_level(nue_float)

        # 读条按指定满格值线性映射：N=3，NUEg=50
        n_overflow = n_float > 3.0
        nue_overflow = nue_float > 50.0
        n_percent = max(0, min(100, int((n_float / 3.0) * 100)))
        nue_percent = max(0, min(100, int((nue_float / 50.0) * 100)))

        self.nProgress.setValue(n_percent)
        self.nProgress.setFormat(f"N含量 预测值：{n_float:.4f}%({self.current_n_level})")
        self.nueProgress.setValue(nue_percent)
        self.nueProgress.setFormat(f"NUEg 预测值：{nue_float:.4f}({self.current_nue_level})")

        if n_overflow or nue_overflow:
            parts = []
            if n_overflow:
                parts.append(f"N含量 超出读条上限 3.0,当前值 {n_float:.4f}")
            if nue_overflow:
                parts.append(f"NUEg 超出读条上限 50.0,当前值 {nue_float:.4f}")
            warning_text = ":".join(parts)
            logging.warning(warning_text)
            self.set_status(warning_text)

    # =========================
    # 颜色显示
    # =========================
    def show_color(self, h, s, v):
        h_qt = max(0, min(359, int(float(h) * 2)))
        s_qt = max(0, min(255, int(float(s))))
        v_qt = max(0, min(255, int(float(v))))

        color = QColor.fromHsv(h_qt, s_qt, v_qt)

        self.colorLabel.clear()
        self.colorLabel.setStyleSheet(
            f"background-color: {color.name()}; border: 1px solid #5B6B73; border-radius: 6px;"
        )

    def eventFilter(self, obj, event):
        if obj == self.exportExcelBtn and event.type() == QEvent.Type.MouseButtonPress:
            if event.button() == Qt.MouseButton.RightButton:
                if self.select_excel_file():
                    self.export_excel()
                return True

        return super().eventFilter(obj, event)

    # =========================
    # 选择/切换 Excel 文件
    # =========================
    def select_excel_file(self, show_message=True):
        default_name = f"导出结果_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        initial_path = self.excel_file_path or default_name
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "选择 Excel 表格",
            initial_path,
            "Excel 文件 (*.xlsx)",
            options=QFileDialog.Option.DontConfirmOverwrite
        )

        if not file_path:
            return False

        if not file_path.lower().endswith(".xlsx"):
            file_path += ".xlsx"

        if Path(file_path).exists():
            reply = QMessageBox.question(
                self,
                "文件已存在",
                f"文件已存在：\n{file_path}\n\n是否添加到该文件？",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.Yes
            )
            if reply != QMessageBox.StandardButton.Yes:
                return False

        self.excel_file_path = file_path
        self.set_status("Excel 导出目标已选择")
        if show_message:
            if Path(file_path).exists():
                QMessageBox.information(self, "Excel 已选择", f"当前导出目标将追加到：\n{file_path}")
            else:
                QMessageBox.information(self, "Excel 已选择", f"当前导出目标已设置为：\n{file_path}")
        return True

    def get_excel_headers(self):
        return [
            "图片名",
            "H",
            "S",
            "V",
            "DOCI",
            "面积(mm²)",
            "周长(mm)",
            "长宽比",
            "圆形度",
            "长度(mm)",
            "宽度(mm)",
            "产量(g/株)",
            "百粒重(g)",
            "体积(ml)",
            "容重(g/ml)",
            "N(%)",
            "N等级",
            "NUE",
            "NUE等级",
            "输出时间"
        ]

    def get_excel_row(self):
        return [
            self.current_image_name or (os.path.splitext(os.path.basename(self.current_image_path))[0] if self.current_image_path else ""),
            self.lineEdit_H.text().strip(),
            self.lineEdit_S.text().strip(),
            self.lineEdit_V.text().strip(),
            self.lineEdit_DOCI.text().strip(),
            self.lineEdit_Area.text().strip(),
            "" if self.current_perimeter is None else str(self.current_perimeter),
            "" if self.current_aspect_ratio is None else str(self.current_aspect_ratio),
            "" if self.current_circularity is None else str(self.current_circularity),
            self.lineEdit_Length.text().strip(),
            self.lineEdit_Width.text().strip(),
            self.lineEdit_Yield.text().strip(),
            self.lineEdit_Hweight.text().strip(),
            self.lineEdit_Vol.text().strip(),
            self.lineEdit_Tweight.text().strip(),
            self.lineEdit_N.text().strip(),
            getattr(self, "current_n_level", ""),
            self.lineEdit_Nue.text().strip(),
            getattr(self, "current_nue_level", ""),
            "" if self.current_output_time is None else str(self.current_output_time)
        ]

    # =========================
    # 导出 Excel
    # =========================
    def export_excel(self):
        file_path = self.excel_file_path
        if not file_path:
            if not self.select_excel_file(show_message=False):
                return
            file_path = self.excel_file_path

        if not file_path:
            return

        self.current_output_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        headers = self.get_excel_headers()
        row = self.get_excel_row()

        try:
            path_obj = Path(file_path)
            if path_obj.exists():
                wb = load_workbook(file_path)
                ws = wb.active
                if ws is None:
                    raise RuntimeError("无法获取 Excel 工作表")
                if ws.max_row == 0 or ws["A1"].value is None:
                    ws.append(headers)
            else:
                wb = Workbook()
                ws = wb.active
                if ws is None:
                    raise RuntimeError("无法创建 Excel 工作表")
                ws.title = "导出数据"
                ws.append(headers)

            ws.append(row)
            wb.save(file_path)
        except Exception as e:
            QMessageBox.critical(self, "导出失败", f"保存 Excel 时出错：\n{e}")
            return

        if self.lineEdit_N.text().strip() or self.lineEdit_Nue.text().strip():
            self.set_status("导出成功")
        else:
            self.set_status("导出成功（未包含预测结果）")
        QMessageBox.information(self, "导出成功", f"已保存到：\n{file_path}")

    def closeEvent(self, event):
        # 关闭窗口前先退出并等待工作线程，避免 QThread 仍在运行时被销毁
        for thread in (getattr(self, "image_thread", None), getattr(self, "predict_thread", None)):
            if thread is not None and thread.isRunning():
                thread.quit()
                thread.wait()
        super().closeEvent(event)






if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MyWindow()
    window.show()
    sys.exit(app.exec())

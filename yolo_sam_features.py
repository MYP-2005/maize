import os
import sys
import math
import gc
import logging
from datetime import datetime
from pathlib import Path

APP_DIR = Path(sys.executable).resolve().parent if getattr(sys, "frozen", False) else Path(__file__).resolve().parent
BASE_DIR = Path(getattr(sys, "_MEIPASS", APP_DIR))
LOG_DIR = APP_DIR / "logs"
LOG_DIR.mkdir(parents=True, exist_ok=True)
logging.basicConfig(
    filename=LOG_DIR / "app.log",
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)

_config_root = APP_DIR / ".ultralytics"
_config_root.mkdir(parents=True, exist_ok=True)
os.environ.setdefault("YOLO_CONFIG_DIR", str(_config_root))

import cv2
import numpy as np
import onnxruntime as ort
import pandas as pd
from ultralytics import SETTINGS, YOLO
from ultralytics.utils.events import events

try:
    SETTINGS["sync"] = False
    events.enabled = False
except Exception:
    logger.exception("Failed to disable Ultralytics analytics events")

try:
    import torch

    torch.set_num_threads(1)
    torch.set_num_interop_threads(1)
except Exception:
    logger.exception("Failed to limit torch threads")
YOLO_MODEL_PATH = BASE_DIR / "best.pt"
SAM_ENCODER_PATH = BASE_DIR / "sam2.1_hiera_tiny.encoder.onnx"
SAM_DECODER_PATH = BASE_DIR / "sam2.1_hiera_tiny.decoder.onnx"
DEFAULT_MM_PER_PIXEL = 0.1159
DEFAULT_TARGET_OBJECTS = 100
TRAINING_LENGTH_SCALE = 10.0
DETAIL_COLUMNS = [
    "name",
    "side",
    "object_index",
    "confidence",
    "area",
    "length",
    "width",
    "perimeter",
    "aspect_ratio",
    "circularity",
    "H_mean",
    "H_std",
    "H_skew",
    "H_kurt",
    "S_mean",
    "S_std",
    "S_skew",
    "S_kurt",
    "V_mean",
    "V_std",
    "V_skew",
    "V_kurt",
    "DOCI",
]


def _safe_std(values):
    if len(values) < 2:
        return 0.0
    return float(np.std(values, ddof=1))


def _safe_skew(values):
    if len(values) < 3:
        return 0.0
    mean = np.mean(values)
    std = np.std(values, ddof=0)
    if std == 0:
        return 0.0
    return float(np.mean(((values - mean) / std) ** 3))


def _safe_kurt(values):
    if len(values) < 4:
        return 0.0
    mean = np.mean(values)
    std = np.std(values, ddof=0)
    if std == 0:
        return 0.0
    return float(np.mean(((values - mean) / std) ** 4))


def _side_from_path(path):
    stem = Path(path).stem
    if stem.upper().endswith("_L"):
        return "L"
    if stem.upper().endswith("_R"):
        return "R"
    return ""


def _base_name_from_path(path):
    stem = Path(path).stem
    if stem.upper().endswith(("_L", "_R")):
        return stem[:-2]
    return stem


class SAM2Predictor:
    def __init__(self, encoder_path, decoder_path, device="cpu"):
        available = set(ort.get_available_providers())
        if device == "cuda" and "CUDAExecutionProvider" in available:
            providers = ["CUDAExecutionProvider", "CPUExecutionProvider"]
        else:
            providers = ["CPUExecutionProvider"]

        session_options = ort.SessionOptions()
        session_options.intra_op_num_threads = 1
        session_options.inter_op_num_threads = 1
        self.encoder_session = ort.InferenceSession(str(encoder_path), sess_options=session_options, providers=providers)
        self.decoder_session = ort.InferenceSession(str(decoder_path), sess_options=session_options, providers=providers)
        self.input_size = 1024
        self.orig_size = None
        self.features = None

    def clear_features(self):
        self.features = None
        self.orig_size = None

    def preprocess(self, image_rgb):
        self.orig_size = image_rgb.shape[:2]
        img_resized = cv2.resize(image_rgb, (self.input_size, self.input_size))
        mean = np.array([0.485, 0.456, 0.406])
        std = np.array([0.229, 0.224, 0.225])
        img_float = img_resized.astype(np.float32) / 255.0
        img_norm = (img_float - mean) / std
        return img_norm.transpose(2, 0, 1)[None, :, :, :].astype(np.float32)

    def run_encoder(self, image_rgb):
        img_input = self.preprocess(image_rgb)
        input_name = self.encoder_session.get_inputs()[0].name
        outputs = self.encoder_session.run(None, {input_name: img_input})

        features = {}
        for output in outputs:
            if len(output.shape) < 4:
                continue
            channels = output.shape[1]
            if channels == 256:
                features["image_embeddings"] = output
            elif channels == 32:
                features["high_res_feats_0"] = output
            elif channels == 64:
                features["high_res_feats_1"] = output

        missing = {"image_embeddings", "high_res_feats_0", "high_res_feats_1"} - set(features)
        if missing:
            raise RuntimeError(f"SAM encoder output missing: {', '.join(sorted(missing))}")
        self.features = features

    def run_decoder(self, box, threshold=0.0):
        if self.features is None:
            raise RuntimeError("SAM encoder must run before decoder.")

        h, w = self.orig_size
        scale_x = self.input_size / w
        scale_y = self.input_size / h
        box_1024 = np.array(
            [box[0] * scale_x, box[1] * scale_y, box[2] * scale_x, box[3] * scale_y],
            dtype=np.float32,
        )

        decoder_inputs = {
            "image_embed": self.features["image_embeddings"],
            "high_res_feats_0": self.features["high_res_feats_0"],
            "high_res_feats_1": self.features["high_res_feats_1"],
            "point_coords": box_1024.reshape(1, 2, 2),
            "point_labels": np.array([[2, 3]], dtype=np.float32),
            "mask_input": np.zeros((1, 1, 256, 256), dtype=np.float32),
            "has_mask_input": np.zeros((1,), dtype=np.float32),
        }
        needed = {i.name for i in self.decoder_session.get_inputs()}
        decoder_inputs = {k: v for k, v in decoder_inputs.items() if k in needed}

        outputs = self.decoder_session.run(None, decoder_inputs)
        masks = outputs[0]
        iou_pred = outputs[1]
        best_mask_idx = int(np.argmax(iou_pred[0, 0]))
        mask_low_res = masks[0, best_mask_idx, :, :]
        mask_final = cv2.resize(mask_low_res, (w, h), interpolation=cv2.INTER_LINEAR)
        return (mask_final > threshold).astype(np.uint8) * 255


class SeedPhenotypingEngine:
    def __init__(self, mm_per_pixel=None):
        self.morph_kernel_open = 3
        self.morph_kernel_close = 7
        self.min_area = 50
        self.mm_per_pixel = mm_per_pixel
        self.color_erosion_iters = 2

    def run(self, img_bgr, raw_mask, cls_id, mm_per_pixel=None):
        scale = mm_per_pixel if mm_per_pixel is not None else self.mm_per_pixel
        geo_mask = self._post_process(raw_mask)
        geo_feats = self._calculate_geometry(geo_mask, cls_id, scale=scale)
        if geo_feats is None:
            return None
        geo_feats.update(self._calculate_color_features(img_bgr, geo_mask))
        return geo_feats

    def _post_process(self, mask):
        if mask is None:
            return np.zeros((10, 10), dtype=np.uint8)
        mask = np.ascontiguousarray(np.asarray(mask, dtype=np.uint8))
        if mask.size and mask.max() == 1:
            mask = mask * 255
        k1 = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (self.morph_kernel_open, self.morph_kernel_open))
        mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, k1)
        k2 = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (self.morph_kernel_close, self.morph_kernel_close))
        return cv2.morphologyEx(mask, cv2.MORPH_CLOSE, k2)

    def _calculate_geometry(self, mask, cls_id, scale=None):
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        if not contours:
            return None
        cnt = max(contours, key=cv2.contourArea)
        area = cv2.contourArea(cnt)
        if area < self.min_area:
            return None
        result = self._find_farthest_points_convex(cnt)
        if result is None:
            return None
        (p1, p2), _ = result
        rect = self._get_rect_aligned_to_axis(cnt, p1, p2)
        if rect is None:
            return None
        perimeter = cv2.arcLength(cnt, True)
        features = {
            "class_id": cls_id,
            "area": area,
            "perimeter": perimeter,
            "length": rect["length"],
            "width": rect["width"],
            "aspect_ratio": rect["length"] / rect["width"] if rect["width"] > 0 else 0,
            "circularity": (4 * np.pi * area) / (perimeter**2) if perimeter > 0 else 0,
        }
        if scale is not None and scale > 0:
            features.update(
                {
                    "length_mm": features["length"] * scale,
                    "width_mm": features["width"] * scale,
                    "perimeter_mm": perimeter * scale,
                    "area_mm2": area * (scale**2),
                }
            )
        return features

    def _calculate_color_features(self, img_bgr, geo_mask):
        mask_for_color = geo_mask.copy()
        if self.color_erosion_iters > 0:
            kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
            mask_for_color = cv2.erode(mask_for_color, kernel, iterations=self.color_erosion_iters)
        if np.sum(mask_for_color) == 0:
            mask_for_color = geo_mask

        pixels_bgr = img_bgr[mask_for_color > 0]
        if len(pixels_bgr) == 0:
            return {}

        mean_b, mean_g, mean_r = np.mean(pixels_bgr, axis=0)
        img_hsv = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2HSV)
        pixels_hsv = img_hsv[mask_for_color > 0]
        h_vals = pixels_hsv[:, 0].astype(np.float64)
        s_vals = pixels_hsv[:, 1].astype(np.float64)
        v_vals = pixels_hsv[:, 2].astype(np.float64)
        mean_h, mean_s, mean_v = np.mean(pixels_hsv, axis=0)
        s_norm = mean_s / 255.0
        v_norm = mean_v / 255.0
        mean_h_std = mean_h * 2.0
        doci = (((60.0 - mean_h_std) / 60.0) + (1.0 - s_norm) + (1.0 - v_norm)) / 3.0

        total_rgb = mean_r + mean_g + mean_b + 1e-6
        r_norm = mean_r / total_rgb
        g_norm = mean_g / total_rgb
        b_norm = mean_b / total_rgb
        exg = 2 * g_norm - r_norm - b_norm
        exr = 1.4 * r_norm - g_norm

        return {
            "mean_hue": float(mean_h),
            "mean_sat": float(mean_s),
            "mean_val": float(mean_v),
            "mean_r": float(mean_r),
            "mean_g": float(mean_g),
            "mean_b": float(mean_b),
            "H_mean": float(mean_h),
            "H_std": _safe_std(h_vals),
            "H_skew": _safe_skew(h_vals),
            "H_kurt": _safe_kurt(h_vals),
            "S_mean": float(mean_s),
            "S_std": _safe_std(s_vals),
            "S_skew": _safe_skew(s_vals),
            "S_kurt": _safe_kurt(s_vals),
            "V_mean": float(mean_v),
            "V_std": _safe_std(v_vals),
            "V_skew": _safe_skew(v_vals),
            "V_kurt": _safe_kurt(v_vals),
            "ExG": float(exg),
            "ExR": float(exr),
            "DOCI": float(doci),
        }

    def _find_farthest_points_convex(self, contour):
        try:
            hull = cv2.convexHull(contour).reshape(-1, 2)
        except Exception:
            return None
        if len(hull) < 2:
            return None
        max_d, pts = 0, None
        for i in range(len(hull)):
            for j in range(i + 1, len(hull)):
                d = np.linalg.norm(hull[i] - hull[j])
                if d > max_d:
                    max_d, pts = d, (hull[i], hull[j])
        return pts, max_d

    def _get_rect_aligned_to_axis(self, contour, p1, p2):
        dx, dy = p2[0] - p1[0], p2[1] - p1[1]
        if dx == 0 and dy == 0:
            return None
        angle = math.degrees(math.atan2(dy, dx))
        moments = cv2.moments(contour)
        if moments["m00"] == 0:
            return None
        center = (moments["m10"] / moments["m00"], moments["m01"] / moments["m00"])
        m_rot = cv2.getRotationMatrix2D(center, angle, 1.0)
        rotated_cnt = cv2.transform(contour.astype(np.float32), m_rot)
        xs, ys = rotated_cnt[:, 0, 0], rotated_cnt[:, 0, 1]
        return {"length": float(xs.max() - xs.min()), "width": float(ys.max() - ys.min())}


class AutoLabelPipeline:
    def __init__(
        self,
        yolo_path=YOLO_MODEL_PATH,
        sam_enc=SAM_ENCODER_PATH,
        sam_dec=SAM_DECODER_PATH,
        sam_thresh=3.0,
        conf=0.4,
        device="cpu",
        mm_per_pixel=DEFAULT_MM_PER_PIXEL,
        target_objects=DEFAULT_TARGET_OBJECTS,
    ):
        for path in (yolo_path, sam_enc, sam_dec):
            if not Path(path).exists():
                raise FileNotFoundError(f"Model file not found: {path}")
        self.device = device
        self.sam_thresh = sam_thresh
        self.conf = conf
        self.target_objects = target_objects
        self.yolo = YOLO(str(yolo_path))
        self.sam2 = SAM2Predictor(sam_enc, sam_dec, device=device)
        self.engine = SeedPhenotypingEngine(mm_per_pixel=mm_per_pixel)

    def close(self):
        self.sam2.clear_features()
        self.yolo = None
        self.sam2 = None
        self.engine = None
        try:
            import torch

            if torch.cuda.is_available():
                torch.cuda.empty_cache()
        except Exception:
            logger.exception("Failed to clear torch cache")
        gc.collect()

    def process_single_image(self, image_path):
        logger.info("Process single image start: %s", image_path)
        img_bgr = None
        img_rgb = None
        results = None
        try:
            img_bgr = cv2.imdecode(np.fromfile(str(image_path), dtype=np.uint8), cv2.IMREAD_COLOR)
            if img_bgr is None:
                raise ValueError(f"Cannot read image: {image_path}")

            img_rgb = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB)
            self.sam2.run_encoder(img_rgb)
            yolo_device = 0 if self.device == "cuda" else "cpu"
            logger.info("YOLO predict start: %s", image_path)
            results = self.yolo.predict(img_bgr, conf=self.conf, verbose=False, device=yolo_device)
            logger.info("YOLO predict done: %s", image_path)

            features_list = []
            if len(results[0].boxes) == 0:
                return features_list

            boxes = results[0].boxes.xyxy.cpu().numpy()
            cls_ids = results[0].boxes.cls.cpu().numpy().astype(int)
            confs = results[0].boxes.conf.cpu().numpy()
            order = np.argsort(confs)[::-1]

            side = _side_from_path(image_path)
            base_name = _base_name_from_path(image_path)
            for rank, i in enumerate(order):
                box = boxes[i]
                raw_mask = self.sam2.run_decoder(box, threshold=self.sam_thresh)
                feats = self.engine.run(img_bgr, raw_mask, int(cls_ids[i]))
                if feats:
                    feats["name"] = f"{base_name}_{side}_{rank}" if side else f"{base_name}_{rank}"
                    feats["side"] = side
                    feats["object_index"] = int(rank)
                    feats["confidence"] = float(confs[i])
                    features_list.append(feats)
            logger.info("Process single image done: %s, objects=%s", image_path, len(features_list))
            return features_list
        finally:
            self.sam2.clear_features()
            del img_bgr, img_rgb, results
            gc.collect()


_PIPELINE = None


def get_pipeline():
    global _PIPELINE
    if _PIPELINE is None:
        _PIPELINE = AutoLabelPipeline()
    return _PIPELINE


def reset_pipeline():
    global _PIPELINE
    if _PIPELINE is not None:
        try:
            _PIPELINE.close()
        finally:
            _PIPELINE = None

#########################################除杂程序筛选阈值#####################
def filter_seed_dataframe(df, target_objects=DEFAULT_TARGET_OBJECTS):
    if df.empty:
        return df.copy()

    required = ["length", "width", "area", "H_skew", "H_kurt", "S_skew", "S_kurt", "V_skew", "V_kurt"]
    missing = [col for col in required if col not in df.columns]
    if missing:
        raise RuntimeError(f"筛选缺少字段: {', '.join(missing)}")

    filtered = df[(df["length"] >= 40) & (df["width"] >= 40)].copy()
    filtered = filtered[
        (filtered["H_skew"] < 10)
        & (filtered["H_kurt"] < 30)
        & (filtered["S_skew"] < 3)
        & (filtered["S_kurt"] < 10)
        & (filtered["V_skew"] < 3)
        & (filtered["V_kurt"] < 10)
    ].copy()

    if target_objects is None or filtered.empty:
        return filtered

    if "side" in filtered.columns and filtered["side"].astype(str).str.len().any():
        parts = []
        for _, side_df in filtered.groupby("side", dropna=False):
            parts.append(side_df.sort_values("confidence", ascending=False).head(target_objects))
        return pd.concat(parts, ignore_index=True) if parts else filtered
    return filtered.sort_values("confidence", ascending=False).head(target_objects)

########################################################################################
def aggregate_filtered_features(df_filtered, objects_before=0):
    if df_filtered.empty:
        raise RuntimeError("筛选后没有剩余种子，请检查图片质量或筛选阈值。")

    def mean_col(col, fallback=None):
        name = col if col in df_filtered.columns else fallback
        if name is None or name not in df_filtered.columns:
            return 0.0
        return float(df_filtered[name].mean())

    base_area = mean_col("area_mm2", "area")
    base_length = mean_col("length_mm", "length")
    base_width = mean_col("width_mm", "width")
    base_perimeter = mean_col("perimeter_mm", "perimeter")
    base_aspect_ratio = mean_col("aspect_ratio")
    base_circularity = mean_col("circularity")
    result = {
        "area": round(base_area, 4),
        "length": round(base_length, 4),
        "width": round(base_width, 4),
        "perimeter": round(base_perimeter, 4),
        "aspect_ratio": round(base_aspect_ratio, 6),
        "circularity": round(base_circularity, 6),
        "objects_before_filter": int(objects_before),
        "objects": int(len(df_filtered)),
    }

    for ui_key, col in (("H", "H_mean"), ("S", "S_mean"), ("V", "V_mean"), ("DOCI", "DOCI")):
        side_means = []
        if "side" in df_filtered.columns and df_filtered["side"].astype(str).str.len().any():
            groups = df_filtered.groupby("side", dropna=False)
        else:
            groups = [(None, df_filtered)]

        for _, side_df in groups:
            values = side_df[col].dropna()
            if values.empty:
                continue
            lower = values.quantile(0.05)
            upper = values.quantile(0.95)
            clean = values[(values >= lower) & (values <= upper)]
            if not clean.empty:
                side_means.append(float(clean.mean()))

        result[ui_key] = round(float(np.mean(side_means)), 6 if ui_key == "DOCI" else 4) if side_means else 0.0

    return result


def save_seed_tables(df_all, df_filtered, sample_name):
    output_dir = APP_DIR / "analysis_results"
    output_dir.mkdir(parents=True, exist_ok=True)
    safe_name = "".join(ch if ch not in r'\/:*?"<>|' else "_" for ch in sample_name)
    output_path = output_dir / f"{safe_name}_seed_details.xlsx"
    with pd.ExcelWriter(output_path) as writer:
        df_all.to_excel(writer, sheet_name="all_detected", index=False)
        df_filtered.to_excel(writer, sheet_name="filtered_for_summary", index=False)
    return output_path


def _normalize_image_paths(image_input):
    if isinstance(image_input, dict):
        paths = [image_input.get("L"), image_input.get("R"), image_input.get("left"), image_input.get("right")]
        return [Path(p) for p in paths if p]
    if isinstance(image_input, (list, tuple, set)):
        return [Path(p) for p in image_input if p]
    return [Path(image_input)]


def extract_features(image_input, sample_name=None, save_tables=True):
    logger.info("Extract features start: sample=%s, input=%s", sample_name, image_input)
    paths = _normalize_image_paths(image_input)
    features_list = []
    pipeline = get_pipeline()
    for path in paths:
        features_list.extend(pipeline.process_single_image(path))

    if not features_list:
        raise RuntimeError("未检测到可分析的目标，请换一张图片或降低 YOLO 置信度。")

    df_all = pd.DataFrame(features_list)
    ordered_cols = [col for col in DETAIL_COLUMNS if col in df_all.columns]
    ordered_cols += [col for col in df_all.columns if col not in ordered_cols]
    df_all = df_all[ordered_cols]
    df_filtered = filter_seed_dataframe(df_all, target_objects=pipeline.target_objects)
    summary = aggregate_filtered_features(df_filtered, objects_before=len(df_all))

    if save_tables:
        if sample_name is None:
            sample_name = _base_name_from_path(paths[0])
        summary["detail_file"] = str(save_seed_tables(df_all, df_filtered, sample_name))

    summary["output_time"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    logger.info("Extract features done: sample=%s, summary=%s", sample_name, summary)
    gc.collect()
    return summary

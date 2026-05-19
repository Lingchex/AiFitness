import os

import cv2
import mediapipe as mp
import numpy as np
import json
import base64
from openai import OpenAI

# ================= 配置区 =================
DASHSCOPE_API_KEY = "OSvY3iEjTdYcXqHU930a632f32E4483e827723E64819C158"
VIDEO_PATH = "./data/健身训练素材/健身训练素材/倒蹬.mp4"
EXERCISE_TYPE = "自动识别"
MAX_FRAMES = 8              # 最多提取的关键帧数
FRAME_STRATEGY = "uniform"  # "uniform"=均匀抽帧, "adaptive"=基于姿态变化量自适应抽帧
OUTPUT_DIR = "./output_keyframes"
# ==========================================

mp_pose = mp.solutions.pose

client = OpenAI(
    api_key=DASHSCOPE_API_KEY,
    base_url="https://ai-api-prod.qingjiao.art/v1"
)

# ===== MediaPipe Pose 33个关键点索引常量 =====
# 完整骨架连接参考: https://developers.google.com/mediapipe/solutions/vision/pose_landmarker
NOSE = 0
LEFT_EYE_INNER, LEFT_EYE, LEFT_EYE_OUTER = 1, 2, 3
RIGHT_EYE_INNER, RIGHT_EYE, RIGHT_EYE_OUTER = 4, 5, 6
LEFT_EAR, RIGHT_EAR = 7, 8
MOUTH_LEFT, MOUTH_RIGHT = 9, 10
LEFT_SHOULDER, RIGHT_SHOULDER = 11, 12
LEFT_ELBOW, RIGHT_ELBOW = 13, 14
LEFT_WRIST, RIGHT_WRIST = 15, 16
LEFT_PINKY, RIGHT_PINKY = 17, 18
LEFT_INDEX, RIGHT_INDEX = 19, 20
LEFT_THUMB, RIGHT_THUMB = 21, 22
LEFT_HIP, RIGHT_HIP = 23, 24
LEFT_KNEE, RIGHT_KNEE = 25, 26
LEFT_ANKLE, RIGHT_ANKLE = 27, 28
LEFT_HEEL, RIGHT_HEEL = 29, 30
LEFT_FOOT_INDEX, RIGHT_FOOT_INDEX = 31, 32

# ===== 通用关节角度定义：每个元组 (点A, 顶点B, 点C, 中文名) =====
JOINT_ANGLES = [
    # --- 上肢 ---
    (LEFT_SHOULDER, LEFT_ELBOW, LEFT_WRIST,  "左肘角度"),
    (RIGHT_SHOULDER, RIGHT_ELBOW, RIGHT_WRIST, "右肘角度"),
    (LEFT_ELBOW, LEFT_SHOULDER, LEFT_HIP,     "左肩角度"),
    (RIGHT_ELBOW, RIGHT_SHOULDER, RIGHT_HIP,  "右肩角度"),
    # --- 躯干 ---
    (LEFT_SHOULDER, LEFT_HIP, LEFT_KNEE,      "左躯干倾角"),
    (RIGHT_SHOULDER, RIGHT_HIP, RIGHT_KNEE,   "右躯干倾角"),
    (NOSE, LEFT_SHOULDER, LEFT_HIP,           "头部-左肩-左髋角度"),
    (NOSE, RIGHT_SHOULDER, RIGHT_HIP,         "头部-右肩-右髋角度"),
    # --- 下肢 ---
    (LEFT_HIP, LEFT_KNEE, LEFT_ANKLE,         "左膝角度"),
    (RIGHT_HIP, RIGHT_KNEE, RIGHT_ANKLE,      "右膝角度"),
    (LEFT_SHOULDER, LEFT_HIP, LEFT_KNEE,      "左髋角度"),
    (RIGHT_SHOULDER, RIGHT_HIP, RIGHT_KNEE,   "右髋角度"),
    (LEFT_KNEE, LEFT_ANKLE, LEFT_FOOT_INDEX,  "左踝背屈角度"),
    (RIGHT_KNEE, RIGHT_ANKLE, RIGHT_FOOT_INDEX, "右踝背屈角度"),
]


def calculate_angle(a, b, c):
    """
    计算三点之间的夹角（度数），b 为顶点。
    使用向量点积公式，对 MediaPipe 图像坐标系（y 轴朝下）做了适配。
    """
    a = np.array(a, dtype=float)
    b = np.array(b, dtype=float)
    c = np.array(c, dtype=float)

    ba = a - b
    bc = c - b

    # 向量点积 / 叉积求夹角（更稳定，不受坐标系方向影响）
    cosine = np.dot(ba, bc) / (np.linalg.norm(ba) * np.linalg.norm(bc) + 1e-8)
    cosine = np.clip(cosine, -1.0, 1.0)  # 防止浮点溢出
    angle = np.degrees(np.arccos(cosine))

    return round(angle, 2)


def get_all_angles(landmarks):
    """从一组 landmark 中提取所有预定义的关节角度"""
    angles = {}
    for point_a, point_b, point_c, name in JOINT_ANGLES:
        a = [landmarks[point_a].x, landmarks[point_a].y]
        b = [landmarks[point_b].x, landmarks[point_b].y]
        c = [landmarks[point_c].x, landmarks[point_c].y]
        angles[name] = calculate_angle(a, b, c)
    return angles


def encode_frame_to_base64(frame):
    """将 OpenCV 图像编码为 base64 字符串，压缩质量 80 以节省 Token"""
    encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), 80]
    _, buffer = cv2.imencode('.jpg', frame, encode_param)
    return base64.b64encode(buffer).decode('utf-8')


def save_keyframes_to_local(selected_frames, fps, output_dir=OUTPUT_DIR):
    """
    将关键帧保存到本地目录
    :param selected_frames: 选中的关键帧列表，格式为 [(frame_idx, lm, frame_bgr, diff), ...]
    :param fps: 视频帧率
    :param output_dir: 保存目录
    :return: 保存的文件路径列表
    """
    # 创建输出目录
    os.makedirs(output_dir, exist_ok=True)

    saved_paths = []
    for i, (fidx, lm, frame_bgr, _) in enumerate(selected_frames):
        time_sec = fidx / fps
        # 文件名格式: keyframe_序号_帧号_时间戳.jpg
        filename = f"keyframe_{i + 1:02d}_frame{fidx:05d}_{time_sec:.2f}s.jpg"
        filepath = os.path.join(output_dir, filename)
        cv2.imwrite(filepath, frame_bgr)
        saved_paths.append(filepath)

    return saved_paths


def extract_key_frames_adaptive(video_path, max_frames=8, frame_strategy="uniform"):
    """
    自适应抽帧策略：基于帧间姿态差异，在动作变化大的时刻多采样。
    如果视频很短或变化很小，退化为均匀抽帧。
    """
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print(f"错误: 无法打开视频 {video_path}")
        return None, None, None

    fps = cap.get(cv2.CAP_PROP_FPS)
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    duration = total_frames / fps

    all_frame_data = []  # (frame_idx, landmarks_list, frame_bgr)
    prev_landmarks_flat = None

    frame_idx = 0
    with mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5) as pose:
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break

            image_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = pose.process(image_rgb)

            if results.pose_landmarks:
                lm = results.pose_landmarks.landmark
                # 将关键点展平为向量，用于计算帧间差异
                lm_flat = np.array([[l.x, l.y, l.visibility] for l in lm]).flatten()

                if prev_landmarks_flat is not None:
                    diff = np.linalg.norm(lm_flat - prev_landmarks_flat)
                else:
                    diff = 0.0

                all_frame_data.append((frame_idx, lm, frame.copy(), diff))
                prev_landmarks_flat = lm_flat

            frame_idx += 1

    cap.release()

    if not all_frame_data:
        return None, None, None

    # ===== 选择关键帧 =====
    if len(all_frame_data) <= max_frames:
        # 帧数不多，全部使用
        selected = all_frame_data
    else:
        if FRAME_STRATEGY == "adaptive":
            # 按帧间差异排序，选出变化最大的帧，加上首尾帧
            diffs = [d[3] for d in all_frame_data]
            # 确保首尾帧入选
            indices = {0, len(all_frame_data) - 1}
            # 剩余名额按差异大小选
            remaining = max_frames - 2
            sorted_by_diff = sorted(
                range(1, len(all_frame_data) - 1),
                key=lambda i: all_frame_data[i][3],
                reverse=True
            )
            for i in sorted_by_diff[:remaining]:
                indices.add(i)
            selected = [all_frame_data[i] for i in sorted(indices)]
        else:
            # 均匀抽帧
            step = len(all_frame_data) // max_frames
            selected = all_frame_data[::step][:max_frames]
            # 确保最后一帧包含
            if all_frame_data[-1] not in selected:
                selected[-1] = all_frame_data[-1]
        # ===== 保存关键帧到本地 =====
    print(f"\n💾 正在保存 {len(selected)} 个关键帧到 {OUTPUT_DIR}...")
    saved_paths = save_keyframes_to_local(selected, fps)
    for path in saved_paths:
        print(f"   ✅ 已保存: {path}")

    # ===== 构造结果 =====
    analysis_data = []
    base64_frames = []
    for fidx, lm, frame_bgr, _ in selected:
        angles = get_all_angles(lm)
        time_sec = fidx / fps
        frame_entry = {
            "frame_index": fidx,
            "time": f"{time_sec:.2f}s",
            **angles
        }
        analysis_data.append(frame_entry)
        base64_frames.append(encode_frame_to_base64(frame_bgr))

    return analysis_data, base64_frames, duration




def analyze_with_llm(analysis_data, base64_frames, exercise_type, duration):
    """构造多模态 Prompt，调用大模型进行通用评估"""

    # 自动检测模式
    if exercise_type == "自动识别":
        type_instruction = (
            "首先，请根据视频截图和骨骼数据，**判断用户正在执行的动作类型**（如深蹲、俯卧撑、硬拉、"
            "平板支撑、引体向上、二头弯举、臀桥、波比跳等），然后基于该动作的标准进行评估。"
        )
    else:
        type_instruction = f"用户标注的动作类型为【{exercise_type}】。"

    text_prompt = f"""你是一位拥有10年经验的专业健身教练和运动生物力学专家。
    {type_instruction}
    视频时长约 {duration:.1f} 秒。系统从视频中提取了 {len(analysis_data)} 个关键帧，
    每个关键帧包含通过 MediaPipe 骨骼识别计算出的 **14 个主要关节角度**（单位：度）。
    以下是结构化数据：
    json{json.dumps(analysis_data, ensure_ascii=False, indent=2)}
    请结合上述数据和视频截图，进行综合分析并输出以下报告：
    ## 📋 评估报告
    ### 1️⃣ 动作识别
    {("请判断动作类型并说明判断依据。" if exercise_type == "自动识别" else "确认动作类型。")}
    ### 2️⃣ 动作标准度评分
    给出一个 0-100 分的总体评分，并简要说明评分依据。
    ### 3️⃣ 关键数据解读
    - 针对该动作最核心的 2-3 个关节角度进行详细分析（说明标准范围、实际数值、偏差程度）
    - 分析各帧之间角度的变化趋势，判断动作是否稳定、是否到位
    ### 4️⃣ 常见错误检测
    检查是否存在以下常见问题（根据动作类型选择相关的）：
    - **关节对齐**：膝盖是否内扣/外翻、手腕是否弯曲、肘部是否外展过大
    - **躯干控制**：是否弯腰驼背、骨盆是否眨眼(背部反弓)、重心是否偏移
    - **对称性**：左右两侧角度差异是否超过 10°
    - **动作幅度**：是否下蹲/下降不够深、手臂是否完全伸展等
    - **节奏控制**：各阶段速度是否均匀、有无停顿或弹振
    ### 5️⃣ 改进建议
    给出 3-5 条具体、可操作的纠正建议，使用简洁的口令式语言（如"想象屁股向后坐椅子"）。
    ### 6️⃣ 总结鼓励
    用积极、鼓励的语气进行总结。
    请确保报告专业、详细且易于理解。
    """

    content_list = [{"type": "text", "text": text_prompt}]
    for img_b64 in base64_frames:
        content_list.append({
            "type": "image_url",
            "image_url": {"url": f"data:image/jpeg;base64,{img_b64}"}
        })

    print(f"正在调用 qwen-omni-turbo 进行多模态分析（{len(base64_frames)} 帧图像）...\n")

    response = client.chat.completions.create(
        model="qwen-omni-turbo",
        messages=[{"role": "user", "content": content_list}],
    )
    return response.choices[0].message.content


def main():
    print("=" * 50)
    print(f"  通用动作分析器  |  视频: {VIDEO_PATH}")
    print(f"  动作类型: {EXERCISE_TYPE}")
    print("=" * 50)

    # 1. 视频特征提取
    print("\n[1/2] 正在使用 MediaPipe 提取全量关节角度...")
    analysis_data, base64_frames, duration = extract_key_frames_adaptive(VIDEO_PATH)

    if not analysis_data:
        print("❌ 未能从视频中检测到人体姿态。")
        print("   请确保：")
        print("   - 视频中人物全身可见")
        print("   - 光线充足、背景不太复杂")
        print("   - 视频文件路径正确")
        return

    print(f"✅ 成功提取 {len(analysis_data)} 个关键帧，视频时长 {duration:.1f}s")
    print(f"   每帧包含 {len(analysis_data[0]) - 2} 个关节角度指标")
    print("\n📊 数据样例（第一帧）:")
    sample = {k: v for k, v in analysis_data[0].items()
              if k not in ("frame_index", "time")}
    print(json.dumps(sample, ensure_ascii=False, indent=2))

    # 2. 大模型分析
    print(f"\n[2/2] 发送数据给大模型进行评估...")
    report = analyze_with_llm(analysis_data, base64_frames, EXERCISE_TYPE, duration)

    # 3. 输出结果
    print("\n" + "=" * 50)
    print(report)
    print("=" * 50)


if __name__ == "__main__":
    main()



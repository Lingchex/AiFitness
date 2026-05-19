import os
import uuid
import json
from flask import Flask, request, jsonify
from werkzeug.utils import secure_filename
import cv2



app = Flask(__name__)

ALLOWED_EXTENSIONS = {'mp4', 'avi', 'mov', 'mkv', 'flv'}
UPLOAD_FOLDER = './temp_uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


def allowed_file(filename):
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({"status": "ok", "service": "Fitness Analyzer API"})


@app.route('/api/analyze', methods=['POST'])
def analyze_video():
    data = request.form if request.files else request.get_json(silent=True)
    if not data:
        return jsonify({"code": 400, "msg": "请求参数不能为空"}), 400

    # ✅ 延迟导入：只有真正需要分析时才导入，避开启动时的 numpy/jax 冲突
    try:
        from analyzer import (
            extract_key_frames_adaptive,
            analyze_with_llm,
            MAX_FRAMES,
            FRAME_STRATEGY
        )
    except Exception as import_err:
        return jsonify({
            "code": 500,
            "msg": f"分析引擎加载失败，请检查依赖库版本: {str(import_err)}"
        }), 500

    # 参数解析
    exercise_type = data.get("exercise_type", "自动识别")
    max_frames = int(data.get("max_frames", MAX_FRAMES))
    frame_strategy = data.get("frame_strategy", FRAME_STRATEGY)

    video_path = None
    cleanup_required = False

    try:
        # 模式1：处理上传文件
        if 'file' in request.files:
            file = request.files['file']
            if file.filename == '':
                return jsonify({"code": 400, "msg": "未选择文件"}), 400

            if file and allowed_file(file.filename):
                ext = file.filename.rsplit('.', 1)[1].lower()
                filename = f"{uuid.uuid4().hex}.{ext}"
                save_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(save_path)
                video_path = save_path
                cleanup_required = True
            else:
                return jsonify({"code": 400, "msg": f"不支持的文件格式，仅支持 {ALLOWED_EXTENSIONS}"}), 400

        # 模式2：处理本地路径
        elif 'video_path' in data:
            video_path = data.get('video_path')
            if not os.path.exists(video_path):
                return jsonify({"code": 404, "msg": f"服务器上找不到视频文件: {video_path}"}), 404
        else:
            return jsonify({"code": 400, "msg": "必须提供 file 或 video_path 参数"}), 400

        # 调用分析（直接传参）
        analysis_data, base64_frames, duration = extract_key_frames_adaptive(
            video_path,
            max_frames=max_frames,
            frame_strategy=frame_strategy
        )

        if not analysis_data:
            return jsonify({
                "code": 404,
                "msg": "未能从视频中检测到人体姿态。请确保视频中人物全身可见且光线充足。"
            }), 404

        report = analyze_with_llm(analysis_data, base64_frames, exercise_type, duration)

        metrics = []
        for frame in analysis_data:
            metrics.append({
                "frame_index": frame.get("frame_index"),
                "time": frame.get("time"),
                "angles": {k: v for k, v in frame.items() if k not in ("frame_index", "time")}
            })

        return jsonify({
            "code": 200,
            "msg": "分析成功",
            "data": {
                "video_info": {
                    "duration_sec": round(duration, 2),
                    "extracted_frames": len(analysis_data),
                    "exercise_type": exercise_type
                },
                "metrics": metrics,
                "report": report
            }
        })

    except Exception as e:
        return jsonify({"code": 500, "msg": f"服务器内部错误: {str(e)}"}), 500

    finally:
        if cleanup_required and video_path and os.path.exists(video_path):
            try:
                os.remove(video_path)
            except Exception:
                pass


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5005, debug=True)

# AI Fitness Analyzer（健身动作 AI 分析）

基于 **MediaPipe** 人体姿态识别与 **大模型多模态 API** 的健身动作分析服务。  
从训练视频中提取关键帧与关节角度，生成动作标准度评估报告。

## 功能

- 视频上传或服务器本地路径分析
- MediaPipe 提取 14+ 关节角度（肘、肩、膝、髋等）
- 均匀 / 自适应关键帧抽取
- 调用 `qwen-omni-turbo` 生成结构化健身评估报告

## 技术栈

- Python 3.8+
- Flask
- OpenCV + MediaPipe
- OpenAI 兼容 API（DashScope / 自定义 base_url）

## API 说明
- GET /api/health
服务健康检查。

- POST /api/analyze
分析健身视频。


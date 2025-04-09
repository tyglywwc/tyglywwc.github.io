from flask import Flask, request, jsonify, render_template, url_for
import cv2
import numpy as np
from pathfinding.core.grid import Grid
from pathfinding.finder.a_star import AStarFinder
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)

# 配置
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['MAX_CONTENT_LENGTH'] = 5 * 1024 * 1024  # 5MB
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# 加载YOLO模型
net = cv2.dnn.readNet("yolov3.weights", "yolov3.cfg")
with open("coco.names") as f:
    classes = [line.strip() for line in f]


@app.route('/')
def home():
    return render_template('index.html')

@app.route('/api/banners')
def get_banners():
    import os
    try:
        banner_dir = os.path.join(app.static_folder, 'images', 'banners')
        banners = [
            url_for('static', filename=f'images/banners/{f}')
            for f in os.listdir(banner_dir)
            if f.lower().endswith(('.jpg', '.jpeg', '.png'))
        ]
        return jsonify(banners)
    except Exception as e:
        return jsonify([]), 500

@app.route('/detect', methods=['POST'])
def detect():
    if 'file' not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    filename = secure_filename(file.filename)
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(filepath)

    img = cv2.imread(filepath)
    if img is None:
        return jsonify({"error": "Image decoding failed"}), 400

    # 物体检测逻辑
    blob = cv2.dnn.blobFromImage(img, 1 / 255, (416, 416), swapRB=True)
    net.setInput(blob)
    layer_names = net.getLayerNames()
    output_layers = [layer_names[i - 1] for i in net.getUnconnectedOutLayers()]
    outs = net.forward(output_layers)

    # 处理检测结果
    height, width = img.shape[:2]
    boxes, confidences, class_ids = [], [], []

    for out in outs:
        for detection in out:
            scores = detection[5:]
            class_id = np.argmax(scores)
            confidence = scores[class_id]
            if confidence > 0.5:
                center_x = int(detection[0] * width)
                center_y = int(detection[1] * height)
                w = int(detection[2] * width)
                h = int(detection[3] * height)
                boxes.append([center_x - w // 2, center_y - h // 2, w, h])
                confidences.append(float(confidence))
                class_ids.append(class_id)

    indexes = cv2.dnn.NMSBoxes(boxes, confidences, 0.5, 0.4).flatten()

    results = []
    for i in indexes:
        results.append({
            "class": classes[class_ids[i]],
            "confidence": float(confidences[i]),
            "bbox": boxes[i],
            "center": [boxes[i][0] + boxes[i][2] // 2, boxes[i][1] + boxes[i][3] // 2]
        })

    return jsonify({
        "success": True,
        "image_url": url_for('static', filename=f'uploads/{filename}'),
        "objects": results,
        "image_size": {"width": width, "height": height}
    })


@app.route('/navigate', methods=['POST'])
def navigate():
    data = request.json
    obstacles = data.get('obstacles', [])
    start = data.get('start', [10, 10])  # 默认起点
    end = data.get('end', [90, 90])  # 默认终点

    try:
        # 创建20x20的网格地图
        grid_size = 20
        matrix = np.ones((grid_size, grid_size), dtype=np.int8)

        # 标记障碍物（坐标转换为网格）
        for obj in obstacles:
            x = int(obj['x'] * grid_size / 100)
            y = int(obj['y'] * grid_size / 100)
            if 0 <= x < grid_size and 0 <= y < grid_size:
                matrix[y][x] = 0

        grid = Grid(matrix=matrix)

        # 转换起点终点坐标
        start_node = grid.node(
            int(start[0] * grid_size / 100),
            int(start[1] * grid_size / 100)
        )
        end_node = grid.node(
            int(end[0] * grid_size / 100),
            int(end[1] * grid_size / 100)
        )

        finder = AStarFinder()
        path, runs = finder.find_path(start_node, end_node, grid)

        # 转换回百分比坐标
        path_percent = [
            [int(x * 100 / grid_size), int(y * 100 / grid_size)]
            for x, y in path
        ]

        return jsonify({
            "success": True,
            "path": path_percent,
            "obstacles": [
                [int(x * 100 / grid_size), int(y * 100 / grid_size)]
                for y in range(grid_size)
                for x in range(grid_size)
                if matrix[y][x] == 0
            ],
            "metrics": {
                "path_length": len(path),
                "operations": runs
            }
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, threaded=True)
// 上传图片交互
document.getElementById("scan-btn").addEventListener("click", function() {
    document.getElementById("file-input").click();
});

document.getElementById("file-input").addEventListener("change", function(e) {
    const file = e.target.files[0];
    if (!file) return;

    const resultDiv = document.getElementById("result");
    resultDiv.innerHTML = `
        <h3 style="color: #4361ee;"><i class="fas fa-spinner fa-spin"></i> 正在分析</h3>
        <p>已上传: ${file.name}</p>
        <div class="loader" style="width: 50px; height: 50px; border: 5px solid #f3f3f3; border-top: 5px solid #4361ee; border-radius: 50%; margin: 20px auto; animation: spin 1s linear infinite;"></div>
    `;

    // 模拟处理过程
    setTimeout(() => {
        resultDiv.innerHTML = `
            <h3 style="color: #4361ee;"><i class="fas fa-check-circle"></i> 检测完成</h3>
            <div style="background: #f0f8ff; padding: 15px; border-radius: 10px; margin-top: 15px;">
                <p><i class="fas fa-user" style="color: #4361ee;"></i> 前方2米处有行人</p>
                <p><i class="fas fa-car" style="color: #4361ee;"></i> 右侧3米处有车辆</p>
                <p><i class="fas fa-archway" style="color: #4361ee;"></i> 5米外有楼梯</p>
            </div>
            <button class="btn-gradient" style="margin-top: 20px;">
                <i class="fas fa-volume-up"></i> 语音播报
            </button>
        `;
    }, 2000);
});

// 导航按钮交互
document.getElementById("nav-btn").addEventListener("click", function() {
    const resultDiv = document.getElementById("result");
    resultDiv.innerHTML = `
        <h3 style="color: #4361ee;"><i class="fas fa-directions"></i> 导航已启动</h3>
        <div style="display: flex; align-items: center; gap: 15px; margin: 20px 0;">
            <i class="fas fa-arrow-left" style="font-size: 2rem; color: #4361ee;"></i>
            <p style="margin: 0;">前方10米后 <strong>左转</strong></p>
        </div>
        <p><i class="fas fa-info-circle" style="color: #4361ee;"></i> 正在避开右侧障碍物</p>
    `;

    // 添加动画效果
    const arrow = resultDiv.querySelector(".fa-arrow-left");
    let count = 0;
    const animate = () => {
        arrow.style.transform = `translateX(${count++ % 2 === 0 ? '-5px' : '5px'})`;
        requestAnimationFrame(animate);
    };
    animate();
});

// 添加CSS动画
const style = document.createElement('style');
style.textContent = `
    @keyframes spin {
        0% { transform: rotate(0deg); }
        100% { transform: rotate(360deg); }
    }
`;
document.head.appendChild(style);
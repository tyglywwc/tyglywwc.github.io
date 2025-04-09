// 图片列表（需与后端路由配合）
const banners = [
    "{{ url_for('static', filename='images/banners/banner1.jpg') }}",
    "{{ url_for('static', filename='images/banners/banner2.jpg') }}",
    "{{ url_for('static', filename='images/banners/banner3.jpg') }}"
];

// 使用动态获取方式（推荐）
document.addEventListener('DOMContentLoaded', () => {
    fetch('/api/banners')
        .then(res => res.json())
        .then(banners => {
            const container = document.querySelector('.slideshow-container');

            // 清空容器（防止重复加载）
            container.innerHTML = '';

            banners.forEach((img, index) => {
                const slide = document.createElement('div');
                slide.className = `slide ${index === 0 ? 'active' : ''}`;
                slide.style.backgroundImage = `linear-gradient(rgba(0,0,0,0.3), rgba(0,0,0,0.3)), url(${img})`;
                container.appendChild(slide);
            });

            // 轮播逻辑
            let currentIndex = 0;
            const slides = document.querySelectorAll('.slide');

            function rotateBanner() {
                if (slides.length === 0) return;

                slides[currentIndex].classList.remove('active');
                currentIndex = (currentIndex + 1) % slides.length;
                slides[currentIndex].classList.add('active');
            }

            // 安全检查
            if (slides.length > 0) {
                setInterval(rotateBanner, 5000);
            } else {
                console.warn('No banner images found');
                // 显示默认背景
                container.style.background = `linear-gradient(45deg, #4361ee, #4cc9f0)`;
            }
        })
        .catch(err => {
            console.error('Failed to load banners:', err);
        });
});
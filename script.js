document.addEventListener("DOMContentLoaded", function() {
    // 找到所有带有 data-github-repo 属性的元素 (也就是我们的 Badge)
    const repos = document.querySelectorAll("[data-github-repo]");
    
    repos.forEach(async el => {
        const repo = el.getAttribute("data-github-repo");
        try {
            // 请求 GitHub API
            const response = await fetch(`https://api.github.com/repos/${repo}`);
            if (!response.ok) throw new Error('Network response was not ok');
            
            const data = await response.json();
            const stars = data.stargazers_count;
            
            // 格式化: 1200 -> 1.2k
            const formatted = stars >= 1000 ? (stars / 1000).toFixed(1) + 'k' : stars;
            
            // 找到内部的数字容器
            const countSpan = el.querySelector(".star-count");
            const suffixSpan = el.querySelector(".star-suffix");
            
            if (countSpan && suffixSpan) {
                countSpan.textContent = formatted;
                // 成功获取数据后，显示整个后缀区域 (包括数字和星星图标)
                suffixSpan.style.display = "inline"; 
            }
        } catch (error) {
            console.log("Failed to fetch stars for " + repo);
            // 失败时不做任何操作，保持默认的隐藏状态
        }
    });
});

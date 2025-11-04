
# HTML 模板 - 仿照图片中的卡片样式
COURSE_LIST_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: "PingFang SC", "Microsoft YaHei", sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 30px 20px;
            -webkit-font-smoothing: antialiased;
            -moz-osx-font-smoothing: grayscale;
            text-rendering: optimizeLegibility;
        }
        
        .container {
            max-width: 1200px;
            margin: 0 auto;
        }
        
        .header {
            text-align: center;
            color: white;
            margin-bottom: 30px;
        }
        
        .header h1 {
            font-size: 48px;
            font-weight: 800;
            margin-bottom: 10px;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.2);
        }
        
        .header p {
            font-size: 20px;
            opacity: 0.9;
        }
        
        .course-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(500px, 1fr));
            gap: 25px;
        }
        
        .course-card {
            background: white;
            border-radius: 16px;
            overflow: hidden;
            box-shadow: 0 8px 24px rgba(0,0,0,0.15);
            transition: transform 0.3s, box-shadow 0.3s;
        }
        
        .course-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 12px 32px rgba(0,0,0,0.2);
        }
        
        .course-cover {
            position: relative;
            width: 100%;
            height: 200px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            overflow: hidden;
        }
        
        .course-cover img {
            width: 100%;
            height: 100%;
            object-fit: cover;
        }
        
        .course-status-badge {
            position: absolute;
            top: 15px;
            right: 15px;
            padding: 8px 16px;
            border-radius: 20px;
            font-size: 16px;
            font-weight: 700;
            color: white;
            box-shadow: 0 2px 8px rgba(0,0,0,0.2);
        }
        
        .status-0 { background: #9e9e9e; } /* 未上架 */
        .status-1 { background: #ffc107; } /* 未开始 */
        .status-2 { background: #4caf50; } /* 进行中 */
        .status-3 { background: #f44336; } /* 已结束 */
        .status-4 { background: #607d8b; } /* 已下架 */
        
        .course-content {
            padding: 20px;
        }
        
        .course-title {
            font-size: 26px;
            font-weight: 700;
            color: #333;
            margin-bottom: 15px;
            line-height: 1.4;
            display: -webkit-box;
            -webkit-line-clamp: 2;
            -webkit-box-orient: vertical;
            overflow: hidden;
        }
        
        .course-meta {
            display: flex;
            flex-wrap: wrap;
            gap: 12px;
            margin-bottom: 15px;
        }
        
        .meta-tag {
            display: inline-flex;
            align-items: center;
            padding: 6px 12px;
            background: #f5f5f5;
            border-radius: 8px;
            font-size: 13px;
            color: #666;
        }
        
        .meta-tag .emoji {
            margin-right: 4px;
        }
        
        .course-info {
            margin-top: 15px;
            padding-top: 15px;
            border-top: 1px solid #eee;
        }
        
        .info-row {
            display: flex;
            align-items: flex-start;
            margin-bottom: 10px;
            font-size: 14px;
            line-height: 1.6;
        }
        
        .info-row:last-child {
            margin-bottom: 0;
        }
        
        .info-label {
            font-weight: bold;
            color: #666;
            min-width: 80px;
            flex-shrink: 0;
        }
        
        .info-value {
            color: #333;
            flex: 1;
        }
        
        .highlight {
            color: #667eea;
            font-weight: bold;
        }
        
        .people-info {
            display: flex;
            align-items: center;
            gap: 10px;
            margin-top: 15px;
            padding: 12px;
            background: linear-gradient(135deg, #e3f2fd 0%, #f3e5f5 100%);
            border-radius: 8px;
        }
        
        .people-info .emoji {
            font-size: 20px;
        }
        
        .people-text {
            flex: 1;
            font-size: 14px;
            color: #333;
        }
        
        .footer {
            text-align: center;
            color: white;
            margin-top: 30px;
            padding: 20px;
            font-size: 14px;
            opacity: 0.9;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>📚 第二课堂课程列表</h1>
            <p>共 {{ total_count }} 个课程{% if display_count < total_count %} · 显示前 {{ display_count }} 个{% endif %}</p>
        </div>
        
        <div class="course-grid">
            {% for course in courses %}
            <div class="course-card">
                <div class="course-cover">
                    {% if course.cover_url %}
                    <img src="{{ course.cover_url }}" alt="{{ course.title }}" onerror="this.style.display='none'">
                    {% endif %}
                    <div class="course-status-badge status-{{ course.sign_status }}">
                        {{ course.status_text }}
                    </div>
                </div>
                
                <div class="course-content">
                    <div class="course-title">{{ course.title }}</div>
                    
                    <div class="course-meta">
                        {% if course.category %}
                        <span class="meta-tag">
                            <span class="emoji">📂</span> {{ course.category }}
                        </span>
                        {% endif %}
                        {% if course.type %}
                        <span class="meta-tag">
                            <span class="emoji">🏷️</span> {{ course.type }}
                        </span>
                        {% endif %}
                        {% if course.score %}
                        <span class="meta-tag">
                            <span class="emoji">⭐</span> {{ course.score }} 分
                        </span>
                        {% endif %}
                    </div>
                    
                    {% if course.department %}
                    <div class="info-row">
                        <span class="info-label">主办单位：</span>
                        <span class="info-value">{{ course.department }}</span>
                    </div>
                    {% endif %}
                    
                    {% if course.sign_time %}
                    <div class="info-row">
                        <span class="info-label">报名时间：</span>
                        <span class="info-value">{{ course.sign_time }}</span>
                    </div>
                    {% endif %}
                    
                    {% if course.activity_time %}
                    <div class="info-row">
                        <span class="info-label">活动时间：</span>
                        <span class="info-value">{{ course.activity_time }}</span>
                    </div>
                    {% endif %}
                    
                    {% if course.time_place %}
                    <div class="info-row">
                        <span class="info-label">时间地点：</span>
                        <span class="info-value">{{ course.time_place }}</span>
                    </div>
                    {% endif %}
                    
                    {% if course.show_people_info %}
                    <div class="people-info">
                        <span class="emoji">👥</span>
                        <div class="people-text">
                            <span class="highlight">{{ course.apply_count }}/{{ course.max_people }}</span> 人
                            · 剩余 <span class="highlight">{{ course.remaining }}</span> 个名额
                        </div>
                    </div>
                    {% endif %}
                </div>
            </div>
            {% endfor %}
        </div>
        
        <div class="footer">
            {% if total_count > display_count %}
            <p>还有 {{ total_count - display_count }} 个课程未显示</p>
            {% endif %}
            <p style="margin-top: 10px;">💡 使用 /第二课堂 [状态] 查看不同状态的课程</p>
            <p>状态：0-未上架 | 1-未开始 | 2-进行中 | 3-已结束 | 4-已下架</p>
        </div>
    </div>
</body>
</html>
"""




# 新课程通知的 HTML 模板
NEW_COURSE_NOTIFICATION_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: "PingFang SC", "Microsoft YaHei", sans-serif;
            background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
            padding: 30px 20px;
            -webkit-font-smoothing: antialiased;
            -moz-osx-font-smoothing: grayscale;
            text-rendering: optimizeLegibility;
        }
        
        .container {
            max-width: 1200px;
            margin: 0 auto;
        }
        
        .header {
            text-align: center;
            color: white;
            margin-bottom: 30px;
        }
        
        .header h1 {
            font-size: 42px;
            margin-bottom: 10px;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.2);
        }
        
        .header .badge {
            display: inline-block;
            padding: 10px 20px;
            background: rgba(255,255,255,0.3);
            border-radius: 20px;
            font-size: 20px;
            font-weight: 700;
            backdrop-filter: blur(10px);
        }
        
        .course-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(500px, 1fr));
            gap: 25px;
        }
        
        .course-card {
            background: white;
            border-radius: 16px;
            overflow: hidden;
            box-shadow: 0 8px 24px rgba(0,0,0,0.15);
            position: relative;
        }
        
        .new-badge {
            position: absolute;
            top: 15px;
            left: 15px;
            padding: 8px 16px;
            background: #ff5722;
            color: white;
            border-radius: 20px;
            font-size: 14px;
            font-weight: bold;
            z-index: 10;
            box-shadow: 0 2px 8px rgba(0,0,0,0.2);
            animation: pulse 2s infinite;
        }
        
        @keyframes pulse {
            0%, 100% { transform: scale(1); }
            50% { transform: scale(1.05); }
        }
        
        .course-cover {
            position: relative;
            width: 100%;
            height: 200px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            overflow: hidden;
        }
        
        .course-cover img {
            width: 100%;
            height: 100%;
            object-fit: cover;
        }
        
        .course-status-badge {
            position: absolute;
            top: 15px;
            right: 15px;
            padding: 8px 16px;
            border-radius: 20px;
            font-size: 14px;
            font-weight: bold;
            color: white;
            box-shadow: 0 2px 8px rgba(0,0,0,0.2);
        }
        
        .status-0 { background: #9e9e9e; }
        .status-1 { background: #ffc107; }
        .status-2 { background: #4caf50; }
        .status-3 { background: #f44336; }
        .status-4 { background: #607d8b; }
        
        .course-content {
            padding: 20px;
        }
        
        .course-title {
            font-size: 22px;
            font-weight: bold;
            color: #333;
            margin-bottom: 15px;
            line-height: 1.4;
        }
        
        .course-meta {
            display: flex;
            flex-wrap: wrap;
            gap: 12px;
            margin-bottom: 15px;
        }
        
        .meta-tag {
            display: inline-flex;
            align-items: center;
            padding: 6px 12px;
            background: #f5f5f5;
            border-radius: 8px;
            font-size: 13px;
            color: #666;
        }
        
        .meta-tag .emoji {
            margin-right: 4px;
        }
        
        .info-row {
            display: flex;
            align-items: flex-start;
            margin-bottom: 10px;
            font-size: 14px;
            line-height: 1.6;
        }
        
        .info-row:last-child {
            margin-bottom: 0;
        }
        
        .info-label {
            font-weight: bold;
            color: #666;
            min-width: 80px;
            flex-shrink: 0;
        }
        
        .info-value {
            color: #333;
            flex: 1;
        }
        
        .highlight {
            color: #f5576c;
            font-weight: bold;
        }
        
        .people-info {
            display: flex;
            align-items: center;
            gap: 10px;
            margin-top: 15px;
            padding: 12px;
            background: linear-gradient(135deg, #fff0e1 0%, #ffe5e5 100%);
            border-radius: 8px;
        }
        
        .people-info .emoji {
            font-size: 20px;
        }
        
        .people-text {
            flex: 1;
            font-size: 14px;
            color: #333;
        }
        
        .footer {
            text-align: center;
            color: white;
            margin-top: 30px;
            padding: 20px;
            font-size: 14px;
            opacity: 0.9;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🎉 第二课堂新课程通知</h1>
            <div class="badge">发现 {{ total_count }} 个新课程</div>
        </div>
        
        <div class="course-grid">
            {% for course in courses %}
            <div class="course-card">
                <div class="new-badge">🆕 NEW</div>
                <div class="course-cover">
                    {% if course.cover_url %}
                    <img src="{{ course.cover_url }}" alt="{{ course.title }}" onerror="this.style.display='none'">
                    {% endif %}
                    <div class="course-status-badge status-{{ course.sign_status }}">
                        {{ course.status_text }}
                    </div>
                </div>
                
                <div class="course-content">
                    <div class="course-title">{{ course.title }}</div>
                    
                    <div class="course-meta">
                        {% if course.category %}
                        <span class="meta-tag">
                            <span class="emoji">📂</span> {{ course.category }}
                        </span>
                        {% endif %}
                        {% if course.type %}
                        <span class="meta-tag">
                            <span class="emoji">🏷️</span> {{ course.type }}
                        </span>
                        {% endif %}
                        {% if course.score %}
                        <span class="meta-tag">
                            <span class="emoji">⭐</span> {{ course.score }} 分
                        </span>
                        {% endif %}
                    </div>
                    
                    {% if course.department %}
                    <div class="info-row">
                        <span class="info-label">主办单位：</span>
                        <span class="info-value">{{ course.department }}</span>
                    </div>
                    {% endif %}
                    
                    {% if course.sign_time %}
                    <div class="info-row">
                        <span class="info-label">报名时间：</span>
                        <span class="info-value">{{ course.sign_time }}</span>
                    </div>
                    {% endif %}
                    
                    {% if course.activity_time %}
                    <div class="info-row">
                        <span class="info-label">活动时间：</span>
                        <span class="info-value">{{ course.activity_time }}</span>
                    </div>
                    {% endif %}
                    
                    {% if course.time_place %}
                    <div class="info-row">
                        <span class="info-label">时间地点：</span>
                        <span class="info-value">{{ course.time_place }}</span>
                    </div>
                    {% endif %}
                    
                    {% if course.show_people_info %}
                    <div class="people-info">
                        <span class="emoji">👥</span>
                        <div class="people-text">
                            <span class="highlight">{{ course.apply_count }}/{{ course.max_people }}</span> 人
                            · 剩余 <span class="highlight">{{ course.remaining }}</span> 个名额
                        </div>
                    </div>
                    {% endif %}
                </div>
            </div>
            {% endfor %}
        </div>
        
        <div class="footer">
            {% if total_count > display_count %}
            <p>还有 {{ total_count - display_count }} 个新课程未显示</p>
            {% endif %}
            <p style="margin-top: 10px;">💡 使用 /第二课堂 命令查看所有课程</p>
        </div>
    </div>
</body>
</html>
'''


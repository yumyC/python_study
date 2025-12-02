from selenium import webdriver
from selenium.webdriver.common.by import By
import openpyxl
import time

# 站点映射
sites = {
    "www-en": "https://www.one-line.com/en/news/all-news/all-years/all-months",
    "www-jp": "https://www.one-line.com/ja/news/all-news/all-years/all-months",
    "au": "https://au.one-line.com/news/all-news/all-years/all-months",
    "bd": "https://bd.one-line.com/news/all-news/all-years/all-months",
    "br-en": "https://br.one-line.com/en/news/all-news/all-years/all-months",
    "br-pt": "https://br.one-line.com/pt-br/news/all-news/all-years/all-months",
    "ca": "https://ca.one-line.com/news/all-news/all-years/all-months",
    "ch-en": "https://ch.one-line.com/en/news/all-news/all-years/all-months",
    "ch-zh": "https://ch.one-line.com/zh-hans/news/all-news/all-years/all-months",
    "eua": "https://eua.one-line.com/news/all-news/all-years/all-months",
    "hk": "https://hk.one-line.com/news/all-news/all-years/all-months",
    "id": "https://id.one-line.com/news/all-news/all-years/all-months",
    "in": "https://in.one-line.com/news/all-news/all-years/all-months",
    "jp-en": "https://jp.one-line.com/en/news/all-news/all-years/all-months",
    "jp-ja": "https://jp.one-line.com/ja/news/all-news/all-years/all-months",
    "my": "https://my.one-line.com/news/all-news/all-years/all-months",
    "mm": "https://mm.one-line.com/news/all-news/all-years/all-months",
    "nz": "https://nz.one-line.com/news/all-news/all-years/all-months",
    "pk": "https://pk.one-line.com/news/all-news/all-years/all-months",
    "ph": "https://ph.one-line.com/news/all-news/all-years/all-months",
    "sg": "https://sg.one-line.com/news/all-news/all-years/all-months",
    "kr-en": "https://kr.one-line.com/en/news/all-news/all-years/all-months",
    "kr-ko": "https://kr.one-line.com/ko/news/all-news/all-years/all-months",
    "lk": "https://lk.one-line.com/news/all-news/all-years/all-months",
    "tw-en": "https://tw.one-line.com/en/news/all-news/all-years/all-months",
    "tw-zh": "https://tw.one-line.com/zh-hant/news/all-news/all-years/all-months",
    "th": "https://th.one-line.com/news/all-news/all-years/all-months",
    "us": "https://us.one-line.com/news/all-news/all-years/all-months",
    "uae": "https://uae.one-line.com/news/all-news/all-years/all-months",
    "la-en": "https://la.one-line.com/en/news/all-news/all-years/all-months",
    "la-es": "https://la.one-line.com/es/news/all-news/all-years/all-months",
    "vn": "https://vn.one-line.com/news/all-news/all-years/all-months",
    "ea": "https://ea.one-line.com/news/all-news/all-years/all-months",
    "kh": "https://kh.one-line.com/news/all-news/all-years/all-months",
    "holdco-en": "https://holdco.one-line.com/en/news/all-news/all-years/all-months",
    "holdco-ja": "https://holdco.one-line.com/ja/news/all-news/all-years/all-months"
}

# 初始化 Chrome
options = webdriver.ChromeOptions()
options.add_argument("--headless")  # 生产环境可开启 headless
driver = webdriver.Chrome(options=options)

results = {}

for code, url in sites.items():
    print(f"正在抓取 {code} ...")
    driver.get(url)
    time.sleep(3)  # 等 JS 渲染

    try:
        # 获取所有 li 元素
        dropdown_items = driver.find_elements(By.CSS_SELECTOR, ".news-categories-dropdown li")

        # 提取 li 内 <a> 的 innerText
        news_categories = []
        for li in dropdown_items:
            li_id = li.get_attribute("id")
            if li_id == "all-news":
                continue
            try:
                a_tag = li.find_element(By.TAG_NAME, "a")
                text = driver.execute_script("return arguments[0].innerText.trim();", a_tag)
                if text:
                    news_categories.append(text)
            except:
                continue

        # 获取主菜单文本
        try:
            main_menu_item = driver.find_element(By.CSS_SELECTOR, "#main-menu ul li:nth-child(3) a.no-link")
            main_menu_text = driver.execute_script("return arguments[0].innerText.trim();", main_menu_item)
            if not main_menu_text:
                main_menu_text = code
        except:
            main_menu_text = code

        results[code] = {
            "categories": news_categories,
            "main_menu_text": main_menu_text
        }
        print(f"{code} 抓取完成: {len(news_categories)} 个分类, 主菜单: {main_menu_text}")

    except Exception as e:
        print(f"{code} 抓取失败: {e}")
        results[code] = {
            "categories": [],
            "main_menu_text": code
        }

driver.quit()

# 构建 Excel
all_categories = set()
for site_data in results.values():
    all_categories.update(site_data["categories"])
all_categories = sorted(all_categories)

wb = openpyxl.Workbook()
ws = wb.active
ws.title = "News Categories"

# 表头：第一列 Category，后面每列显示 "主菜单 (语言)"
header = ["Category"]
for code in sites.keys():
    main_menu_text = results.get(code, {}).get("main_menu_text", code)
    # 解析语言信息
    if "-" in code:
        site_name, lang = code.split("-", 1)
        header.append(f"{main_menu_text} ({lang.upper()})")
    else:
        header.append(main_menu_text)
ws.append(header)

# 填充数据
for category in all_categories:
    row = [category]
    for code in sites.keys():
        site_cats = results.get(code, {}).get("categories", [])
        row.append("✅" if category in site_cats else "☐")
    ws.append(row)

# 保存 Excel
wb.save("one_line_news_multilang.xlsx")
print("Excel 已生成：one_line_news_multilang.xlsx")

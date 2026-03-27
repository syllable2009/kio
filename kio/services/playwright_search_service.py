import asyncio
import argparse
import json
from typing import Any, Dict, List
from urllib.parse import urljoin

from crawlee import Request
from crawlee.crawlers import PlaywrightCrawler, PlaywrightCrawlingContext


# 全局爬虫实例
crawler = PlaywrightCrawler(
    max_requests_per_crawl=50,
    headless=False,
    browser_type="chromium",
)

router = crawler.router

# 采集结果（在所有详情页里累积）
_collected_results: List[Dict[str, Any]] = []


def _get_common_user_data(context: PlaywrightCrawlingContext) -> Dict[str, Any]:
    """从请求中提取用户配置."""
    return context.request.user_data or {}


@router.handler("LIST")
async def handle_list_page(context: PlaywrightCrawlingContext) -> None:
    """
    列表页处理：
    - 找到列表中的所有链接
    - 按文本做模糊匹配
    - 把匹配到的链接加入队列，进入详情页
    """
    context.log.info(f"LIST page: {context.request.url}")

    user_data = _get_common_user_data(context)
    keyword = str(user_data.get("keyword", "")).strip().lower()
    list_selector = user_data.get("list_selector", "ul li a")

    if not keyword:
        context.log.warning("No keyword provided, skip fuzzy matching.")
        return

    page = context.page

    # 等待页面主要内容加载，模拟用户稍等一下
    await page.wait_for_timeout(1500)

    links = await page.locator(list_selector).all()
    context.log.info(f"Found {len(links)} candidate items in list.")

    base_url = str(context.request.loaded_url)

    for element in links:
        try:
            text = await element.inner_text()
            text = (text or "").strip()
            if not text:
                continue

            if keyword not in text.lower():
                continue

            href = await element.get_attribute("href")
            if not href or href.strip() in ("", "#", "javascript:void(0)"):
                continue

            absolute_url = urljoin(base_url, href)

            context.log.info(f"Matched item: text='{text}' url={absolute_url}")

            # 把详情页加入队列
            await context.enqueue_links(
                urls=[absolute_url],
                label="DETAIL",
                user_data={
                    **user_data,
                    "from_list_url": base_url,
                    "item_text": text,
                },
            )
        except Exception as e:
            context.log.warning(f"Failed to process list element: {e}")


@router.handler("DETAIL")
async def handle_detail_page(context: PlaywrightCrawlingContext) -> None:
    """
    详情页处理：
    - 根据选择器提取图片链接和页面中的超链接
    - 保存到内存，爬虫结束后统一写入文件
    """
    user_data = _get_common_user_data(context)
    image_selector = user_data.get("image_selector", "img")
    link_selector = user_data.get("link_selector", "a")

    context.log.info(f"DETAIL page: {context.request.url}")

    page = context.page

    # 模拟用户停留/浏览
    await page.wait_for_timeout(1000)

    # 提取图片
    image_elements = await page.locator(image_selector).all()
    image_urls: List[str] = []
    for el in image_elements:
        try:
            src = await el.get_attribute("src")
            if src and src.strip():
                image_urls.append(src.strip())
        except Exception as e:
            context.log.warning(f"Failed to read image src: {e}")

    # 提取链接
    link_elements = await page.locator(link_selector).all()
    link_urls: List[str] = []
    for el in link_elements:
        try:
            href = await el.get_attribute("href")
            if href and href.strip() not in ("", "#", "javascript:void(0)"):
                link_urls.append(href.strip())
        except Exception as e:
            context.log.warning(f"Failed to read link href: {e}")

    # 保存结果到全局列表
    _collected_results.append(
        {
            "detail_url": str(context.request.loaded_url),
            "from_list_url": user_data.get("from_list_url"),
            "item_text": user_data.get("item_text"),
            "images": image_urls,
            "links": link_urls,
        }
    )

    context.log.info(
        f"Collected {len(image_urls)} images and {len(link_urls)} links from detail page."
    )


async def handle_default_page(context: PlaywrightCrawlingContext) -> None:
    context.log.info(f"default:{context.request.url}")


router.default_handler(handle_default_page)


async def run_playwright_search_crawler(
    start_url: str,
    keyword: str,
    list_selector: str,
    image_selector: str,
    link_selector: str,
    output_path: str,
) -> None:
    """
    启动爬虫：
    - 从 start_url 作为列表页入口
    - 使用 keyword 做模糊搜索
    - 把所有匹配项的详情页结果写入 output_path (JSON)
    """
    global _collected_results
    _collected_results = []

    await crawler.run(
        [
            Request.from_url(
                url=start_url,
                label="LIST",
                user_data={
                    "keyword": keyword,
                    "list_selector": list_selector,
                    "image_selector": image_selector,
                    "link_selector": link_selector,
                    "output_path": output_path,
                },
            )
        ]
    )

    # 爬虫结束后统一写文件
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(_collected_results, f, ensure_ascii=False, indent=2)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="使用 PlaywrightCrawler 仿真人方式打开页面，模糊搜索列表并抓取详情页图片和链接。"
    )
    parser.add_argument(
        "--url",
        required=True,
        help="列表页起始 URL。",
    )
    parser.add_argument(
        "--keyword",
        required=True,
        help="在列表项文本中进行模糊匹配的关键字（不区分大小写）。",
    )
    parser.add_argument(
        "--list-selector",
        default="ul li a",
        help="列表中每一项链接的 CSS 选择器，默认 'ul li a'。",
    )
    parser.add_argument(
        "--image-selector",
        default="img",
        help="详情页中需要保存的图片 CSS 选择器，默认 'img'。",
    )
    parser.add_argument(
        "--link-selector",
        default="a",
        help="详情页中需要保存的链接 CSS 选择器，默认 'a'。",
    )
    parser.add_argument(
        "--output",
        default="playwright_search_results.json",
        help="保存结果的 JSON 文件路径，默认 'playwright_search_results.json'。",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    asyncio.run(
        run_playwright_search_crawler(
            start_url=args.url,
            keyword=args.keyword,
            list_selector=args.list_selector,
            image_selector=args.image_selector,
            link_selector=args.link_selector,
            output_path=args.output,
        )
    )


if __name__ == "__main__":
    main()


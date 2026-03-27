"""
VOA Special English（21voa）列表 → 详情 爬取：保存正文文本与 MP3。

参考 `playwright_service.py` 的 Crawlee + PlaywrightCrawler 写法；
入口列表页：https://www.21voa.com/special_english/
"""

from __future__ import annotations

import asyncio
import os
import re
from pathlib import Path
from urllib.parse import urljoin

from crawlee import Request
from crawlee.crawlers import PlaywrightCrawler, PlaywrightCrawlingContext

VOA_SPECIAL_ENGLISH_LIST_URL = "https://www.21voa.com/special_english/"

# 详情页 jPlayer 配置里的 mp3 地址
_MP3_IN_SCRIPT_RE = re.compile(
    r'''mp3\s*:\s*["'](https?://[^"']+\.mp3)["']''',
    re.IGNORECASE,
)

voa_crawler = PlaywrightCrawler(
    # 至少为 1（列表）+ 详情条数；默认留足余量
    max_requests_per_crawl=int(os.getenv("VOA_MAX_REQUESTS", "64")),
    headless=os.getenv("VOA_HEADLESS", "1") == "1",
    browser_type="chromium",
)

voa_router = voa_crawler.router


def _default_storage_root() -> Path:
    env = os.getenv("VOA_STORAGE_DIR")
    if env:
        return Path(env).expanduser().resolve()
    # 仓库根目录下的 storage/voa
    return (Path(__file__).resolve().parents[2] / "storage" / "voa").resolve()


def _slug_from_article_url(url: str) -> str:
    path = url.rstrip("/").split("/")[-1]
    if path.endswith(".html"):
        path = path[: -len(".html")]
    return path or "article"


def _extract_mp3_url(html: str) -> str | None:
    m = _MP3_IN_SCRIPT_RE.search(html)
    return m.group(1) if m else None


async def _save_text(path: Path, title: str, body: str) -> None:
    def _write() -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(f"{title}\n\n{body}".strip() + "\n", encoding="utf-8")

    await asyncio.to_thread(_write)


async def _download_mp3(
    context: PlaywrightCrawlingContext,
    url: str,
    dest: Path,
    *,
    referer: str,
) -> None:
    page = context.page
    resp = await page.request.get(
        url,
        timeout=120_000,
        headers={
            "Referer": referer,
            "User-Agent": (
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/123.0.0.0 Safari/537.36"
            ),
            "Accept": "audio/mpeg,audio/*;q=0.9,*/*;q=0.8",
        },
    )
    if resp.status != 200:
        raise RuntimeError(f"MP3 HTTP {resp.status}: {url}")

    body = await resp.body()

    def _write() -> None:
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_bytes(body)

    await asyncio.to_thread(_write)


@voa_router.handler("VOA_LIST")
async def handle_voa_list_page(context: PlaywrightCrawlingContext) -> None:
    """打开慢速英语列表页，解析条目后入队详情页。"""
    ud = context.request.user_data or {}
    max_articles = int(ud.get("max_articles", os.getenv("VOA_MAX_ARTICLES", "5")))
    storage_root = Path(str(ud.get("storage_root", _default_storage_root())))

    base_url = str(context.request.loaded_url)
    context.log.info(f"VOA_LIST: {base_url} max_articles={max_articles}")

    page = context.page
    await page.wait_for_selector("div.list ul li", timeout=60_000)

    li_elements = await page.locator("div.list ul li").all()
    seen: set[str] = set()
    enqueued = 0

    for li in li_elements:
        if enqueued >= max_articles:
            break
        try:
            anchors = await li.locator("a[href]").all()
            for a in anchors:
                href = await a.get_attribute("href")
                if not href or href.strip() in ("", "#", "javascript:void(0)"):
                    continue
                href = href.strip()
                # 栏目页如 /as_it_is.html；正文在 /special_english/xxx.html
                if "/special_english/" not in href or not href.endswith(".html"):
                    continue
                absolute_url = urljoin(base_url, href)
                if absolute_url in seen:
                    continue
                seen.add(absolute_url)

                # Crawlee：必须用 `requests=` 显式入队；`urls=` 不是合法参数，会退化为从页面抓所有 <a>，
                # 导致列表页/栏目页也被标成 VOA_DETAIL。
                await context.enqueue_links(
                    requests=[
                        Request.from_url(
                            absolute_url,
                            label="VOA_DETAIL",
                            user_data={
                                "storage_root": str(storage_root),
                                "list_url": base_url,
                            },
                        )
                    ],
                )
                enqueued += 1
                context.log.info(f"enqueue detail ({enqueued}/{max_articles}): {absolute_url}")
                if enqueued >= max_articles:
                    break
        except Exception as e:
            context.log.warning(f"list li failed: {e}")

    context.log.info(f"VOA_LIST done, enqueued {enqueued} detail requests.")


@voa_router.handler("VOA_DETAIL")
async def handle_voa_detail_page(context: PlaywrightCrawlingContext) -> None:
    """详情页：拉取正文、解析 MP3 链接并落盘。"""
    ud = context.request.user_data or {}
    storage_root = Path(str(ud.get("storage_root", _default_storage_root())))

    url = str(context.request.loaded_url or context.request.url)
    context.log.info(
        f"VOA_DETAIL: loaded_url={context.request.loaded_url} request.url={context.request.url}"
    )

    page = context.page
    await page.wait_for_selector("div.content", timeout=60_000)

    title = (await page.title()).strip() or _slug_from_article_url(url)
    body = (await page.locator("div.content").inner_text()).strip()
    html = await page.content()
    mp3_url = _extract_mp3_url(html)

    slug = _slug_from_article_url(url)
    out_dir = storage_root / slug
    text_path = out_dir / "article.txt"
    audio_path = out_dir / "audio.mp3"

    await _save_text(text_path, title, body)
    context.log.info(f"saved text: {text_path}")

    if mp3_url:
        try:
            await _download_mp3(context, mp3_url, audio_path, referer=url)
            context.log.info(f"saved audio: {audio_path} <= {mp3_url}")
        except Exception as e:
            context.log.error(f"audio download failed: {e}")
    else:
        context.log.warning("no mp3 url found in page script; text only saved.")


async def handle_voa_default_page(context: PlaywrightCrawlingContext) -> None:
    context.log.info(f"VOA default: {context.request.url}")


voa_router.default_handler(handle_voa_default_page)


async def crawl_voa_special_english(
    *,
    list_url: str = VOA_SPECIAL_ENGLISH_LIST_URL,
    max_articles: int | None = None,
    storage_root: Path | str | None = None,
) -> None:
    """
    爬取 21voa 慢速英语「最近更新」列表，再逐篇进入详情保存文本与 MP3。

    环境变量（可选）：
    - VOA_MAX_ARTICLES：默认每轮最多入队详情数（默认 5）
    - VOA_MAX_REQUESTS：Crawlee 最大请求数（默认 32，需 >= 1 + 详情数）
    - VOA_STORAGE_DIR：保存目录（默认 仓库根下 storage/voa）
    - VOA_HEADLESS：1/0，是否无头浏览器（默认 1）
    """
    root = Path(storage_root).expanduser().resolve() if storage_root else _default_storage_root()
    ma = max_articles if max_articles is not None else int(os.getenv("VOA_MAX_ARTICLES", "5"))

    await voa_crawler.run(
        [
            Request.from_url(
                list_url,
                label="VOA_LIST",
                user_data={
                    "max_articles": ma,
                    "storage_root": str(root),
                },
            )
        ]
    )


if __name__ == "__main__":
    # uv run python -m kio.services.voa_service
    asyncio.run(crawl_voa_special_english(max_articles=1))

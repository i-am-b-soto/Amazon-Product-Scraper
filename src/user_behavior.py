import random
import asyncio
from playwright.async_api import Page

async def human_sleep(min_time: float, max_time: float):
    await asyncio.sleep(random.uniform(min_time, max_time))


async def human_scroll(
    page: Page,
    max_scrolls: int = 5,
    use_mouse_movement: bool = True,
    use_keyboard_scroll: bool = True,
    use_wheel_scroll: bool = True
):
    viewport = await page.evaluate("""() => {
        return {
            height: window.innerHeight,
            scrollHeight: document.body.scrollHeight
        };
    }""")

    current_scroll = 0
    viewport_height = viewport["height"]
    scroll_height = viewport["scrollHeight"]

    for _ in range(max_scrolls):
        # Simulate random mouse movement across the screen
        if use_mouse_movement and random.random() < 0.7:
            try:
                x = random.randint(0, viewport_height)
                y = random.randint(0, viewport_height)
                await page.mouse.move(x, y)
            except Exception as e:
                pass  # Ignore failed mouse moves

        if random.random() < 0.2:
            await human_sleep(1.5, 3.0)

        scroll_by = random.randint(200, 600)

        if use_wheel_scroll and random.random() < 0.6:
            try:
                await page.mouse.wheel(0, scroll_by)
            except Exception as e:
                await page.evaluate(f"window.scrollBy(0, {scroll_by})")
        elif use_keyboard_scroll and random.random() < 0.5:
            await page.keyboard.press("PageDown")
            scroll_by = viewport_height
        else:
            await page.evaluate(f"window.scrollBy(0, {scroll_by})")

        current_scroll += scroll_by
        await human_sleep(0.2, 0.8)

        if current_scroll + 1000 > scroll_height:
            break


async def human_scroll_and_hover(
    page: Page,
    max_scrolls=5,
    use_mouse_movement=True,
    use_keyboard_scroll=True,
    use_wheel_scroll=True,
    max_hovers=2
):
    viewport = await page.evaluate("""() => {
        return {
            height: window.innerHeight,
            scrollHeight: document.body.scrollHeight
        };
    }""")

    current_scroll = 0
    viewport_height = viewport["height"]
    scroll_height = viewport["scrollHeight"]

    # Get visible links
    links = await page.locator("a").element_handles()
    visible_links = []
    for link in links:
        try:
            box = await link.bounding_box()
            href = await link.get_attribute("href")
            if box is not None and href:
                visible_links.append(link)
        except:
            pass

    hover_count = random.randint(1, max_hovers)

    for _ in range(max_scrolls):
        # Random mouse movement
        if use_mouse_movement and random.random() < 0.7:
            x_offset = random.randint(0, viewport_height)
            y_offset = random.randint(0, viewport_height)
            try:
                await page.mouse.move(x_offset, y_offset)
            except:
                pass

        if random.random() < 0.2:
            await human_sleep(1.5, 3)

        scroll_by = random.randint(200, 600)

        # Wheel scroll
        if use_wheel_scroll and random.random() < 0.6:
            try:
                await page.mouse.wheel(0, scroll_by)
            except:
                await page.evaluate(f"window.scrollBy(0, {scroll_by})")
        # Keyboard scroll
        elif use_keyboard_scroll and random.random() < 0.5:
            await page.keyboard.press("PageDown")
            scroll_by = viewport_height
        # Fallback
        else:
            await page.evaluate(f"window.scrollBy(0, {scroll_by})")

        current_scroll += scroll_by
        current_scroll = max(0, current_scroll)
        await human_sleep(0.2, 0.8)

        # Hover behavior
        if hover_count > 0 and visible_links:
            link = random.choice(visible_links)
            box = await link.bounding_box()
            if box:
                try:
                    # Move near the link first
                    offset_x = box["x"] + random.randint(-30, 30)
                    offset_y = box["y"] + random.randint(-10, 10)
                    await page.mouse.move(offset_x, offset_y)
                    await human_sleep(0.1, 0.4)

                    # Hover directly
                    await page.mouse.move(box["x"] + box["width"] / 2, box["y"] + box["height"] / 2)
                    await human_sleep(0.3, 2.0)

                    # Occasionally move away
                    if random.random() < 0.3:
                        await page.mouse.move(
                            offset_x + random.randint(50, 150),
                            offset_y + random.randint(20, 60)
                        )
                        await human_sleep(0.1, 0.4)
                except Exception as e:
                    pass
                finally:
                    hover_count -= 1

        if current_scroll + 1000 > scroll_height:
            break


async def perform_random_user_behavior(page):
    num = random.randint(1,10)
    if num == 1:
        await human_scroll_and_hover(page)
    if num == 2:
        await human_scroll(page)
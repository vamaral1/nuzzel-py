"""Stealth measures to avoid bot detection"""

import random
from typing import Optional

from playwright.async_api import BrowserContext, Page


async def apply_stealth_measures(context: BrowserContext) -> None:
    """
    Apply stealth measures to browser context to avoid detection.

    Args:
        context: Playwright browser context
    """
    # Override webdriver property
    await context.add_init_script("""
        Object.defineProperty(navigator, 'webdriver', {
            get: () => undefined
        });

        // Override plugins
        Object.defineProperty(navigator, 'plugins', {
            get: () => [1, 2, 3, 4, 5]
        });

        // Override languages
        Object.defineProperty(navigator, 'languages', {
            get: () => ['en-US', 'en']
        });

        // Override permissions
        const originalQuery = window.navigator.permissions.query;
        window.navigator.permissions.query = (parameters) => (
            parameters.name === 'notifications' ?
                Promise.resolve({ state: Notification.permission }) :
                originalQuery(parameters)
        );

        // Chrome runtime
        window.chrome = {
            runtime: {}
        };
    """)


async def human_like_scroll(page: Page, distance: Optional[int] = None) -> None:
    """
    Perform human-like scrolling with random variations.

    Args:
        page: Playwright page instance
        distance: Optional scroll distance, otherwise random
    """
    if distance is None:
        distance = random.randint(300, 800)

    # Scroll with easing (simulate human behavior)
    steps = random.randint(3, 6)
    step_distance = distance // steps

    for i in range(steps):
        scroll_amount = step_distance * (i + 1)
        await page.evaluate(f"window.scrollBy(0, {scroll_amount})")
        await page.wait_for_timeout(random.randint(100, 300))


async def random_mouse_movement(page: Page) -> None:
    """
    Perform random mouse movements to appear more human.

    Args:
        page: Playwright page instance
    """
    try:
        # Move mouse to random position
        x = random.randint(100, 800)
        y = random.randint(100, 600)
        await page.mouse.move(x, y)
        await page.wait_for_timeout(random.randint(50, 200))
    except Exception:
        # Ignore errors - mouse movement is optional
        pass

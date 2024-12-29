import base64
import io
import logging
from tempfile import NamedTemporaryFile
from typing import List, Union

import pyautogui
from PIL import Image

from . import Executor, logger


class WindowsExecutor(Executor):
    def __init__(self):
        super().__init__()
        self.screenshot_as_base64 = False
        self.screenshot_as_tempfile = False

    def move_mouse(self, x: int, y: int, observation: str) -> bool:
        try:
            logger.debug(f"move mouse x y {x} {y}")
            # pyautogui.moveTo expects (x, y), so keep the order consistent:
            pyautogui.moveTo(x, y, duration=1)
            return True
        except Exception as e:
            logger.exception("Error in move_mouse")
            return False

    def press_key(self, keys: List[str], observation: str) -> bool:
        try:
            logger.debug(f"press keys {keys}")
            # Convert all keys to lowercase for consistency
            pyautogui.hotkey(*[k.lower() for k in keys])
            return True
        except Exception as e:
            logger.exception("Error in press_key")
            return False

    def type_text(self, text: str, observation: str) -> bool:
        try:
            logger.debug(f"type text {text}")
            pyautogui.write(text)
            return True
        except Exception as e:
            logger.exception("Error in type_text")
            return False

    def click_mouse(self, observation: str, button: str = "left") -> bool:
        try:
            logger.debug(f"click mouse {button}")
            pyautogui.click(button=button)
            return True
        except Exception as e:
            logger.exception("Error in click_mouse")
            return False

    def double_click_mouse(self, button: str, observation: str) -> bool:
        try:
            logger.debug(f"doubleclick mouse {button}")
            pyautogui.doubleClick(button=button)
            return True
        except Exception as e:
            logger.exception("Error in double_click_mouse")
            return False

    def scroll(self, clicks: int, observation: str) -> bool:
        try:
            logger.debug(f"scroll {clicks}")
            pyautogui.scroll(clicks)
            return True
        except Exception as e:
            logger.exception("Error in scroll")
            return False

    def click_at_a_point(self, x: int, y: int, observation: str) -> bool:
        try:
            logger.debug(f"click at a point x y {x} {y}")
            # pyautogui.click expects (x, y)
            pyautogui.click(x=x, y=y, duration=1)
            return True
        except Exception as e:
            logger.exception("Error in click_at_a_point")
            return False

    def swipe_left(self, observation: str) -> bool:
        # You might implement a Windows-specific gesture or fallback to NotImplementedError
        raise NotImplementedError("Swipe left is not implemented on Windows")

    def swipe_right(self, observation: str) -> bool:
        raise NotImplementedError("Swipe right is not implemented on Windows")

    def swipe_up(self, observation: str) -> bool:
        raise NotImplementedError("Swipe up is not implemented on Windows")

    def swipe_down(self, observation: str) -> bool:
        raise NotImplementedError("Swipe down is not implemented on Windows")

    def volume_up(self, observation: str) -> bool:
        # You could implement Windows-specific logic for volume control here
        raise NotImplementedError("Volume up is not implemented on Windows")

    def volume_down(self, observation: str) -> bool:
        # You could implement Windows-specific logic for volume control here
        raise NotImplementedError("Volume down is not implemented on Windows")

    def navigate_back(self, observation: str) -> bool:
        # Windows-specific "go back" (like Alt+Left in some contexts)
        # or raise NotImplementedError if uncertain
        raise NotImplementedError("Navigate back is not implemented on Windows")

    def minimize_app(self, observation: str) -> bool:
        # Windows-specific logic to minimize the currently active window
        raise NotImplementedError("Minimize app is not implemented on Windows")

    def screenshot(
        self, observation: str, as_base64: bool = False, use_tempfile: bool = False
    ) -> Union[Image.Image, str, tuple]:
        """
        Takes a screenshot.

        Args:
            as_base64 (bool): Whether to return the screenshot as a base64-encoded string. Defaults to False.
            use_tempfile (bool): Whether to use a temporary file for storing the screenshot. Defaults to False.

        Returns:
            Union[Image.Image, str, tuple]: The screenshot as a PIL Image object, a base64-encoded string,
                                             or a tuple containing the PIL Image object and the file path if use_tempfile is True.
        """
        try:
            logger.debug(f"Take a screenshot use_tempfile={use_tempfile}")
            screenshot = pyautogui.screenshot()
            if use_tempfile or self.screenshot_as_tempfile:
                with NamedTemporaryFile(delete=False, suffix=".png") as temp_file:
                    screenshot.save(temp_file, format="PNG")
                    temp_file_path = temp_file.name
                return temp_file_path

            if as_base64 or self.screenshot_as_base64:
                buffered = io.BytesIO()
                screenshot.save(buffered, format="PNG")
                base64_str = base64.b64encode(buffered.getvalue()).decode("utf-8")
                return base64_str

            return screenshot
        except Exception as e:
            logger.exception("Error in screenshot")
            return "" if as_base64 or use_tempfile else None

    def apple_script(self, script: str, observation: str) -> bool:
        # AppleScript is specific to macOS, so we raise an error
        raise NotImplementedError("AppleScript is not supported on Windows")

import time
from pathlib import Path

from gameyamlspiderandgenerator.plugin.gcores import Gcores
from gameyamlspiderandgenerator.plugin.steam import Steam
from gameyamlspiderandgenerator.util.config import config
from gameyamlspiderandgenerator.util.fgi_yaml import get_valid_filename
from gameyamlspiderandgenerator.util.plugin_manager import pkg
from loguru import logger
import sys

logger.remove()
logger.add(sys.stdout, level="DEBUG")


def get_time(f):
    def inner(*arg, **kwarg):
        s_time = time.time()
        res = f(*arg, **kwarg)
        e_time = time.time()
        print(f"耗时：{e_time - s_time:.2f}秒")
        return res

    return inner


config.load(Path(__file__).parent / "config.yaml")
pkg.init()


@get_time
def test1():
    yml = Gcores("https://www.gcores.com/games/133528").to_yaml()
    print(yml)
    with open(get_valid_filename(yml.raw_dict["name"]) + ".zip", "wb") as f:
        f.write(bytes(yml))


@get_time
def test2():
    yml = Steam(
        "https://store.steampowered.com/app/1710540/Fall_of_Porcupine/"
    ).to_yaml()
    print(yml)
    with open(get_valid_filename(yml.raw_dict["name"]) + ".zip", "wb") as f:
        f.write(bytes(yml))


test1()
test2()
print(config)

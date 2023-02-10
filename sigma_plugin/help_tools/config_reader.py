import json
from pathlib import Path
from typing import Union


class ConfigWorker:

    def __init__(self, header: str):

        self.header = header

        self.config_file_path = Path(__file__).parents[1].joinpath("configs/config.json")
        self.config_styles_path = Path(__file__).parents[1].joinpath("configs/style_files/config_styles.json")

        self.config_file = self._get_config_file()
        self.styles_config_file = self._get_styles_config_file()

    def _get_config_file(self):
        with open(self.config_file_path, "r", encoding="UTF-8") as config_file:
            return json.load(config_file)

    def _get_styles_config_file(self):
        try:
            with open(self.config_styles_path, "r", encoding="utf-8") as styles_config_file:
                return json.load(styles_config_file)
        except json.JSONDecodeError:
            with open(self.config_styles_path, "r", encoding="utf-8-sig") as styles_config_file:
                return json.load(styles_config_file)

    @property
    def config_reader(self) -> dict:
        return self.config_file.get(self.header)

    @property
    def styles_config_reader(self) -> dict:
        return self.styles_config_file.get(self.header)

    @property
    def get_config_file(self) -> dict:
        return self.config_file

    def config_writer(self, change_field: str, new_value: Union[Path, dict, str]) -> None:
        if isinstance(new_value, dict):
            self.config_file[self.header][change_field] = new_value
        else:
            self.config_file[self.header][change_field] = str(new_value)
        with open(self.config_file_path, "w", encoding="UTF-8") as config_file:
            config_file.write(json.dumps(self.config_file, ensure_ascii=False))

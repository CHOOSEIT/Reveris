from typing import List
from story.story_modules import StoryModules


class StoryPart:
    def __init__(self, modules: List[StoryModules]):
        self._modules = modules

    def to_prompt_string(self) -> str:
        return "\n".join([module.to_prompt_string() for module in self._modules])

    def get_modules(self) -> List[StoryModules]:
        return self._modules

    def __getitem__(self, index):
        return self._modules[index]

    def __len__(self):
        return len(self._modules)

    def to_dict(self) -> dict:
        return [module.to_dict() for module in self._modules]

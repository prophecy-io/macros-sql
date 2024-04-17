from dataclasses import dataclass

from prophecy.cb.sql.MacroBuilderBase import *
from prophecy.cb.ui.uispec import *


class Deduplicate(MacroSpec):
    name: str = "Deduplicate"
    project: str = "https://github.com/dbt-labs/dbt-utils"

    @dataclass(frozen=True)
    class DeduplicateProperties(MacroProperties):
        macroName: str = ''
        projectName: str = ''
        parameters: list[MacroParameter] = field(default_factory=list)

    def dialog(self) -> Dialog:
        return Dialog("Macro") \
            .addElement(
            ColumnsLayout(gap="1rem", height="100%")
            .addColumn(
                Ports(allowInputAddOrDelete=True),
                "content"
            )
            .addColumn(
                MacroInstance(
                    "Macro Parameters",
                    name=self.name,
                    projectName=self.project.split('/')[-1]
                ).bindProperty("parameters").withSchemaSuggestions(),
                "5fr"
            )
        )

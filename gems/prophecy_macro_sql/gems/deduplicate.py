from prophecy.cb.sql import MacroBuilderBase
from prophecy.cb.ui.uispec import Dialog, ColumnsLayout, Ports, MacroInstance


class Deduplicate(MacroBuilderBase):
    name: str = "Deduplicate"
    project: str = "https://github.com/dbt-labs/dbt-utils"

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
                    name="Deduplicate",
                    projectName="dbt-utils"
                ).bindProperty("parameters").withSchemaSuggestions(),
                "5fr"
            )
        )

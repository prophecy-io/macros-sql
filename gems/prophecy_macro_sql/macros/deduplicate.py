from dataclasses import dataclass

from prophecy.cb.sql.MacroBuilderBase import *
from prophecy.cb.ui.uispec import *


class Deduplicate(MacroSpec):
    name: str = "Deduplicate"
    projectName: str = "dbt-utils"

    @dataclass(frozen=True)
    class DeduplicateProperties(MacroProperties):
        macroName: str = ''
        projectName: str = ''
        tableName: str = ''
        partitionBy: str = ''
        orderBy: str = ''

    def dialog(self) -> Dialog:
        return Dialog("Macro") \
            .addElement(
            ColumnsLayout(gap="1rem", height="100%")
            .addColumn(
                Ports(allowInputAddOrDelete=True),
                "content"
            )
            .addColumn(
                StackLayout()
                .addElement(
                    TextBox("Table Name")
                    .bindPlaceholder("Configure table name")
                    .bindProperty("tableName")
                )
                .addElement(
                    TextBox("Deduplicate Columns")
                    .bindPlaceholder("Select a column to deduplicate on")
                    .bindProperty("partitionBy")
                )
                .addElement(
                    TextBox("Rows to keep logic")
                    .bindPlaceholder("Select row on the basis of ordering a particular column")
                    .bindProperty("partitionBy")
                )
            )
        )

    def loadProperties(self, parameters: List[MacroParameter]) -> PropertiesType:
        parametersMap = self.convertToParameterMap(parameters)
        return Deduplicate.DeduplicateProperties(
            macroName=self.name,
            projectName=self.projectName,
            tableName=parametersMap.get('relation'),
            orderBy=parametersMap.get('partition_by'),
            partitionBy=parametersMap.get('order_by')
        )

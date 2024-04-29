from dataclasses import dataclass

from collections import defaultdict
from prophecy.cb.sql.MacroBuilderBase import *
from prophecy.cb.ui.uispec import *


class Deduplicate2(MacroSpec):
    name: str = "Deduplicate2"
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

    def validate(self, context: SqlContext, component: Component) -> List[Diagnostic]:
        diagnostics = []
        macroProjectMap: Dict[str, list[MacroDefFromSqlSource]] = self.getMacroMap(context)
        projectName = self.projectName if self.projectName != "" else context.projectName
        if projectName not in macroProjectMap:
            diagnostics.append(Diagnostic(
                "properties.projectName",
                f"Project name {self.projectName} doesn't exist. Current Project is ${context.projectName}",
                SeverityLevelEnum.Error
            ))
        else:
            macroDef: Optional[MacroDefFromSqlSource] = self.getMacro(self.name, projectName,
                                                                      context)
            if macroDef is None:
                diagnostics.append(Diagnostic(
                    "properties.macroName",
                    f"Macro {self.name} doesn't exist",
                    SeverityLevelEnum.Error
                ))
            else:
                if component.properties.tableName == '':
                    diagnostics.append(
                        Diagnostic(
                            f"properties.tableName",
                            f"Please define table name",
                            SeverityLevelEnum.Error
                        )
                    )
                if component.properties.partitionBy == '':
                    diagnostics.append(
                        Diagnostic(
                            f"properties.partitionBy",
                            f"Please define partition by column",
                            SeverityLevelEnum.Error
                        )
                    )
                if component.properties.orderBy == '':
                    diagnostics.append(
                        Diagnostic(
                            f"properties.orderBy",
                            f"Please define order by by column",
                            SeverityLevelEnum.Error
                        )
                    )
        return diagnostics

    def onChange(self, context: SqlContext, oldState: Component, newState: Component) -> Component:
        return newState

    def apply(self, props: DeduplicateProperties) -> str:
        if props.projectName != "":
            resolved_macro_name = f"{props.projectName}.{self.name}"
        else:
            resolved_macro_name = self.name
        return f'{{{{ {resolved_macro_name}({props.tableName}, {props.partitionBy}, {props.orderBy}) }}}}'

    def loadProperties(self, parameters: List[MacroParameter]) -> PropertiesType:
        parametersMap = self.convertToParameterMap(parameters)
        return Deduplicate2.DeduplicateProperties(
            macroName=self.name,
            projectName='',
            tableName=parametersMap.get('relation'),
            orderBy=parametersMap.get('partition_by'),
            partitionBy=parametersMap.get('order_by')
        )

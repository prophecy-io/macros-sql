from dataclasses import dataclass

from prophecy.cb.sql.MacroBuilderBase import *
from prophecy.cb.ui.uispec import *


class Deduplicate2(MacroSpec):
    name: str = "Deduplicate2"

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

    def validate(self, context: SqlContext, component: Component) -> List[Diagnostic]:
        diagnostics = []
        if component.properties.macroName == "":
            diagnostics.append(Diagnostic(
                "properties.macroName",
                "Macro name cannot be empty",
                SeverityLevelEnum.Error
            ))
        else:
            macroProjectMap: Dict[str, list[MacroDefFromSqlSource]] = self.getMacroMap(context)
            projectName = component.properties.projectName if component.properties.projectName != "" else context.projectName
            if projectName not in macroProjectMap:
                diagnostics.append(Diagnostic(
                    "properties.projectName",
                    f"Project name {component.properties.projectName} doesn't exist. Current Project is ${context.projectName}",
                    SeverityLevelEnum.Error
                ))
            else:
                macroDef: Optional[MacroDefFromSqlSource] = self.getMacro(component.properties.macroName, projectName,
                                                                          context)
                if macroDef is None:
                    diagnostics.append(Diagnostic(
                        "properties.macroName",
                        f"Macro {component.properties.macroName} doesn't exist",
                        SeverityLevelEnum.Error
                    ))
                else:
                    if macroDef.macroType == DBTMacroType.Expression:
                        diagnostics.append(Diagnostic(
                            "properties.macroName",
                            f"Macro {component.properties.macroName} is an Expression Macro. Cannot be used as a Gem.",
                            SeverityLevelEnum.Error
                        ))
                    else:
                        paramsUserSelected = {parameter.name for parameter in component.properties.parameters}
                        for idx, argumentDef in enumerate(macroDef.parameters):
                            if argumentDef.name not in paramsUserSelected and argumentDef.defaultValue != "":
                                diagnostics.append(Diagnostic(
                                    f"properties.parameters[{idx}].value",
                                    f"Parameter {argumentDef.name} must not be empty. As it doesn't contain a default value.",
                                    SeverityLevelEnum.Error
                                )
                                )
                # TODO WIP: Jinja validation

        return diagnostics

    def onChange(self, context: SqlContext, oldState: Component, newState: Component) -> Component:
        projectName = newState.properties.projectName if newState.properties.projectName != "" else context.projectName
        macroDef: Optional[MacroDefFromSqlSource] = self.getMacro(newState.properties.macroName, projectName, context)
        macroArgs = macroDef.parameters if macroDef is not None else []

        if oldState.properties.macroName != newState.properties.macroName or len(oldState.ports.inputs) != len(
                newState.ports.inputs):
            parameters = self.updateParamValuesWithSlugs(processedParams=[],
                                                         availableSlugs=[x.slug for x in newState.ports.inputs],
                                                         remainingMacroArgs=macroArgs)
        else:
            parameters = newState.properties.parameters

        # TODO WIP Jinja validation and populate used macros

        return newState.bindProperties(replace(newState.properties, parameters=parameters))

    def apply(self, props: DeduplicateProperties) -> str:
        non_empty_params = list(filter(lambda parameter: parameter.value != "", props.parameters))
        if len(non_empty_params) == 1 and non_empty_params[0].name == "relation":
            macro_name = "deduplicate_simple"
        else:
            macro_name = props.macroName
        arguments = ','.join([f"{parameter.name} = {parameter.value}" for parameter in non_empty_params])
        if props.projectName != "":
            resolved_macro_name = f"{props.projectName}.{macro_name}"
        else:
            resolved_macro_name = macro_name
        return f'{{{{ {resolved_macro_name}({arguments}) }}}}'

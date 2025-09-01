import adsk.core
import adsk.fusion
import adsk.cam
import traceback
import os

# Global list to keep all event handlers in scope.
handlers = []


def run(context: dict) -> None:
    """Called when the add-in is run."""
    try:
        app: adsk.core.Application = adsk.core.Application.get()
        ui: adsk.core.UserInterface = app.userInterface

        # Create a command definition for the Section Flipper
        cmdDef: adsk.core.CommandDefinition = ui.commandDefinitions.addButtonDefinition(
            'SectionFlipperCmd',
            'Flip Section View',
            'Flips visible section view in the active design',
            get_icon_path()
        )

        # Connect to the command created event
        onCommandCreated = SectionFlipperCommandCreatedHandler()
        cmdDef.commandCreated.add(onCommandCreated)
        handlers.append(onCommandCreated)

        # Add the command to the ADD-INS panel in Tools tab
        addInsPanel: adsk.core.ToolbarPanel = ui.allToolbarPanels.itemById('SolidScriptsAddinsPanel')
        if addInsPanel:
            cmdControl: adsk.core.CommandControl = addInsPanel.controls.addCommand(cmdDef)
            cmdControl.isVisible = True

    except Exception:
        ui: adsk.core.UserInterface = adsk.core.Application.get().userInterface
        ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))


def stop(context: dict) -> None:
    """Called when the add-in is stopped."""
    try:
        app: adsk.core.Application = adsk.core.Application.get()
        ui: adsk.core.UserInterface = app.userInterface

        # Clean up the UI
        addInsPanel: adsk.core.ToolbarPanel = ui.allToolbarPanels.itemById('SolidScriptsAddinsPanel')
        if addInsPanel:
            cmdControl: adsk.core.CommandControl = addInsPanel.controls.itemById('SectionFlipperCmd')
            if cmdControl:
                cmdControl.deleteMe()

        # Remove command definition
        cmdDef: adsk.core.CommandDefinition = ui.commandDefinitions.itemById('SectionFlipperCmd')
        if cmdDef:
            cmdDef.deleteMe()

    except Exception:
        ui: adsk.core.UserInterface = adsk.core.Application.get().userInterface
        ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))


def get_icon_path() -> str:
    """Returns the path to the add-in icon."""
    return os.path.join(os.path.dirname(__file__), 'resources')


class SectionFlipperCommandCreatedHandler(adsk.core.CommandCreatedEventHandler):
    """Event handler for the command created event."""
    
    def __init__(self) -> None:
        super().__init__()

    def notify(self, args: adsk.core.CommandCreatedEventArgs) -> None:
        """Called when the command is created."""
        try:
            cmd: adsk.core.Command = args.command

            # Connect to the execute event
            onExecute = SectionFlipperCommandExecuteHandler()
            cmd.execute.add(onExecute)
            handlers.append(onExecute)

        except Exception:
            ui: adsk.core.UserInterface = adsk.core.Application.get().userInterface
            ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))


class SectionFlipperCommandExecuteHandler(adsk.core.CommandEventHandler):
    """Event handler for the command execute event."""
    
    def __init__(self) -> None:
        super().__init__()

    def notify(self, args: adsk.core.CommandEventArgs) -> None:
        """Called when the command is executed."""
        try:
            flip_visible_section_view()

        except Exception:
            ui: adsk.core.UserInterface = adsk.core.Application.get().userInterface
            ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))


def flip_visible_section_view() -> None:
    """Flips all currently visible section analyses in the active design."""
    try:
        app: adsk.core.Application = adsk.core.Application.get()
        ui: adsk.core.UserInterface = app.userInterface
        
        # Check if there's an active document
        if not app.activeDocument:
            ui.messageBox('No active document found.')
            return
        
        design: adsk.fusion.Design = app.activeDocument.design
        if not design:
            ui.messageBox('No design found in active document.')
            return
        
        sectionAnalyses: adsk.fusion.SectionAnalyses = design.analyses.sectionAnalyses
        
        if sectionAnalyses.count == 0:
            ui.messageBox('No section analyses found in the design.')
            return
        
        flipped_count: int = 0
        total_visible: int = 0
        
        for i in range(sectionAnalyses.count):
            section: adsk.fusion.SectionAnalysis = sectionAnalyses.item(i)
            if section.isLightBulbOn:
                total_visible += 1
                section.flip()
                flipped_count += 1
        
        if total_visible == 0:
            ui.messageBox('No visible section analyses found.')

    except Exception as e:
        ui: adsk.core.UserInterface = adsk.core.Application.get().userInterface
        ui.messageBox(f'Error flipping section view:\n{str(e)}\n\n{traceback.format_exc()}')
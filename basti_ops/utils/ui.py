import bpy


def set_status_text(content: list[tuple[str, str]]) -> None:
    """Set a list of icons and labels as the status bar text"""

    def draw(self, context):
        layout = self.layout
        for element in content:
            layout.label(text=element[1], icon=element[0])

    bpy.context.workspace.status_text_set(draw)


def clear_status_text():
    """Clear the status bar text"""
    bpy.context.workspace.status_text_set(None)

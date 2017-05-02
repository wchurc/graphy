try:
    from graphy.pygame_viewer import PygameViewer as Viewer
except ImportError:
    from graphy.turtle_viewer import TurtleViewer as Viewer
    print("Install Pygame for much better performance!")

try:
    from fdag import fdag, config
except ImportError:
    fdag = None
    config = None
    print("Failed to import fdag. C-extensions are disabled")
else:
    fdag_imported = True

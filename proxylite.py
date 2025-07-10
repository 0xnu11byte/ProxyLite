from proxylite.gui import launch_gui
import traceback

if __name__ == "__main__":
    try:
        launch_gui()
    except Exception as e:
        print("An error occurred during startup:")
        traceback.print_exc()
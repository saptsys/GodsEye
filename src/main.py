from app import App
from pathlib import Path



def main():
    path = "./data/img/car2.jpg"
    # path = str(Path(__file__).parent.parent / "data/video/plate.mp4")
    app = App(path)
    app.run()

if __name__ == "__main__":
    main()
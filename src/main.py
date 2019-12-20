from app import App
from pathlib import Path



def main():
    path = "../data/video/traffic2.mp4"
    # path = str(Path(__file__).parent.parent / "data/video/traffic.mp4")
    app = App(path)

if __name__ == "__main__":
    main()
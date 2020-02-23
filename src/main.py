from app import App
from pathlib import Path
import settings as settings



def main():
    sets = settings.Settings()
    # path = str(Path(__file__).parent.parent / "data/video/plate.mp4")
    app = App(sets)
    app.run()

if __name__ == "__main__":
    # try:
    main()
    # except BaseException as e:
        # print('An exception occurred: {}'.format(e))
        # pass

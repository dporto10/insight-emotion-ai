import glob
from app.analysis.pipeline import processar_video

def main():

    videos = glob.glob("*.mp4")

    if not videos:
        print("Nenhum vídeo encontrado")
        return

    video = videos[0]

    print("Vídeo encontrado:", video)

    processar_video(video)


if __name__ == "__main__":
    main()

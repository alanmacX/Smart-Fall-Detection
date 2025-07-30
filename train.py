from ultralytics import YOLO

def main():
    model = YOLO('best.pt')

    model.train(
        data='data.yaml',
        epochs=100,
        mosaic=0,
        batch=8,
        device=0,
        name='yolov8n_custom'
    )

if __name__ == '__main__':
    main()

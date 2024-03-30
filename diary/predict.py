import base64
import logging
from io import BytesIO

import torch
import torch.nn as nn
from PIL import Image
from torchvision import transforms
from torchvision.models import resnet18

logger = logging.getLogger(__name__)

# 画像の前処理を定義
transform = transforms.Compose([
    transforms.Resize(256),
    transforms.CenterCrop(224),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
])


def load_model(model_path):
    model = resnet18(pretrained=False)
    num_features = model.fc.in_features
    model.fc = nn.Linear(num_features, 2)
    model.load_state_dict(torch.load(model_path, map_location=torch.device('cpu')))
    model.eval()
    return model


def predict(model, base64_image):
    try:
        logger.debug("Decoding base64 image")
        # Base64エンコードされた文字列をバイトデータにデコードする
        if base64_image.startswith('data:image/jpeg;base64,'):
            base64_image = base64_image.replace('data:image/jpeg;base64,', '')
        elif base64_image.startswith('data:image/png;base64,'):
            base64_image = base64_image.replace('data:image/png;base64,', '')

        image_bytes = base64.b64decode(base64_image)

        logger.debug("Loading image")
        # バイトデータから画像を読み込む
        image = Image.open(BytesIO(image_bytes))
        image = image.convert('RGB')

        # 画像の前処理を適用
        logger.debug("Applying transformations")
        image = transform(image).unsqueeze(0)

        # 推論を実行
        logger.debug("Performing inference")
        with torch.no_grad():
            outputs = model(image)

        _, predicted = torch.max(outputs, 1)
        prediction = predicted.item()
        logger.debug(f"Predicted: {prediction}")

        # 推論結果に基づいてメッセージを返す
        if prediction == 0:
            return "ダークチョコレートです"
        elif prediction == 1:
            return "ミルクチョコレートです"
        else:
            return "不明な結果です"
    except Exception as e:
        logger.error(f"Error in prediction: {e}")
        return "推論エラーが発生しました"


# モデルのパスを指定
model_path = 'ml_model/model.pth'
model = load_model(model_path)

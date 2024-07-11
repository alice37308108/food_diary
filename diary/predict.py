import base64
import io
import logging
from io import BytesIO

import torch
import torch.nn as nn
import torch.nn.functional as F
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
    """
    モデルをロードする関数
    resnet18モデルの最終層を2クラス分類用に変更

    :param model_path: モデルのパス
    :return: ロードしたモデル
    """
    model = resnet18(pretrained=False)
    num_features = model.fc.in_features
    model.fc = nn.Linear(num_features, 2)
    model.load_state_dict(torch.load(model_path, map_location=torch.device('cpu')))
    model.eval()
    return model


def predict(model, base64_image, labels):
    """
    画像の推論を行う関数

    :param model: 推論に使用するモデル
    :param base64_image: Base64エンコードされた画像データ（JPEGまたはPNG形式の画像を想定）
    :param labels: モデルが分類するクラスラベルのリスト
    :return: 推論結果のラベル名またはエラーメッセージを含む文字列
    """
    try:
        # Base64エンコードされた画像データをデコード
        if base64_image.startswith('data:image/jpeg;base64,'):
            base64_image = base64_image.replace('data:image/jpeg;base64,', '')
        elif base64_image.startswith('data:image/png;base64,'):
            base64_image = base64_image.replace('data:image/png;base64,', '')

        image_bytes = base64.b64decode(base64_image)
        image = Image.open(BytesIO(image_bytes))
        image = image.convert('RGB')

        # 画像を前処理
        image = transform(image).unsqueeze(0)

        # 推論
        with torch.no_grad():
            outputs = model(image)

        _, predicted = torch.max(outputs, 1)
        prediction = predicted.item()
        logger.debug(f'Predicted: {prediction}')

        if prediction < len(labels):
            return f'{labels[prediction]}です'
        else:
            return '不明な結果です'
    except Exception as e:
        logger.error(f'Error in prediction: {e}')
        return '推論エラーが発生しました'


def predict_kinoko_takenoko(model, base64_image):
    """
    きのことたけのこの推論を行う関数

    :param model: 推論に使用するモデル
    :param base64_image: Base64エンコードされた画像データ（JPEGまたはPNG形式の画像）
    :return: きのこ度とたけのこ度を含む辞書、またはエラーメッセージを含む文字列
    """
    try:
        # Base64エンコードされた画像データをデコード
        if base64_image.startswith('data:image/jpeg;base64,'):
            base64_image = base64_image.replace('data:image/jpeg;base64,', '')
        elif base64_image.startswith('data:image/png;base64,'):
            base64_image = base64_image.replace('data:image/png;base64,', '')

        image_data = base64.b64decode(base64_image)

        # 画像を開いてRGBに変換
        image = Image.open(io.BytesIO(image_data)).convert('RGB')

        # 画像を前処理
        image = transform(image).unsqueeze(0)

        # 推論
        with torch.no_grad():
            outputs = model(image)
            probabilities = F.softmax(outputs, dim=1)
            kinoko_prob = probabilities[0][0].item() * 100
            takenoko_prob = probabilities[0][1].item() * 100

        return {
            'きのこ度': f'{kinoko_prob:.2f}',
            'たけのこ度': f'{takenoko_prob:.2f}'
        }
    except Exception as e:
        logger.error(f'Error in prediction: {e}')
        return '推論エラーが発生しました'


# モデルのパスを指定
chocolate_model_path = 'ml_model/model.pth'
kinoko_model_path = 'ml_model/model_kinoko.pth'

# モデルをロード
chocolate_model = load_model(chocolate_model_path)
kinoko_model = load_model(kinoko_model_path)

# ラベルを定義
chocolate_labels = ["ダークチョコレート", "ミルクチョコレート"]
kinoko_labels = ["きのこ", "たけのこ"]


def predict_chocolate(base64_image):
    """
    チョコレートの種類を推論する関数

    :param base64_image: Base64エンコードされた画像データ（JPEGまたはPNG形式の画像）
    :return: 推論結果のラベル名またはエラーメッセージを含む文字列
    """
    return predict(chocolate_model, base64_image, chocolate_labels)


def predict_kinoko(base64_image):
    """
    きのことたけのこの分類を推論する関数。

    :param base64_image: Base64エンコードされた画像データ（JPEGまたはPNG形式の画像）
    :return: 推論結果のラベル名またはエラーメッセージを含む文字列
    """
    return predict(kinoko_model, base64_image, kinoko_labels)


def predict_kino_take(base64_image):
    """
    きのことたけのこの度数を推論する関数

    :param base64_image: Base64エンコードされた画像データ（JPEGまたはPNG形式の画像）
    :return: きのこ度とたけのこ度を含む辞書、またはエラーメッセージを含む文字列
    """
    return predict_kinoko_takenoko(kinoko_model, base64_image)

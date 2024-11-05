from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from transformers import TrOCRProcessor, VisionEncoderDecoderModel
from PIL import Image
import torch
import base64
from io import BytesIO
import json


# 初始化模型和處理器
processor = TrOCRProcessor.from_pretrained('microsoft/trocr-base-handwritten')
model = VisionEncoderDecoderModel.from_pretrained('microsoft/trocr-base-handwritten')
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model.to(device)

# 定義替換字典
replace_dict = {
    "o": "0", "O": "0", "z": "2", "Z": "2", "i": "1",
    "l": "1", "B": "8", "S": "5", "s": "5", "t": "5",
    "g": "9", "q": "9", "p": "9", "P": "9",
}

@csrf_exempt  # 如開發環境測試用，可在正式環境使用適當 CSRF 保護
def extract_text_from_image(request):
    if request.method == 'POST':
        # 獲取圖片和座標資料
        image_file = request.FILES.get('image')
        coordinates = json.loads(request.POST.get('coordinates', '[0, 0, 0, 0]'))
        
        result = []
        for coord in coordinates:

            # 讀取和裁剪圖片
            image = Image.open(image_file).convert("RGB")
            cropped_image = image.crop(coord)
            
            # 預處理圖片並轉換成張量
            pixel_values = processor(images=cropped_image, return_tensors="pt").pixel_values.to(device)
            
            # 生成文字
            generated_ids = model.generate(pixel_values, max_length=20)
            generated_texts = processor.batch_decode(generated_ids, skip_special_tokens=True)[0].replace(" ", "").replace(".", "")
            
            # 替換非數字字母為相應的數字
            for i in generated_texts:
                if i in replace_dict:
                    generated_texts = generated_texts.replace(i, replace_dict[i])

            # 將裁剪後的圖片轉換成 base64 編碼格式
            buffered = BytesIO()
            cropped_image.save(buffered, format="JPEG")
            encoded_image = base64.b64encode(buffered.getvalue()).decode('utf-8')

            result.append({
                    "text": generated_texts,
                    "image": encoded_image
                })
                
        # 回傳 JSON 格式結果
        return JsonResponse(result, safe=False)
    else:
        return JsonResponse({"error": "Only POST requests are allowed."}, status=405)
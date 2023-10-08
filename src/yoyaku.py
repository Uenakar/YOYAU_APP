from transformers import AutoModelForSeq2SeqLM, AutoTokenizer, T5Config, T5ForConditionalGeneration
import torch

import os


# スクリプトのあるディレクトリを取得
script_dir = os.path.dirname(os.path.abspath(__file__))

# model_weights.pth ファイルへの絶対パスを組み立て
model_weights_path = os.path.join(script_dir, "model_weights.pth")


class YoyakuModel:
    def __init__(self, model_weights_path):
        # トークナイザーの初期化
        self.tokenizer = AutoTokenizer.from_pretrained('sonoisa/t5-base-japanese')
        
        # T5のモデルのインスタンスを作成
        config = T5Config.from_pretrained('sonoisa/t5-base-japanese')
        self.model = T5ForConditionalGeneration(config)
        
         #ファイルが存在しない場合、gdownを使用してダウンロード DockerfileにモデルをDLするコマンドを追加する為不要
        #if not os.path.exists(model_weights_path):
            #import gdown
            #url = 'https://drive.google.com/uc?id=18Kh3mCkNeUVG1Y1mcjobcq6FHqMwcL_e'
            #gdown.download(url, model_weights_path, quiet=False)
        # 重みをロード
        state_dict = torch.load(model_weights_path)
        self.model.load_state_dict(state_dict)

    def summarize(self, text: str, max_input_length: int = 512, max_output_length: int = 150) -> str:
        self.model.eval()
        inputs = self.tokenizer.encode(text, return_tensors="pt", max_length=max_input_length, truncation=True)
        with torch.no_grad():
            summary_ids = self.model.generate(inputs, max_length=max_output_length)
        return self.tokenizer.decode(summary_ids[0], skip_special_tokens=True)

if __name__ == "__main__":
    #model_weights_path = "./src/model_weights.pth"
    #model_weights_path = "C:\\Users\\user\\Desktop\\yoyaku_app\\src\\model_weights.pth"
    yoyaku = YoyakuModel(model_weights_path)
    text = "ここに要約したいテキストを入力"
    print(yoyaku.summarize(text))

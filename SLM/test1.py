import torch
from transformers import AutoModelForSequenceClassification, AutoTokenizer, Trainer, TrainingArguments
from datasets import load_dataset
from sklearn.metrics import accuracy_score, precision_recall_fscore_support
import time

def compute_metrics(pred):
    labels = pred.label_ids
    preds = pred.predictions.argmax(-1)
    precision, recall, f1, _ = precision_recall_fscore_support(labels, preds, average='binary')
    acc = accuracy_score(labels, preds)
    return {
        'accuracy': acc,
        'f1': f1,
        'precision': precision,
        'recall': recall
    }

def evaluate_model(model_name):
    # 데이터 로드
    dataset = load_dataset("glue", "sst2")
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    
    def tokenize_function(examples):
        return tokenizer(examples["sentence"], padding="max_length", truncation=True)

    tokenized_datasets = dataset.map(tokenize_function, batched=True)

    # 모델 로드
    model = AutoModelForSequenceClassification.from_pretrained(model_name, num_labels=2)
    
    # 학습 인자 설정
    training_args = TrainingArguments(
        output_dir="./results",
        num_train_epochs=3,
        per_device_train_batch_size=16,
        per_device_eval_batch_size=64,
        warmup_steps=500,
        weight_decay=0.01,
        logging_dir='./logs',
    )

    # 트레이너 초기화
    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=tokenized_datasets["train"],
        eval_dataset=tokenized_datasets["validation"],
        compute_metrics=compute_metrics,
    )

    # 평가
    start_time = time.time()
    results = trainer.evaluate()
    end_time = time.time()

    # 모델 크기 계산
    model_size = sum(p.numel() for p in model.parameters())

    return {
        "model_name": model_name,
        "accuracy": results["eval_accuracy"],
        "f1": results["eval_f1"],
        "model_size": model_size,
        "inference_time": end_time - start_time
    }

# 평가할 모델 리스트
models = [
    "distilbert-base-uncased",
    "albert-base-v2",
    "prajjwal1/bert-tiny",  # TinyBERT
    "google/mobilebert-uncased",
    "google/electra-small-discriminator"
]

# 모든 모델 평가
results = []
for model_name in models:
    print(f"Evaluating {model_name}...")
    result = evaluate_model(model_name)
    results.append(result)

# 결과 출력
for result in results:
    print(f"\nModel: {result['model_name']}")
    print(f"Accuracy: {result['accuracy']:.4f}")
    print(f"F1 Score: {result['f1']:.4f}")
    print(f"Model Size: {result['model_size']:,} parameters")
    print(f"Inference Time: {result['inference_time']:.2f} seconds")
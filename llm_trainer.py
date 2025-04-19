# llm_trainer.py
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM, Seq2SeqTrainer, Seq2SeqTrainingArguments, DataCollatorForSeq2Seq
from datasets import load_dataset, Dataset
import json
import os

def load_jsonl_dataset(path):
    with open(path, "r", encoding="utf-8") as f:
        lines = [json.loads(l) for l in f if l.strip()]
    return Dataset.from_list(lines)

def prepare_model(model_name="google/flan-t5-base"):
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForSeq2SeqLM.from_pretrained(model_name)
    return tokenizer, model

def tokenize(example, tokenizer, max_input=512, max_output=128):
    model_input = tokenizer(example["input"], truncation=True, padding="max_length", max_length=max_input)
    label = tokenizer(example["output"], truncation=True, padding="max_length", max_length=max_output)
    model_input["labels"] = label["input_ids"]
    return model_input

def train_model(dataset_path="data/synthetic/train_synthetic.jsonl", output_dir="model/fine-tuned-flan"):
    tokenizer, model = prepare_model()
    dataset = load_jsonl_dataset(dataset_path)
    tokenized = dataset.map(lambda e: tokenize(e, tokenizer), batched=True)

    args = Seq2SeqTrainingArguments(
        output_dir=output_dir,
        per_device_train_batch_size=8,
        learning_rate=5e-5,
        num_train_epochs=3,
        save_total_limit=2,
        evaluation_strategy="no",
        logging_dir=f"{output_dir}/logs",
        save_strategy="epoch",
        fp16=True if torch.cuda.is_available() else False
    )

    trainer = Seq2SeqTrainer(
        model=model,
        args=args,
        train_dataset=tokenized,
        tokenizer=tokenizer,
        data_collator=DataCollatorForSeq2Seq(tokenizer, model)
    )

    trainer.train()
    model.save_pretrained(output_dir)
    tokenizer.save_pretrained(output_dir)
    print(f"✅ Model fine-tuned and saved to {output_dir}")

if __name__ == '__main__':
    train_model()

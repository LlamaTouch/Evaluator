from sentence_transformers import SentenceTransformer, util


def compute_sentence_similiarity(sentence1: str, sentence2: str) -> float:
    model = SentenceTransformer(
        model_name_or_path="all-MiniLM-L6-v2",
        device="cpu",
    )

    sentence_embedding1 = model.encode(sentence1, convert_to_tensor=True)
    sentence_embedding2 = model.encode(sentence2, convert_to_tensor=True)

    similarity = util.pytorch_cos_sim(sentence_embedding1, sentence_embedding2)[0][0]

    return similarity


def check_sentence_similarity(sentence1: str, sentence2: str, threshold: float = 0.8):
    similarity = compute_sentence_similiarity(sentence1, sentence2)
    return similarity, similarity > threshold

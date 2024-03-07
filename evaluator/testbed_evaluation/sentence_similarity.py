from sentence_transformers import SentenceTransformer, util
import logging


def compute_sentence_similiarity(sentence1, sentence2):
    """
    计算两个句子的相似度
    """
    # 加载模型
    model = SentenceTransformer(
        "/data/jxq/mobile-agent/comparison_algorithm/all-MiniLM-L6-v2"
    )

    # 计算句子的向量
    sentence_embedding1 = model.encode(sentence1, convert_to_tensor=True)
    sentence_embedding2 = model.encode(sentence2, convert_to_tensor=True)

    # 计算两个向量之间的余弦相似度
    similarity = util.pytorch_cos_sim(sentence_embedding1, sentence_embedding2)[0][0]

    return similarity


def check_sentence_similarity(sentence1, sentence2, threshold=0.8):
    """
    检查两个句子是否相似
    """
    logging.info(f"sentence similarity threshold: {threshold}")
    similarity = compute_sentence_similiarity(sentence1, sentence2)
    return similarity, similarity > threshold


if __name__ == "__main__":
    # 输入两个句子
    sentence1 = "What's the weather like in Singapore?"
    sentence2 = "weather like in Singapore?"

    # 计算相似度
    similarity, is_similar = check_sentence_similarity(sentence1, sentence2)

    print(f"Similarity: {similarity}")
    print(
        "The sentences are semantically " + ("similar" if is_similar else "not similar")
    )
